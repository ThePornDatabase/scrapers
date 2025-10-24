import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkFTMPlusSpider(BaseSceneScraper):
    name = 'FTMPlus'
    network = 'FTMPlus'

    start_urls = [
        'https://ftmplus.com',
    ]

    selector_map = {
        'description': '//div[@class="textDescription"]//p/text()',
        'date': '//div[@class="releasedate"]/text()',
        're_date': r'(\w+ \d{1,2}, \d{4})',
        'image': '//video[contains(@id,"video-bb")]/@poster',
        'performers': '//div[contains(@class,"item-model")]//h4/text()',
        'tags': '//div[@class="update_tags"]/a/span/text()',
        'trailer': '',
        'external_id': r'videos/(.*)(?:_vids)?\.htm',
        'pagination': '/videos?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="grid-vid-item"]')
        for scene in scenes:
            site = scene.xpath('.//div[@class="update-sitename"]/text()')
            if site:
                site = self.cleanup_title(site.get())
                meta['site'] = site
                meta['parent'] = site

            scene = scene.xpath('./div/a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_title(self, response):
        title = response.xpath('//h2[@class="serieMovie"]/text()').get()
        serie_name = response.xpath('//h2[@class="serie_name"]/text()')
        if serie_name:
            serie_name = " - " + serie_name.get()
        else:
            serie_name = ""
        if title:
            title = string.capwords(title + serie_name)
        else:
            title = response.xpath('//div[contains(@class,"titlePlayer")]/h2/text()')
            if title:
                title = string.capwords(title.get())
        if not title:
            title = response.xpath('//h2[@class="video-detail-h2"]/text()')
            if title:
                title = string.capwords(title.get().strip())
        if not title:
            title = ""
        return title

    def get_duration(self, response):
        duration = response.xpath('//div[@class="releasedate"]/text()')
        if duration:
            duration = re.search(r'(\d+)min (\d+)sec', duration.get())
            if duration:
                minutes = int(duration.group(1)) * 60
                seconds = int(duration.group(2))
                duration = str(minutes + seconds)
                return duration
        return None
