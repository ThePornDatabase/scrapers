import scrapy
import re

from tpdb.BaseSceneScraper import BaseSceneScraper


class siteFutileStrugglesSpider(BaseSceneScraper):
    name = 'FutileStruggles'
    network = 'Futile Struggles'
    site = "Futile Struggles"
    parent = "Futile Struggles"


    start_urls = [
        'http://www.futilestruggles.com',
    ]

    cookies = [{"name": "warn", "value": "true"}]

    selector_map = {
        'title': '//div[@class="title_bar"]/span/text()',
        'description': '//span[@class="update_description"]/text()',
        'tags': '//span[@class="update_tags"]/a/text()',
        'external_id': 'id=(\d+)',
        'trailer': '',
        'pagination': '/trial/index.php?page=%s'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="latest_updates_block"]//div[@class="update_details"]')
        for scene in scenes:
            image = scene.xpath('.//img/@src0_3x')
            if image:
                image = image.get()
                meta['image'] =  "http://www.futilestruggles.com" + image.strip()
            else:
                meta['image'] = ''

            scenedate = scene.xpath('.//comment()[contains(., "Date")]/following-sibling::text()[1]')
            if scenedate:
                scenedate = scenedate.get().strip()
                scenedate = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', scenedate)
                if scenedate:
                    meta['date'] = self.parse_date(scenedate.group(1), date_formats=['%m/%d/%Y']).strftime('%Y-%m-%d')

            meta['performers'] = scene.xpath('.//span[@class="update_models"]/a/text()').getall()
            meta['performers_data'] = self.get_performers_data(meta['performers'])

            duration = scene.xpath('.//div[@class="update_counts" and contains(text(), "min") and contains(text(), "video")]/text()')
            if duration:
                duration = duration.get()
                duration = duration.replace("&nbsp;", "")
                duration = re.sub(r'[^a-z0-9]+', '', duration.lower())
                duration = re.search(r'(\d+)min', duration)
                if duration:
                    meta['duration'] = str(int(duration.group(1)) * 60)

            scene = "http://www.futilestruggles.com/trial/" + scene.xpath('./a[1]/@href').get()
            if re.search(self.get_selector_map('external_id'), scene) and meta['date']:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_performers_data(self, performers):
        performers_data = []
        if len(performers):
            for performer in performers:
                perf = {}
                perf['name'] = performer
                perf['extra'] = {}
                perf['extra']['gender'] = "Female"
                perf['network'] = "Futile Struggles"
                perf['site'] = "Futile Struggles"
                performers_data.append(perf)
        return performers_data

