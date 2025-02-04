import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteDuskTVSpider(BaseSceneScraper):
    name = 'DuskTV'
    site = 'DuskTV'
    parent = 'DuskTV'
    network = 'DuskTV'

    start_urls = [
        'https://www.dusk-tv.com'
    ]

    selector_map = {
        'title': '//div[contains(@class, "dashboard")]//h4/text()',
        'description': '//div[contains(@class, "dashboard")]//p[contains(@class, "mt-2")]/text()',
        'date': '',
        'image': '//div[contains(@class, "dashboard")]//h4/following-sibling::a[1]/img/@src',
        'tags': '//div[contains(@class, "dashboard")]//strong[contains(text(), "Tags:")]/following-sibling::a/text()',
        'director': '//div[contains(@class, "dashboard")]//strong[contains(text(), "Directors:")]/following-sibling::text()[1]',
        'trailer': '',
        'type': 'Scene',
        'external_id': r'.*/(.*?)$',
        'pagination': '/videos/category/new-porn-for-women-videos?page=%s',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "bg-white")]/a[contains(@href, "/videos/") and not(contains(@href, "https"))]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_performers(self, response):
        performers = response.xpath('//div[contains(@class, "dashboard")]//strong[contains(text(), "Actors:")]/following-sibling::text()[1]')
        if performers:
            performers = performers.get()
            performers = performers.splitlines()
            performers = list(map(lambda x: string.capwords(x.strip()), performers))
            performers = list(filter(None, performers))
            return performers
        return []

    def get_duration(self, response):
        duration = response.xpath('//div[contains(@class, "dashboard")]//strong[contains(text(), "Duration:")]/following-sibling::text()[1]')
        if duration:
            duration = duration.get()
            duration = re.search(r'(\d+)', duration)
            if duration:
                duration = str(int(duration.group(1)) * 60)
                return duration
        return None
