import re
import string
import scrapy
from tpdb.helpers.http import Http
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteMosoMonsterSpider(BaseSceneScraper):
    name = 'MosoMonster'

    start_urls = [
        'https://moso.monster',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/api/j/home/?start=%s',
        'type': 'Scene',
    }

    def get_next_page_url(self, base, page):
        page = str((int(page) - 1) * 15)
        return self.format_url(base, self.get_selector_map('pagination') % page)

    def get_scenes(self, response):
        meta = response.meta
        jsondata = response.json()
        for scene in jsondata['data']['videos']:
            meta['id'] = scene['id']
            meta['title'] = self.cleanup_title(scene['title'])
            link = f"https://moso.monster/api/video/{meta['id']}/"
            yield scrapy.Request(link, callback=self.parse_scene, meta=meta)

    def parse_scene(self, response):
        meta = response.meta
        item = self.init_scene()
        scene = response.json()
        item['id'] = meta['id']
        item['title'] = meta['title']
        if scene['bango'] and len(scene['bango']) > 3:
            item['title'] = f"{scene['bango']} - {item['title']}"

        item['description'] = self.cleanup_description(scene['desc'])
        item['date'] = re.search(r'(\d{4}-\d{2}-\d{2})', scene['publish_time']).group(1)

        item['image'] = scene['itemImageSrc']
        if item['image']:
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
        else:
            item['image_blob'] = ''

        item['poster'] = scene['itemVerticalImageSrc']
        if item['poster']:
            if "?width" in item['poster']:
                item['poster'] = re.search(r'(.*)\?', item['poster']).group(1)
            item['poster_blob'] = self.get_image_blob_from_link(item['poster'])
        else:
            item['poster_blob'] = ''

        if scene['length']:
            item['duration'] = self.duration_to_seconds(scene['length'])

        item['url'] = f"https://moso.monster/video/{item['id']}/"
        item['network'] = "Moso Monster"
        item['site'] = "Moso Monster"
        item['parent'] = "Moso Monster"

        item['performers'], item['performers_data'] = self.get_performers(scene['actors'])
        tags = scene['tags']
        for tag in tags:
            if string.capwords(tag.strip()) not in item['performers']:
                item['tags'].append(string.capwords(tag.strip()))

        yield self.check_item(item, self.days)

    def get_performers(self, actors):
        performers = []
        perf_data = []
        for actor in actors:
            perf = {}
            perf['extra'] = {}
            perf['name'] = string.capwords(actor['name'])
            performers.append(perf['name'])
            height = re.search(r'(\d+)', actor['height'])
            if height:
                perf['extra']['height'] = height.group(1)
            if actor['nationality']:
                perf['nationality'] = actor['nationality']
            if actor['sex'] == 0:
                perf['extra']['gender'] = "Female"
            if actor['sex'] == 1:
                perf['extra']['gender'] = "Male"
            if actor['thumb_url']:
                perf['image'] = actor['thumb_url']
                perf['image_blob'] = self.get_image_blob_from_link(perf['image'])

            if actor['sex'] == 0 and 'measurement' in actor and actor['measurement']:
                measurements = re.search(r'(\d+)[^0-9]+?(\d+)[^0-9]+?(\d+)', actor['measurement'])
                if measurements:
                    bust_cm, waist_cm, hips_cm = map(int, measurements.groups())
                    bust_in = round(bust_cm * 0.3937)
                    waist_in = round(waist_cm * 0.3937)
                    hips_in = round(hips_cm * 0.3937)
                    perf['extra']['measurements'] = f"{bust_in}-{waist_in}-{hips_in}"

            perf['network'] = "Moso Monster"
            perf['site'] = "Moso Monster"

            perf_data.append(perf)
        return performers, perf_data

    def get_image_from_link(self, image):
        if image:
            req = Http.get(image, headers=self.headers, cookies=self.cookies, follow_redirects=True)
            if req and req.is_success:
                return req.content
        return None
