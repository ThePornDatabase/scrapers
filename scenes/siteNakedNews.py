import re
import datetime
import json
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteNakedNewsSpider(BaseSceneScraper):
    name = 'NakedNews'
    site = 'NakedNews'
    parent = 'NakedNews'
    network = 'NakedNews'

    start_urls = [
        'https://www.nakednews.com'
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/api/rest/v1/program?page=%s&size=36',
    }

    def get_next_page_url(self, base, page):
        page = str(int(page) - 1)
        return self.format_url(base, self.get_selector_map('pagination') % page)

    def get_scenes(self, response):
        meta = response.meta
        scenes = json.loads(response.text)
        scenes = scenes['segments']
        for scene in scenes:
            meta['id'] = scene['programSegmentId']
            meta['slug'] = scene['programSlug']
            meta['title'] = scene['title']
            scenedate = int(int(scene['date']) / 1000)
            scene_date = datetime.datetime.fromtimestamp(scenedate).strftime('%Y-%m-%d')
            if scene_date:
                meta['date'] = scene_date
            else:
                meta['date'] = self.parse_date('today').strftime('%Y-%m-%d')

            scene = f"https://www.nakednews.com/api/rest/v1/program/programSegment/{meta['id']}?showDescription=true"
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def parse_scene(self, response):
        meta = response.meta
        scene = json.loads(response.text)
        if scene:
            item = self.init_scene()

            item['title'] = self.cleanup_title(meta['title'])
            item['id'] = meta['id']
            item['description'] = self.cleanup_description(re.sub('<[^<]+?>', '', scene['description'])).replace("\r", " ").replace("\n", " ").replace("\t", " ").strip()
            item['image'] = scene['clip']['imageUrl']
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['date'] = meta['date']
            item['url'] = "https://www.nakednews.com/" + meta['slug']
            item['tags'] = ['Reality', 'News', 'Nudity']
            item['site'] = 'NakedNews'
            item['parent'] = 'NakedNews'
            item['network'] = 'NakedNews'
            item['type'] = "Scene"
            item['performers'] = []
            if 'anchors' in scene:
                item['performers_data'] = []
                for model in scene['anchors']:
                    performer = model['name']
                    performer_extra = {}
                    performer_extra['site'] = "NakedNews"
                    performer_extra['name'] = performer
                    performer_extra['extra'] = {}
                    performer_extra['extra']['gender'] = "Female"
                    if "anchorsPageImage" in model and model['anchorsPageImage']:
                        perf_image = model['anchorsPageImage']
                        if perf_image:
                            perf_image = perf_image
                            performer_extra['image'] = perf_image
                            performer_extra['image_blob'] = self.get_image_blob_from_link(performer_extra['image'])
                            if not performer_extra['image_blob']:
                                performer_extra['image_blob'] = ""
                                performer_extra['image'] = ""
                    item['performers'].append(performer)
                    if performer_extra['extra']:
                        item['performers_data'].append(performer_extra)
            if "performers_data" in item and not item['performers_data']:
                del item['performers_data']

            yield self.check_item(item, self.days)
