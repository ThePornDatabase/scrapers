import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteEricVideosSpider(BaseSceneScraper):
    name = 'EricVideos'
    network = 'Eric Videos'
    parent = 'Eric Videos'
    site = 'Eric Videos'

    start_urls = [
        'https://www.ericvideos.com',
    ]

    cookies = {'warning': '1', 'lang': 'EN', 'locale': 'en_US'}

    selector_map = {
        'title': '//h1[contains(@class,"video_titre")]/text()',
        'description': '//div[@class="video-info"]//div[@class="texte"]/text()',
        'image': '//div[@class="vid"]/@data-poster',
        'performers': '//div[@class="acteurs"]//div[@class="nom"]/text()',
        'tags': '//div[@class="categories"]/ul/li/a/text()',
        'trailer': '//div[@class="vid"]/@data-hls',
        'external_id': r'.*/(\d+)/.*?',
        'pagination': '/EN/vod/1/page%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "vod-item")]/a[contains(@class, "lien_block")]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_duration(self, response):
        duration = response.xpath('//i[@class="icon icon-clock"]/following-sibling::text()[1]')
        if duration:
            duration = duration.get()
            if re.search(r'(\d+)', duration):
                duration = re.search(r'(\d+)', duration).group(1)
                duration = str(int(duration) * 60)
        return duration
