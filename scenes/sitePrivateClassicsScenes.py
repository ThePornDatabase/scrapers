import re
import string
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class PrivateClassicsScenesSpider(BaseSceneScraper):
    name = 'PrivateClassicsScenes'
    network = "Private"

    start_urls = [
        'https://www.privateclassics.com',
    ]

    # The site no longer nests scenes inside movie pages: /en/scenes/N now lists the
    # scenes themselves, each as an article.video card carrying its title, cast and
    # still.  The old movie -> "Scenes" -> scene walk had nothing left to walk, and
    # parse_movie's release/sinopsys markup is gone, so the item is built from the
    # card and enriched from the scene page's synopsis.
    selector_map = {
        'title': '//div[contains(@class, "content-text")]//h1/text()|//h1/text()',
        'description': '//p[contains(@class, "sinopsys")]/text()|//div[contains(@class, "content-text")]//p/text()',
        'date': '',
        'image': '',
        'performers': '//ul[@class="list-models"]/li/a/text()',
        'tags': '',
        'external_id': r'/(\d+)$',
        'pagination': '/en/scenes/%s/',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        for card in response.xpath('//article[contains(@class, "video")]'):
            link = card.xpath('.//div[contains(@class, "content-text")]/h1/a/@href').get()
            if not link or not re.search(self.get_selector_map('external_id'), link):
                continue
            meta = {}
            title = card.xpath('.//div[contains(@class, "content-text")]/h1/a/text()').get()
            if title:
                meta['title'] = self.cleanup_title(title)
            performers = [x.strip() for x in card.xpath('.//ul[@class="list-models"]/li/a/text()').getall() if x and x.strip()]
            if performers:
                meta['performers'] = performers
            # the still is lazy-loaded, so it sits in data-src rather than src
            image = card.xpath('.//figure//img/@data-src').get() or card.xpath('.//figure//img/@src').get()
            if image and image.strip():
                meta['image'] = self.format_link(response, image.strip())
                meta['image_blob'] = self.get_image_blob_from_link(meta['image'])
            yield scrapy.Request(url=self.format_link(response, link), callback=self.parse_scene, meta=meta)

    def get_site(self, response):
        return 'Private Classics'

    def get_parent(self, response):
        return 'Private'
