import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteTabooluSpider(BaseSceneScraper):
    name = 'Taboolu'
    network = 'Taboolu'
    parent = 'Taboolu'

    start_urls = [
        'https://taboolu.com',
    ]

    custom_scraper_settings = {
        'REDIRECT_ENABLED': False,
    }

    cookies = [
        {"name": "ageConfirmed", "value": "true"},
        {"name": "use_lang", "value": "val=en"},
        {"name": "defaults", "value": "{'hybridView':'member'}"},
    ]

    selector_map = {
        'title': '//h1[@class="description"]/text()|//div[contains(@class, "boxcover")]/img/@title',
        'description': '//div[@class="synopsis"]/p//text()',
        'date': '//div[@class="release-date"]/span[contains(text(), "Released")]/following-sibling::text()',
        # 'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[@class="video-performer"]/a/div/text()',
        'tags': '//div[@class="tags"]/a/text()',
        'external_id': r'.*/(\d+)/',
        'pagination': '/watch-newest-taboolu-clips-and-scenes.html?page=%s&hybridview=member',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        scenes = response.xpath('//article/div[1]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                meta['orig_scene'] = scene
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_duration(self, response):
        duration = response.xpath('//div[@class="release-date"]/span[contains(text(), "Length")]/following-sibling::text()')
        if duration:
            duration = re.search(r'(\d+)', duration.get())
            if duration:
                return str(int(duration.group(1)) * 60)
        return ""
    
    def get_site(self, response):
        series = response.xpath('//div[@class="series"]/a/text()')
        if series:
            return string.capwords(series.get().strip())
        return "Taboolu"

    def get_performers_data(self, response):
        performers = super().get_performers(response)
        performers_data = []
        for performer in performers:
            performer = string.capwords(performer.strip())
            performer_extra = {}
            performer_extra['name'] = performer
            performer_extra['site'] = "MF Video"
            performer_extra['extra'] = {}
            performer_extra['extra']['gender'] = "Female"
            performers_data.append(performer_extra)

        return performers_data