import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkRichardXXXSpider(BaseSceneScraper):
    name = 'RichardXXX'
    network = 'Richard XXX'

    start_urls = [
        'https://www.richard.xxx',
    ]

    selector_map = {
        'description': '//span[contains(text(), "Synopsis")]/following-sibling::text()',
        'image': '//div[@class="overlays"]/img/@src',
        'date': '//script[contains(@type, "json")]/text()',
        're_date': r'datePublished.*?(\d{4}-\d{2}-\d{2})',
        'tags': '//p[@class="scene-categories"]/a/text()',
        'external_id': r'-(\d+)',
        'pagination': '/new-porn-videos?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "col-12") and contains(@class, "scene")]')
        for scene in scenes:

            site = scene.xpath('.//span[@class="scene-title"]/text()')
            if site:
                site = site.get()
                meta['site'] = site
                meta['parent'] = site

            duration = scene.xpath('.//span[@class="duration"]/text()')
            if duration:
                duration = duration.get()
                duration = re.search(r'(\d+) min', duration).group(1)
                meta['duration'] = str(int(duration) * 60)

            performers = scene.xpath('.//span[@class="scene-actors"]/a/text()')
            if performers:
                performers = performers.getall()
                meta['performers'] = performers
                meta['title'] = (", ").join(performers) + " in " + meta['site']

            scene = self.format_link(response, scene.xpath('./div/a/@href').get())

            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
