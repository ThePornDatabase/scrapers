import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteTransEroticaSpider(BaseSceneScraper):
    name = 'TransErotica'
    site = 'TransErotica'
    parent = 'TransErotica'
    network = 'TransErotica'

    start_urls = [
        'https://tour.transerotica.com',
    ]

    selector_map = {
        'title': '//h1[@class="title_bar"]/text()',
        'description': '//div[@class="updateDetails"]/p[contains(text(), "Description:")]/text()',
        'image': '//video/@poster',
        'performers': '//h1/following-sibling::div[@class="updateDetails"]//span[contains(@class, "tour_update_models")]/a/text()',
        'tags': '//meta[@name="keywords"]/@content',
        'duration': '//h1/following-sibling::div[@class="updateDetails"]//span[contains(@class, "upddate")]',
        'trailer': '//video/source/@src',
        'external_id': r'.*/(.*?)\.htm',
        'pagination': '/categories/movies_%s_d.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="updateItem"]')
        for scene in scenes:
            scenedate = scene.xpath('.//comment()[contains(., "upddate")]')
            if scenedate:
                scenedate = scenedate.get()
                scenedate = re.search(r'(\d{2}/\d{2}/\d{4})', scenedate)
                if scenedate:
                    scenedate = scenedate.group(1)
                    meta['date'] = self.parse_date(scenedate, date_formats=['%m/%d/%Y']).strftime('%Y-%m-%d')

            scene = scene.xpath('./div[1]/a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                if "?nats" in scene:
                    scene = re.search(r'(.*?)\?nats', scene).group(1)
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_description(self, response):
        description = super().get_description(response)
        if "Description:" in description:
            description = description.replace("Description:", "").strip()
        return description

    def get_duration(self, response):
        duration = response.xpath('//h1/following-sibling::div[@class="updateDetails"]//span[contains(@class, "upddate")]/text()')
        if duration:
            duration = duration.get()
            duration = re.sub(r'[^a-z0-9]', "", duration.replace("&nbsp;", "").lower())
            minutes = 0
            seconds = 0

            minutes = re.search(r'(\d+)min', duration)
            if minutes:
                minutes = int(minutes.group(1)) * 60
            else:
                minutes = 0

            seconds = re.search(r'(\d+)sec', duration)
            if seconds:
                seconds = int(seconds.group(1))
            else:
                seconds = 0
            return str(minutes + seconds)
        return None

    def get_tags(self, response):
        performers = self.get_performers(response)
        tags = response.xpath('//meta[@name="keywords"]/@content')
        if tags:
            tags = tags.get()
            tags = tags.split(",")
            tags = list(map(lambda x: string.capwords(x.strip()), tags))
            for tag in tags:
                if tag in performers:
                    tags.remove(tag)
            if "Trans" not in tags:
                tags.append("Trans")
            if "Transerotica" in tags:
                tags.remove("Transerotica")
            return tags
        return []
