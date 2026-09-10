import re
import requests
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteXesPLSpider(BaseSceneScraper):
    name = 'XesPL'
    network = 'Xes.PL'
    parent = 'Xes.PL'
    site = 'Xes.PL'

    start_urls = [
        'https://xes.pl',
    ]

    cookies = [{"name": "lang_select", "value": "eng"}]

    # The scene page was rebuilt and its details table is gone entirely: the cast
    # now sits in a.videoHeroPerformer, the release date in a <time datetime>, and
    # the synopsis in div.videoDescription.
    selector_map = {
        'title': '//h1//text()',
        'description': '//*[contains(@class, "videoDescription")]//text()',
        # The scene page's only <time> elements are a countdown banner (a future
        # date, which check_item then drops) and a comment timestamp -- the real
        # release date is on the listing card, so get_scenes passes it via meta.
        'date': '',
        're_date': r'(\d{4}-\d{2}-\d{2})',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//a[contains(@class, "videoHeroPerformer")]/span/text()',
        'tags': '//a[contains(@href, "kategoria,") or contains(@href, "tag,")]/text()',
        'duration': '',
        'trailer': '',
        'external_id': r',(\d+),',
        'pagination': '/katalog_filmow,%s.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        # div.big-box-video became div.videoCatalogCard, whose body holds the h2 link
        for card in response.xpath('//*[contains(@class, "videoCatalogCard")][.//h2/a]'):
            scene = card.xpath('.//h2/a[contains(@href, "epizod")]/@href').get()
            if not scene or not re.search(self.get_selector_map('external_id'), scene):
                continue
            scenedate = card.xpath('.//time[contains(@class, "videoCatalogCard__date")]/@datetime').get()
            if scenedate:
                meta['date'] = scenedate.strip()[:10]
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_description(self, response):
        """Strip the "Show full description" toggle the theme injects into the text."""
        description = super().get_description(response)
        return re.sub(r'\s*Show full description\s*', ' ', description).strip()

    def get_image_from_link(self, image):
        if image:
            req = requests.get(image)
            if req and req.ok:
                return req.content
        return None

    def get_title(self, response):
        title = response.xpath('//h1//text()')
        if title:
            title = title.getall()
            title = self.cleanup_title("".join(title))
            return title
        return ""
