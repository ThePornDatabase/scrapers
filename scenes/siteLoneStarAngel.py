import re
import string
import requests
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteLoneStarAngelSpider(BaseSceneScraper):
    name = 'LoneStarAngel'
    network = 'Lone Star Angel'
    parent = 'Lone Star Angel'
    site = 'Lone Star Angel'

    start_urls = [
        'https://www.thelonestarangel.com',
    ]

    selector_map = {
        'description': '//span[contains(@class,"latest_update_description")]//text()',
        'tags': '//span[contains(@class,"update_tags")]/a/text()',
        'trailer': '',
        'external_id': r'',
        'pagination': '/categories/movies_%s_d.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        scenes = response.xpath('//div[@class="updateItem"]')
        for scene in scenes:
            scenedate = scene.xpath('.//span[contains(text(), "/")]/text()').get()
            if scenedate:
                scenedate = re.search(r'(\d{2}/\d{2}/\d{4})', scenedate.strip())
                if scenedate:
                    scenedate = scenedate.group(1)
                    scenedate = self.parse_date(scenedate, date_formats=['%m/%d/%Y']).strftime('%Y-%m-%d')
                    meta['date'] = scenedate

            title = scene.xpath('.//h4/a/text()').get()
            if title:
                title = title.strip()
                meta['title'] = string.capwords(self.cleanup_title(title))

            sceneid = scene.xpath('.//img/@id').get()
            if sceneid:
                sceneid = re.search(r'.*-(\d+)', sceneid)
                if sceneid:
                    sceneid = sceneid.group(1)
                    meta['id'] = sceneid

            image = scene.xpath('.//img/@src0_4x').get()
            if image:
                image = self.format_link(response, image)
                meta['image'] = image

            sceneurl = scene.xpath('.//h4/a/@href').get()

            if self.check_item(meta, self.days) and meta['id']:
                meta['image_blob'] = self.get_image_blob_from_link(image)
                yield scrapy.Request(url=self.format_link(response, sceneurl), callback=self.parse_scene, meta=meta)

    def get_duration(self, response):
        duration = response.xpath('//div[contains(@class,"update_counts_preview_table")]/text()')
        if duration:
            duration = duration.get()
            if "min" in duration.lower():
                duration = duration.replace("&nbsp;", "")
                duration = re.search(r'(\d+)(?=[^\d]*min)', duration)
                if duration:
                    duration = str(int(duration.group(1)) * 60)
                return duration
        return None
    
    def get_performers(self, response):
        return ['Lonestar Angel']