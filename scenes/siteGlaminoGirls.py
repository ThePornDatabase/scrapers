import re
import string
import html
import tldextract
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteGlaminoGirlsSpider(BaseSceneScraper):
    name = 'GlaminoGirls'
    network = 'Czech Casting'

    start_urls = [
        'https://glaminogirls.com',
        'https://lifepornstories.com',
    ]

    # Same platform as the CzechAv network: /tour/page-N/ 404s, each site now serves
    # its whole listing on the root, and div.episode__preview is gone.  The scene
    # page still publishes a full schema.org VideoObject, so the item is built from
    # that rather than scraped out of the listing card.
    selector_map = {
        'title': "//meta[@property='og:title']/@content",
        'description': '//script[contains(@type, "json")]/text()',
        're_description': r'description[\'\"]\s*:\s*[\'\"](.*?)[\'\"],',
        'date': '//script[contains(@type, "json")]/text()',
        're_date': r'uploadDate[\'\"].*?(\d{4}-\d{2}-\d{2})',
        'image': "//meta[@property='og:image']/@content",
        're_image': r'(.*)\?',
        'performers': '',
        'tags': '',
        'external_id': r'/video/(.+?)/',
        'trailer': '//script[contains(@type, "json")]/text()',
        're_trailer': r'contentUrl[\'\"]\s*:\s*[\'\"](https?://[^\'\"]+)',
        'pagination': ''
    }

    async def start(self):
        meta = {}
        meta['page'] = self.page
        for link in self.start_urls:
            yield scrapy.Request(link, callback=self.parse, meta=meta,
                                 headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        scenes = response.xpath('//a[contains(@href, "/video/")]/@href').getall()
        for scene in dict.fromkeys(scenes):
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_tags(self, response):
        tags = response.xpath('//script[contains(@type, "json")]/text()').get() or ''
        found = re.search(r'keywords[\'\"]\s*:\s*[\'\"](.*?)[\'\"]', tags)
        if not found:
            return []
        return [string.capwords(x.strip()) for x in found.group(1).split(',') if x.strip()]

    def get_site(self, response):
        domain = tldextract.extract(response.url).domain
        return {'glaminogirls': 'Glamino Girls',
                'lifepornstories': 'Life Porn Stories'}.get(domain, string.capwords(domain))

    def get_parent(self, response):
        return self.get_site(response)
