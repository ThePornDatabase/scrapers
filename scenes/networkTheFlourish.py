import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkTheFlourishSpider(BaseSceneScraper):
    name = 'TheFlourish'
    network = 'The Flourish'

    start_urls = [
        'https://tour.theflourishamateurs.com',
        'https://tour.theflourishfetish.com',
        'https://tour.theflourishpov.com',
        'https://tour.theflourishxxx.com',
    ]

    selector_map = {
        'title': '//div[@class="bodyInnerArea"][1]//h2/text()',
        'description': '//div[@class="description"]/p/text()',
        'date': '',
        'image': '//script[contains(text(), "video_content")]/text()',
        're_image': r'poster=.*?\"(/content.*\.jpg)',
        'performers': '//div[@class="info"]//a[contains(@href, "/models/")]/text()',
        'tags': '//ul[@class="tags"]/li/a/text()',
        'trailer': '//script[contains(text(), "video_content")]/text()',
        're_trailer': r'video src=.*?\"(/trailer.*\.mp4)',
        'external_id': r'^.*/(.*?).html',
        'pagination': '/categories/movies_%s_d.html'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class,"item-video")]')
        for scene in scenes:
            date = scene.xpath('.//div[@class="timeDate"]/text()')
            meta['date'] = self.parse_date('today').isoformat()
            if date:
                date = re.search(r'(\d{4}-\d{2}-\d{2})', date.get())
                if date:
                    meta['date'] = self.parse_date(date.group(1), date_formats=['%Y-%m-%d']).isoformat()
            scene = scene.xpath('./div[@class="item-thumb"]/a/@href').get()

            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_tags(self, response):
        origtags = super().get_tags(response)
        tags = []
        for tag in origtags:
            if "series" not in tag.lower() and not re.search(r'(\d+p)', tag) and not re.search(r'(\d+k)', tag):
                tags.append(string.capwords(tag))
        if tags:
            return tags

        return origtags

    def get_site(self, response):
        if "amateurs" in response.url:
            return "The Flourish Amateurs"
        if "fetish" in response.url:
            return "The Flourish Fetish"
        if "pov" in response.url:
            return "The Flourish POV"
        if "xxx" in response.url:
            return "The Flourish XXX"

        return "The Flourish"

    def get_parent(self, response):
        if "amateurs" in response.url:
            return "The Flourish Amateurs"
        if "fetish" in response.url:
            return "The Flourish Fetish"
        if "pov" in response.url:
            return "The Flourish POV"
        if "xxx" in response.url:
            return "The Flourish XXX"

        return "The Flourish"
