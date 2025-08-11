import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteThrillmongerSpider(BaseSceneScraper):
    name = 'Thrillmonger'
    network = 'Thrillmonger'
    parent = 'Thrillmonger'
    site = 'Thrillmonger'

    start_urls = [
        'https://www.thrillmonger.com',
    ]

    selector_map = {
        'title': '//div[@class="update_block_info"]/span[contains(@class, "update_title")]/text()',
        'description': '//div[@class="update_block_info"]/span[contains(@class, "latest_update_description")]/text()',
        'date': '//div[@class="update_block_info"]/span[contains(@class, "availdate")]/text()[contains(., "/")][1]',
        'performers': '//div[@class="update_block_info"]/span[contains(@class, "tour_update_models")]/a/text()',
        'tags': '//div[@class="update_block_info"]/span[contains(@class, "update_tags")]/a/text()',
        'external_id': r'',
        'pagination': '/categories/movies_%s.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="updateItem"]')
        for scene in scenes:
            image = scene.xpath('.//video/@poster_4x')
            if not image:
                image = scene.xpath('.//video/@poster_3x')
                if not image:
                    image = scene.xpath('.//video/@poster_2x')
            if image:
                meta['image'] = self.format_link(response, image.get())
                meta['image_blob'] = self.get_image_blob_from_link(meta['image'])

            trailer = scene.xpath('.//video/source/@src')
            if trailer:
                meta['trailer'] = self.format_link(response, trailer.get())

            sceneid = scene.xpath('.//video/following-sibling::comment()[contains(., "set-target-")][1]')
            if sceneid:
                sceneid = sceneid.get()
                meta['id'] = re.search(r'set-target-(\d+)', sceneid).group(1)

            scene = scene.xpath('./a[1]/@href').get()

            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_duration(self, response):
        duration = response.xpath('//div[@class="update_counts_preview_table"]/text()[contains(., "min")]')
        if duration:
            duration = duration.get().replace("&nbsp;", "")
            duration = re.sub(r'[^a-z0-9]+', '', duration.lower())
            duration = re.search(r'(\d+)min', duration)
            if duration:
                duration = duration.group(1)
                return str(int(duration) * 60)
        return None

    def get_performers_data(self, response):
        performers = super().get_performers(response)
        performers_data = []
        if len(performers):
            for performer in performers:
                perf = {}
                perf['name'] = performer
                perf['extra'] = {}
                perf['extra']['gender'] = "Female"
                perf['network'] = "Thrillmonger"
                perf['site'] = "Thrillmonger"
                performers_data.append(perf)
        return performers_data
