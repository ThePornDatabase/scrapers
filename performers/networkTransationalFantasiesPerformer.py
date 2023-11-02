import re
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class NetworkTransationalFantasiesPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//h1/text()',
        'cupsize': '//li[contains(text(), "Meas")]/text()',
        're_cupsize': r': (\d{1,2}\w+)-',
        'ethnicity': '//li[contains(text(), "Ethnicity")]/text()',
        're_ethnicity': r': (.*)',
        'haircolor': '//li[contains(text(), "Hair")]/text()',
        're_haircolor': r': (.*)',
        'height': '//li[contains(text(), "Height")]/text()',
        're_height': r': (.*)',
        'measurements': '//li[contains(text(), "Meas")]/text()',
        're_measurements': r': (.*)',
        'weight': '//li[contains(text(), "Weight")]/text()',
        're_weight': r': (.*)',

        'pagination': '/watch-transational-fantasies-free-trailers.html?page=%s&hybridview=member',
        'external_id': r'model/(.*)/'
    }

    custom_scraper_settings = {
        'AUTOTHROTTLE_ENABLED': True,
        'USE_PROXY': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 60,
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 2,
    }

    name = 'TransationalFantasiesPerformer'
    network = 'Transational Fantasies'

    start_urls = [
        'https://www.transationalfantasies.com',
    ]

    def parse(self, response, **kwargs):
        scenes = self.get_scenes(response)
        count = 0
        for scene in scenes:
            count += 1
            yield scene

        if count:
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                meta = response.meta
                meta['page'] = meta['page'] + 1
                print('NEXT PAGE: ' + str(meta['page']))
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page']), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@id, "item_")]/div/a/@href').getall()
        for scene in scenes:
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.get_performers, meta=meta)

    def get_performers(self, response):
        meta = response.meta
        performers = response.xpath('//div[@class="video-performer"]')
        for performer in performers:
            image = performer.xpath('./a/img/@data-bgsrc')
            if image:
                meta['image'] = self.format_link(response, image.get())
                meta['image_blob'] = self.get_image_blob_from_link(meta['image'])
            performer = performer.xpath('./a/@href').get()
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, meta=meta)

    def get_gender(self, response):
        return 'Transgender Female'

    def get_weight(self, response):
        weight = super().get_weight(response)
        if weight:
            weight = re.search(r'(\d+)', weight)
            if weight:
                weight = weight.group(1)
                weight = str(int(int(weight) * .453592)) + "kg"
        return weight

    def get_height(self, response):
        height = super().get_height(response)
        if height:
            height = re.search(r'(\d+).*(\d+)', height)
            if height:
                feet = int(height.group(1))
                inches = int(height.group(2))
                feet = int(feet) * 12
                height = str(int((feet + inches) * 2.54)) + "cm"
        return height
