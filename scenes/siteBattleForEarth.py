import re
import json
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteBattleForEarthSpider(BaseSceneScraper):
    name = 'BattleForEarth'
    network = 'Battle For Earth'
    parent = 'Battle For Earth'
    site = 'Battle For Earth'

    start_urls = [
        'https://www.thebattleforearth.com/all-releases',
    ]

    selector_map = {
        'title': '',
        'description': '//div[contains(@data-testid, "richTextElement")]//span[@class="wixGuard"]/../following-sibling::p/text()',
        'date': '//script[contains(text(), "thumbnailUrl")]/text()',
        're_date': r'uploadDate.*?(\d{4}.*?)\"',
        'image': '//script[contains(text(), "thumbnailUrl")]/text()',
        're_image': r'videos.*?thumbnailUrl.*?(http.*?)\"',
        'performers': '',
        'tags': '',
        'duration': '//span[contains(text(), "Runtime")]/text()',
        're_duration': r'\d{1,2}:\d{2}(?:\:\d{2})?',
        'trailer': '',
        'external_id': r'\.com/(.*)',
        'pagination': '/all-releases?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//script[@id="wix-viewer-model"]/text()').get()
        jsondata = json.loads(scenes)
        jsondata = jsondata['siteFeaturesConfigs']['router']
        for value in jsondata['pagesMap']:
            meta['title'] = jsondata['pagesMap'][value]['title']
            meta['url'] = "https://www.thebattleforearth.com/" + jsondata['pagesMap'][value]['pageUriSEO']
            meta['id'] = jsondata['pagesMap'][value]['pageId']
            yield scrapy.Request(meta['url'], callback=self.parse_scene, meta=meta)

    def get_duration(self, response):
        duration = response.xpath(self.get_selector_map('duration')).get()
        if duration:
            duration = re.search(r'(\d{1,2}:\d{2}(?:\:\d{2})?)', duration)
            if duration:
                duration = duration.group(1)
                duration = self.duration_to_seconds(duration)
        return duration

    def get_date(self, response):
        scenedate = response.xpath(self.get_selector_map('date'))
        if scenedate:
            scenedate = re.search(r'uploadDate.*?(\d{4}.*?)\"', scenedate.get())
            if scenedate:
                scenedate = scenedate.group(1)
                scenedate = re.search(r'(.*)\.', scenedate).group(1)
                return scenedate
        return self.parse_date('today').isoformat()

    def get_image(self, response):
        image = super().get_image(response)
        return image.replace(" ", "%20")
