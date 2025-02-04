import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteSpider(BaseSceneScraper):
    name = 'WhoreHimOut'
    site = 'WhoreHimOut'
    parent = 'WhoreHimOut'
    network = 'WhoreHimOut'

    cookies = {"warning": "ok"}

    start_urls = [
        'https://www.whorehimout.com'
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//div[@class="row"]/div[contains(@style, "x-large")]/p//text()',
        'date': '//strong[contains(text(), "Posted")]/following-sibling::text()',
        'date_formats': ['%a, %d %B %Y'],
        'image': '',
        'performers': '//strong[contains(text(), "Model")]/following-sibling::a//text()',
        'trailer': '',
        'type': 'Scene',
        'external_id': r'mb=(.*)',
        'pagination': '/index.php?p=%s',
    }

    def get_next_page_url(self, base, page):
        page = int(page) - 1
        page = str(page * 8)
        return self.format_url(base, self.get_selector_map('pagination') % page)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "scenes-grid")]//div[@class="item"]/div[1]/a')
        for scene in scenes:
            image = scene.xpath('./img/@data-async-load')
            if image:
                image = image.get()
                meta['image'] = image
                meta['image_blob'] = self.get_image_blob_from_link(image)

            scene = scene.xpath('./@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_performers_data(self, response):
        performers = self.get_performers(response)
        performers_data = []
        if len(performers):
            for performer in performers:
                perf = {}
                perf['name'] = performer
                perf['extra'] = {}
                perf['extra']['gender'] = "Male"
                perf['network'] = "WhoreHimOut"
                perf['site'] = "WhoreHimOut"
                performers_data.append(perf)
        return performers_data

    def get_tags(self, response):
        return ['Gay']
