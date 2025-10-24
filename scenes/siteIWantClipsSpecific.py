import re
import datetime
import string
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteIWantClipsSpecificSpider(BaseSceneScraper):
    name = 'IWantClipsSpecific'
    network = 'I Want Clips'

    start_urls = [
        'https://iwantclips.com',
    ]

    cookies = {'accepted': '1', 'member_id': '0'}

    selector_map = {
        'external_id': '(\\d+)$',
        'pagination': '/?page=%s'
    }

    def get_next_page_url(self, base, page):
        return f"https://iwantclips.com/store/697092/Marceline-Leigh?page={page}"

    def start_requests(self):
        page = int(self.page) - 1

        for link in self.start_urls:
            link = self.get_next_page_url(link, page + 1)
            meta = {}
            meta['storeid'] = re.search(r'store/(\d+)/', link).group(1)
            meta['page'] = page
            meta['url'] = link
            yield scrapy.Request(link, callback=self.parse_token, meta=meta, cookies=self.cookies)

    def parse_token(self, response):
        meta = response.meta
        token_script = response.xpath('//script[contains(text(), "let typesenseClient") and contains(text(), "apiKey")]/text()').get()
        meta['token'] = re.search(r"\'apiKey\'.*?\'(.*?)\'", token_script).group(1)
        meta['host'] = re.search(r'host: \'(.*?)\'', token_script).group(1)
        return self.call_algolia(response.meta['page'], meta)

    def parse(self, response, **kwargs):
        meta = response.meta
        if response.status == 200:
            scenes = self.get_scenes(response)
            count = 0
            for scene in scenes:
                count += 1
                yield scene

            if count:
                if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                    meta['page'] = meta['page'] + 1
                    yield self.call_algolia(meta['page'], meta)

    def get_scenes(self, response):
        # ~ print(response.json())
        for scene in response.json()['results'][0]['hits']:
            scene = scene['document']
            item = SceneItem()
            item['image'] = scene['thumbnail_url']
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            if 'preview_mp4_url' in scene:
                item['trailer'] = scene['preview_mp4_url']
                if "https" not in item['trailer'].lower():
                    item['trailer'] = None
            else:
                item['trailer'] = None
            item['id'] = scene['content_id']
            item['title'] = string.capwords(scene['title'])
            item['description'] = scene['description']

            if scene['publish_date']:
                item['date'] = datetime.datetime.utcfromtimestamp(scene['publish_date']).isoformat()
                # ~ print(f"Datetime: {scene['publish_date']}     Parsed_date: {item['date']}")
            else:
                print("Date not provided, using today")
                item['date'] = self.parse_date('today').isoformat()
            item['performers'] = [scene['model_username']]
            if " and " in scene['model_username'].lower():
                item['performers'] = scene['model_username'].lower().split(" and ")
            if " & " in scene['model_username'].lower():
                item['performers'] = scene['model_username'].lower().split(" & ")

            item['performers'] = list(map(lambda x: string.capwords(x.strip()), item['performers']))

            if len(item['performers']) > 1:
                item['performers'] = [f"{performer} ({scene['member_id']})" for performer in item['performers']]

            item['tags'] = scene['categories'] + scene['keywords']
            item['tags'] = [i for i in item['tags'] if i]

            item['site'] = "I Want Clips: Marceline Leigh"
            item['parent'] = "I Want Clips"
            item['network'] = "I Want Clips"
            item['url'] = scene['content_url']

            yield self.check_item(item, self.days)

    def call_algolia(self, page, meta):
        token = meta['token']
        host = meta['host']
        referrer = meta['url']
        # ~ print (f'Page: {page}        Token: {token}     Referrer: {referrer}')
        algolia_url = f"https://{host}/multi_search?x-typesense-api-key={token}"
        headers = {
            'Content-Type': 'application/json',
            'Referer': self.get_next_page_url(referrer, page)
        }

        jbody = '{"searches":[{"sort_by":"publish_time:desc,popularity:desc","query_by":"title,description,member_id,model_username,categories,price_range,nudity,keywords,viewable_by,aa_ai,aa_body-shape,aa_body-type,aa_breast-size,aa_butt-size,aa_butt-type,aa_eye-color,aa_foot-size,aa_glasses,aa_hair-color,aa_hair-length,aa_height,aa_piercings,aa_pubic-hair,aa_tattoos,aa_origin-country,aa_race,aa_age,aa_circumcised,aa_endowment,aa_ethnicity,aa_girth,aa_language,aa_nose,aa_qwe,aa_wake,aa_wake-attributes,aa_abs","highlight_full_fields":"title,description,member_id,model_username,categories,price_range,nudity,keywords,viewable_by,aa_ai,aa_body-shape,aa_body-type,aa_breast-size,aa_butt-size,aa_butt-type,aa_eye-color,aa_foot-size,aa_glasses,aa_hair-color,aa_hair-length,aa_height,aa_piercings,aa_pubic-hair,aa_tattoos,aa_origin-country,aa_race,aa_age,aa_circumcised,aa_endowment,aa_ethnicity,aa_girth,aa_language,aa_nose,aa_qwe,aa_wake,aa_wake-attributes,aa_abs","collection":"prod_content","q":"*","facet_by":"type,categories,type,categories","filter_by":"member_id:' + meta['storeid'] + '","max_facet_values":1000,"page":' + str(page) + ',"per_page":25}]}'

        return scrapy.Request(
            url=algolia_url,
            method='post',
            body=jbody,
            meta=meta,
            callback=self.parse,
            headers=headers
        )
