import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteSquirtStudiosSpider(BaseSceneScraper):
    name = 'SquirtStudios'
    network = 'SquirtStudios'
    parent = 'SquirtStudios'
    site = 'SquirtStudios'

    start_urls = [
        'https://www.squirtstudios.xxx',
    ]

    selector_map = {
        'title': '//div[@class="movie-player"]/h2[contains(@class, "text-left")]/text()',
        'description': '//div[contains(@class, "description")]/text()[1]',
        'date': '//div[contains(@class, "description")]/text()[contains(., "ate:")]',
        're_date': r'(\d{1,2}.*?\d{4})',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[contains(@class, "row model-list")]//div[contains(@class, "p-title")]/a/text()',
        'tags': '//div[contains(@class, "v-tags")]/a/text()',
        'duration': '//div[contains(@class, "movie-player")]//i[contains(@class, "fa-clock")]/following-sibling::text()',
        'external_id': r'.*/(.*?)_vid',
        'pagination': '/categories/scenes_%s_d.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "v-img")]/a[1]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_performers_data(self, response):
        performers = super().get_performers(response)
        perf_data = []
        perf_data_items = response.xpath('//div[contains(@class, "row model-list")]//div[contains(@class, "v-img")]')
        for performer in performers:
            for perf_entry in perf_data_items:
                perf_url = perf_entry.xpath('./a/@href').get().lower()
                perf_lower = performer.lower().replace(" ", "-")
                perf_lower_bare = re.sub(r'[^a-z]+', '', perf_lower)
                if perf_lower in perf_url or perf_lower_bare in perf_url:
                    perf = {}
                    perf['name'] = performer
                    perf['extra'] = {}
                    perf['extra']['gender'] = "Male"
                    perf['network'] = "SquirtStudios"
                    perf['site'] = "SquirtStudios"

                    image = perf_entry.xpath('.//img/@src').get()
                    perf['image'] = image
                    perf['image_blob'] = self.get_image_blob_from_link(perf['image'])
                    perf_data.append(perf)
        return perf_data

    def get_tags(self, response):
        tags = super().get_tags(response)
        tags2 = []
        for tag in tags:
            tag = tag.replace("#", "")
            tag = string.capwords(tag)
            tags2.append(tag)
        tags2.append("Gay")
        return tags2
