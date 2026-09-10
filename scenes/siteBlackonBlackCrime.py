import re
import string

import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteBlackonBlackCrimeSpider(BaseSceneScraper):
    name = 'BlackonBlackCrime'
    network = 'D&E Media'
    parent = 'D&E Media'
    site = 'Black on Black Crime'

    start_urls = [
        'https://tour5m.blackonblackcrime.com',
    ]

    # The tour was rebuilt on the Ghetto Doorway template:
    # /tour/categories/movies/<page>/latest/ now redirects to the 404 page, the
    # cards are div.item-update rather than div.item-video, and the date and
    # runtime moved onto the scene page's "Added: ..." row.  The h1 is rendered
    # twice -- site name then scene title -- so the last one is taken.
    selector_map = {
        'description': '//meta[@name="description"]/@content',
        'date': '//div[contains(@class, "update-info-row")][contains(., "Added:")]/text()',
        # "Added:" itself sits in a <strong>, so it is not in the text node.
        're_date': r'(\w+ \d{1,2}, \d{4})',
        'date_formats': ['%B %d, %Y'],
        'image': '//div[@class="player-thumb"]/img/@src0_2x',
        'duration': '//div[contains(@class, "update-info-row")][contains(., "Runtime:")]/text()',
        're_duration': r'Runtime:\s*((?:\d{1,2}:)?\d{1,2}:\d{2})',
        'performers': '',
        'tags': '',
        'trailer': '',
        'external_id': r'/trailers/(.*)\.html',
        'pagination': '/tour/categories/movies_%s_d.html',
    }

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        scenes = response.xpath('//div[contains(@class, "item-update ")]//div[@class="item-title"]/a/@href').getall()
        for scene in dict.fromkeys(scenes):
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_title(self, response):
        # The page renders the site name in an h1 before the scene's own h1.
        titles = response.xpath('//h1/text()').getall()
        if titles:
            return self.cleanup_title(titles[-1])
        return ''

    def get_tags(self, response):
        tags = response.xpath('//meta[@name="keywords"]/@content').get()
        if not tags:
            return []
        tags = [string.capwords(tag.strip()) for tag in tags.split(",") if tag.strip()]
        title = self.get_title(response)
        for drop in ("Black On Black Crime", title):
            if drop in tags:
                tags.remove(drop)
        return tags

    def get_performers(self, response):
        # The tour names the scene after its performer and lists nothing else.
        title = self.get_title(response)
        return [title] if title else []
