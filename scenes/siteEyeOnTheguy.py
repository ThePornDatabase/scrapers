import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteEyeOnTheGuySpider(BaseSceneScraper):
    name = 'EyeOnTheGuy'
    network = 'Eye on the Guy'
    parent = 'Eye on the Guy'
    site = 'Eye on the Guy'

    start_urls = [
        'https://www.eyeontheguy.com',
    ]

    selector_map = {
        'title': '//div[not(@class="container")]/div[@class="title-block"]/h2[@class="section-title"]/text()',
        'description': '//h3[contains(text(), "Description")]/following-sibling::text()',
        'date': '//strong[contains(text(), "Released")]/following-sibling::text()',
        'date_formats': ['%B %d, %Y'],
        'image': '//script[contains(text(), "video_content")]/text()',
        're_image': r'poster=\"(.*\.jpg)',
        'performers': '//div[contains(@class, "models-list-thumbs")]/ul/li/a/span/text()',
        'tags': '//ul[@class="tags"]/li/a/text()',
        'trailer': '//script[contains(text(), "video_content")]/text()',
        're_trailer': r'src=\"(.*\.mp4)',
        'external_id': r'.*/(.*?)\.htm',
        'pagination': '/t1/categories/movies_%s_d.html'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//h4/a[contains(@href, "/t1/trailers")]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
