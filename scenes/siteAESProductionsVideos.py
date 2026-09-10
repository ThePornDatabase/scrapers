import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class siteAESProductionsVideosSpider(BaseSceneScraper):
    name = 'AESProductionsVideos'
    network = 'AES Productions'
    parent = 'AES Productions'
    site = 'AES Productions'

    start_urls = [
        'https://estore.surfnetcorp.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'image': '//div[contains(@class, "product-image-container")]/img/@src',
        'trailer': '',
        'external_id': r'id=(.*?)\&',
        'pagination': '/store/aesclips/index.cfm?showall=Newestreleases&pg=%s&ipp=12',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        scenes = response.xpath('//div[@class="product-thumb"]/div[1]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_date(self, response):
        scenedate = response.xpath('//div[@class="product-meta-line"]/text()')
        if scenedate:
            scenedate = scenedate.get()
            scenedate = scenedate.replace("\r", "").replace("\n", "").replace("\t", "").strip()
            scenedate = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', scenedate)
            if scenedate:
                scenedate = scenedate.group(1)
                return self.parse_date(scenedate).strftime('%Y-%m-%d')
        return None
    
    def get_duration(self, response):
        duration = response.xpath('//div[@class="product-meta-line"]/text()')
        if duration:
            duration = duration.get()
            duration = duration.replace("\r", "").replace("\n", "").replace("\t", "").replace(" ", "").strip().lower()
            durationcheck = re.search(r'(\d+hr\d+min\d+sec)', duration)
            if not durationcheck:
                durationcheck = re.search(r'(\d+min\d+sec)', duration)

            if durationcheck:
                durationcheck = durationcheck.group(1)
                
                hours = re.search(r'(\d+)hr', durationcheck)
                minutes = re.search(r'(\d+)min', durationcheck)
                seconds = re.search(r'(\d+)sec', durationcheck)
                total_seconds = 0
                if hours:
                    total_seconds += int(hours.group(1)) * 3600
                if minutes:
                    total_seconds += int(minutes.group(1)) * 60
                if seconds:                    
                    total_seconds += int(seconds.group(1))

                return str(total_seconds)

        return None
    
    def get_tags(self, response):
        return ['Bondage']