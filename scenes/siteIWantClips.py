import re
import datetime
import string
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteIWantClipsSpider(BaseSceneScraper):
    name = 'IWantClips'
    network = 'I Want Clips'

    start_url = 'https://iwantclips.com'

    cookies = {'accepted': '1', 'member_id': '0'}

    selector_map = {
        'external_id': '(\\d+)$',
        'pagination': '/?page=%s'
    }

    def start_requests(self):
        # ~ page = int(self.page) - 1
        page = int(self.page)

        if self.limit_pages == 1:
            self.limit_pages = 50

        yield scrapy.Request(url=self.get_next_page_url(self.start_url, page + 1), callback=self.parse_token, meta={'page': page, 'url': self.start_url}, cookies=self.cookies, dont_filter=True)

    def parse_token(self, response):
        meta = response.meta
        token_script = response.xpath('//script[contains(text(), "let typesenseIndex = \'prod_content\'") and contains(text(), "apiKey")]/text()').get()
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
                if 'page' in meta and meta['page'] < self.limit_pages:
                    meta['page'] = meta['page'] + 1
                    print(meta['page'])
                    yield scrapy.Request(url=self.get_next_page_url(self.start_url, meta['page']), callback=self.parse_token, meta={'page': meta['page'], 'url': self.start_url}, cookies=self.cookies, dont_filter=True)
                    # ~ yield self.call_algolia(meta['page'], meta)

    def get_scenes(self, response):
        for scene in response.json()['results'][0]['hits']:
            scene = scene['document']
            item = SceneItem()

            if ".gif" in scene['thumbnail_url'] and scene['thumbnail']:
                cdn_host = re.search(r'(.*?\.com)/', scene['thumbnail_url']).group(1)
                item['image'] = f"{cdn_host}/uploads/contents/videos/{scene['member_id']}/{scene['thumbnail']}"
            else:
                item['image'] = scene['thumbnail_url']

            if "/contents/" not in item['image'] and "/contents/" in scene['preview_url']:
                item['image'] = scene['preview_url']

            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            # ~ item['image_blob'] = ""
            if 'preview_mp4_url' in scene:
                item['trailer'] = scene['preview_mp4_url']
                if "https" not in item['trailer'].lower():
                    item['trailer'] = None
            else:
                item['trailer'] = None
            item['id'] = scene['content_id']
            item['title'] = string.capwords(scene['title'])
            item['description'] = re.sub(r'<[^>]+>', '', scene['description'])
            item['description'] = re.sub(r'[\r\n\t]+', ' ', item['description'])
            item['description'] = re.sub(r'\s+', ' ', item['description'])

            if scene['publish_date']:
                item['date'] = datetime.datetime.utcfromtimestamp(scene['publish_date']).strftime('%Y-%m-%d')
                # ~ print(f"Datetime: {scene['publish_date']}     Parsed_date: {item['date']}")
            else:
                print("Date not provided, using today")
                item['date'] = self.parse_date('today').strftime('%Y-%m-%d')

            item['performers'] = [scene['model_username']]
            if " and " in scene['model_username'].lower():
                item['performers'] = scene['model_username'].lower().split(" and ")
            if " & " in scene['model_username'].lower():
                item['performers'] = scene['model_username'].lower().split(" & ")

            item['performers'] = list(map(lambda x: string.capwords(x.strip()), item['performers']))

            item['tags'] = scene['categories'] + scene['keywords']
            item['tags'] = [i for i in item['tags'] if i]

            if "video_length" in scene and scene['video_length'] and re.search(r'((?:\d{1,2}\:)?\d{2}\:\d{2})', scene['video_length']):
                scene['video_length'] = re.search(r'((?:\d{1,2}\:)?\d{2}\:\d{2})', scene['video_length']).group(1)
                item['duration'] = self.duration_to_seconds(scene['video_length'])

            studioname = scene['model_username']
            item['site'] = f"I Want Clips: {string.capwords(studioname)}"
            item['parent'] = "I Want Clips"
            item['network'] = "I Want Clips"
            item['url'] = scene['content_url']

            item['performers'] = [scene['model_username']]
            if len(item['performers']) == 1:
                perf_data = self.get_performers_data(scene, item.copy())
                if perf_data:
                    item['performers_data'] = perf_data

            item['performers'] = list(map(lambda x: string.capwords(x.strip()), item['performers']))

            if len(item['performers']) > 1:
                item['performers'] = [f"{performer} ({scene['member_id']})" for performer in item['performers']]

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
        jbody = '{"searches":[{"per_page":100,"sort_by":"publish_date:desc,popularity:desc","query_by":"title,description,member_id,model_username,categories,price_range,nudity,keywords,viewable_by,aa_ai,aa_body-shape,aa_body-type,aa_breast-size,aa_butt-size,aa_butt-type,aa_eye-color,aa_foot-size,aa_glasses,aa_hair-color,aa_hair-length,aa_height,aa_piercings,aa_pubic-hair,aa_tattoos,aa_origin-country,aa_race,aa_age,aa_circumcised,aa_endowment,aa_ethnicity,aa_girth,aa_language,aa_nose,aa_qwe,aa_wake,aa_wake-attributes,aa_abs","query":"*","highlight_full_fields":"title,description,member_id,model_username,categories,price_range,nudity,keywords,viewable_by,aa_ai,aa_body-shape,aa_body-type,aa_breast-size,aa_butt-size,aa_butt-type,aa_eye-color,aa_foot-size,aa_glasses,aa_hair-color,aa_hair-length,aa_height,aa_piercings,aa_pubic-hair,aa_tattoos,aa_origin-country,aa_race,aa_age,aa_circumcised,aa_endowment,aa_ethnicity,aa_girth,aa_language,aa_nose,aa_qwe,aa_wake,aa_wake-attributes,aa_abs","collection":"prod_content","q":"*","facet_by":"member_id,type,nudity,nudity,nudity,nudity,nudity,nudity","max_facet_values":10,"page":' + str(page) + '}]}'
        return scrapy.Request(
            url=algolia_url,
            method='post',
            body=jbody,
            meta=meta,
            callback=self.parse,
            headers=headers
        )

    def get_performers_data(self, scene, item):
        perf = {}

        if "gender" in scene and scene['gender']:
            perf['name'] = string.capwords(item['performers'][0])
            gender = scene['gender'].lower().strip()
            perf['extra'] = {}
            if gender == "f":
                perf['extra']['gender'] = "Female"
            elif gender == "m":
                perf['extra']['gender'] = "Male"
            elif gender == "ts" or gender == "tg" or gender == "mtf":
                perf['extra']['gender'] = "Trans Female"
            elif gender == "ftm":
                perf['extra']['gender'] = "Trans Male"

            if "avatar" in scene and len(scene['avatar']):
                perf['image'] = scene['avatar']
                perf['image_blob'] = self.get_image_blob_from_link(perf['image'])
                # ~ perf['image_blob'] = ""

            perf['network'] = "IWantClips"
            perf['site'] = "IWantClips"
            return [perf]
        return None
