import re
import datetime
import string
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteIWantClipsSpider(BaseSceneScraper):
    name = 'IWantClips'
    network = 'I Want Clips'

    start_urls = [
        'https://iwantclips.com',
    ]

    cookies = {'accepted': '1', 'member_id': '0'}

    selector_map = {
        'external_id': '(\\d+)$',
        'pagination': '/?page=%s'
    }

    def start_requests(self):
        if not hasattr(self, 'start_urls'):
            raise AttributeError('start_urls missing')

        if not self.start_urls:
            raise AttributeError('start_urls selector missing')
        page = int(self.page) - 1

        if self.limit_pages == 1:
            self.limit_pages = 50

        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, page + 1), callback=self.parse_token, meta={'page': page, 'url': link}, cookies=self.cookies, dont_filter=True)

    def parse_token(self, response):
        meta = response.meta
        meta['token'] = re.search(r'apiKey: \'(.*?)\'', response.text).group(1)
        meta['host'] = re.search(r'host: \'(.*?)\'', response.text).group(1)
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
                if 'page' in meta and meta['page'] < self.limit_pages:
                    meta['page'] = meta['page'] + 1
                    print(meta['page'])
                    yield self.call_algolia(meta['page'], meta)

    def get_scenes(self, response):
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
                item['date'] = datetime.datetime.utcfromtimestamp(scene['publish_date']).strftime('%Y-%m-%d')
                # ~ print(f"Datetime: {scene['publish_date']}     Parsed_date: {item['date']}")
            else:
                print("Date not provided, using today")
                item['date'] = self.parse_date('today').strftime('%Y-%m-%d')

            item['performers'] = [scene['model_username']]
            item['tags'] = scene['categories'] + scene['keywords']
            item['tags'] = [i for i in item['tags'] if i]

            if "video_length" in scene and scene['video_length'] and re.search(r'((?:\d{1,2}\:)?\d{2}\:\d{2})', scene['video_length']):
                scene['video_length'] = re.search(r'((?:\d{1,2}\:)?\d{2}\:\d{2})', scene['video_length']).group(1)
                item['duration'] = self.duration_to_seconds(scene['video_length'])

            item['site'] = "I Want Clips"
            item['parent'] = "I Want Clips"
            item['network'] = "I Want Clips"
            item['url'] = scene['content_url']
            yield self.check_item(item, self.days)

    def call_algolia(self, page, meta):
        token = meta['token']
        host = meta['host']
        referrer = meta['url']
        # ~ print (f'Page: {page}        Token: {token}     Referrer: {referrer}')
        # ~ algolia_url = 'https://tsmkfa364q-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia for vanilla JavaScript 3.27.1;JS Helper 2.26.0&x-algolia-application-id=TSMKFA364Q&x-algolia-api-key=%s' % token
        algolia_url = f"https://{host}/multi_search?x-typesense-api-key={token}"

        headers = {
            'Content-Type': 'application/json',
            'Referer': self.get_next_page_url(referrer, page)
        }
        # ~ jbody = '{"searches":[{"per_page":10,"sort_by":"publish_date:desc,popularity:desc","query_by":"title,description,member_id,model_username,categories,price_range,nudity,keywords,viewable_by,aa_ai,aa_body-shape,aa_body-type,aa_breast-size,aa_butt-size,aa_butt-type,aa_eye-color,aa_foot-size,aa_glasses,aa_hair-color,aa_hair-length,aa_height,aa_piercings,aa_pubic-hair,aa_tattoos,aa_origin-country,aa_race,aa_age,aa_circumcised,aa_endowment,aa_ethnicity,aa_girth,aa_language,aa_nose,aa_qwe,aa_wake,aa_wake-attributes,aa_abs","query":"*","highlight_full_fields":"title,description,member_id,model_username,categories,price_range,nudity,keywords,viewable_by,aa_ai,aa_body-shape,aa_body-type,aa_breast-size,aa_butt-size,aa_butt-type,aa_eye-color,aa_foot-size,aa_glasses,aa_hair-color,aa_hair-length,aa_height,aa_piercings,aa_pubic-hair,aa_tattoos,aa_origin-country,aa_race,aa_age,aa_circumcised,aa_endowment,aa_ethnicity,aa_girth,aa_language,aa_nose,aa_qwe,aa_wake,aa_wake-attributes,aa_abs","collection":"prod_content","q":"*","facet_by":"type,nudity,nudity","max_facet_values":10,"page":' + str(page) + '}]}'
        jbody = '{"searches":[{"per_page":100,"sort_by":"publish_date:desc,popularity:desc","query_by":"title,description,member_id,model_username,categories,price_range,nudity,keywords,viewable_by,aa_ai,aa_body-shape,aa_body-type,aa_breast-size,aa_butt-size,aa_butt-type,aa_eye-color,aa_foot-size,aa_glasses,aa_hair-color,aa_hair-length,aa_height,aa_piercings,aa_pubic-hair,aa_tattoos,aa_origin-country,aa_race,aa_age,aa_circumcised,aa_endowment,aa_ethnicity,aa_girth,aa_language,aa_nose,aa_qwe,aa_wake,aa_wake-attributes,aa_abs","query":"*","highlight_full_fields":"title,description,member_id,model_username,categories,price_range,nudity,keywords,viewable_by,aa_ai,aa_body-shape,aa_body-type,aa_breast-size,aa_butt-size,aa_butt-type,aa_eye-color,aa_foot-size,aa_glasses,aa_hair-color,aa_hair-length,aa_height,aa_piercings,aa_pubic-hair,aa_tattoos,aa_origin-country,aa_race,aa_age,aa_circumcised,aa_endowment,aa_ethnicity,aa_girth,aa_language,aa_nose,aa_qwe,aa_wake,aa_wake-attributes,aa_abs","collection":"prod_content","q":"*","facet_by":"type,nudity,nudity","max_facet_values":10,"page":' + str(page) + '}]}'

        return scrapy.Request(
            url=algolia_url,
            method='post',
            body=jbody,
            meta=meta,
            callback=self.parse,
            headers=headers
        )
