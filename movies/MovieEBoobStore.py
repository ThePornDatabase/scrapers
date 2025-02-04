import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class MovieEBoobStoreSpider(BaseSceneScraper):
    name = 'MovieEBoobStore'
    network = 'Score'
    parent = 'Score'
    site = 'Score'

    start_urls = [
        'https://www.eboobstore.com',
    ]

    selector_map = {
        'title': '//meta[@name="twitter:title"]/@content|//meta[@property="og:title"]/@content',
        'description': '//div[contains(@class, "description") and contains(@class, "full")]/div//text()',
        'date': '',
        'image': '//meta[@name="twitter:image"]/@content|//meta[@itemprop="image"]/@content',
        'performers': '//h2[contains(text(), "Models")]/../following-sibling::article/div/a/div/text()',
        'tags': '',
        'duration': '',
        'trailer': '//video/source/@src',
        'external_id': r'.*/(\d+)/',
        'pagination': '/adult-movies/c/255/DVD/?page=%s',
        'type': 'Movie',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//article[contains(@class, "list-item")]/div[1]/a/@href').getall()
        for scene in scenes:
            if "?nats" in scene:
                scene = re.search(r'(.*)\?nats', scene).group(1)
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_duration(self, response):
        duration = response.xpath('//div[@class="options"]/div[@class="format-details"]//strong[contains(text(), "Duration")]/following-sibling::text()')
        if duration:
            duration = duration.get()
            if "minutes" in duration.lower():
                duration = re.search(r'(\d+)min', duration.lower().replace(" ", ""))
                if duration:
                    return str(int(duration.group(1)) * 60)
        return None
