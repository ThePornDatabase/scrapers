import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SitePeachyKeenFilmsSpider(BaseSceneScraper):
    name = 'PeachyKeenFilms'
    site = 'Peachy Keen Films'
    parent = 'Peachy Keen Films'
    network = 'Peachy Keen Films'

    start_urls = [
        'https://www.pkfstudios.com',
    ]

    selector_map = {
        'title': '//h1[contains(@class, "entry-title")]/text()',
        'description': '//div[@class="wp-video"]/following-sibling::p/text()',
        'date': '//time[@class="entry-date"]/@datetime',
        're_date': r'(\d{4}-\d{2}-\d{2})',
        'image': '//div[@class="post-thumbnail"]/img/@data-lazy-src',
        'performers': '',
        'tags': '//span[@class="cat-links"]/a/text()',
        'duration': '',
        'trailer': '//video/source/@src',
        'external_id': r'.*/(.*?)/',
        'pagination': '/updates/page/%s/',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//header[@class="entry-header"]//h1/a[1]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_performers(self, response):
        performers = response.xpath('//div[@class="entry-content"]/p/strong[contains(text(), "Starring")]/text()')
        if performers:
            performers = performers.get()
            performers = performers.lower()
            performers = performers.replace("starring", "").strip()
            if " and " in performers:
                performers = performers.split(" and ")
            else:
                performers = [performers]

            return list(map(lambda x: string.capwords(x.strip()), performers))
        return []

    def get_trailer(self, response):
        trailer = response.xpath('//video/source/@src')
        if trailer:
            trailer = trailer.get()
        if "?" in trailer:
            trailer = re.search(r'(.*?)\?', trailer).group(1)
        if not trailer:
            trailer = ""
        return trailer.replace(" ", "%20")
