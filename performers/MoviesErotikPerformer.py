import re
import json
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class MoviesErotikPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '',
        'image': '',
        'image_blob': True,
        'bio': '',
        'gender': '',
        'astrology': '',
        'birthday': '',
        'birthplace': '',
        'cupsize': '//ul[@class="star-characteristics"]//span[contains(text(), "Breast cup")]/../following-sibling::div[1]/a/text()',
        'ethnicity': '',
        'eyecolor': '//ul[@class="star-characteristics"]//span[contains(text(), "Eye")]/../following-sibling::div[1]/a/text()',
        'fakeboobs': '//ul[@class="star-characteristics"]//span[contains(text(), "Breasts")]/../following-sibling::div[1]/a/text()',
        'haircolor': '//ul[@class="star-characteristics"]//span[contains(text(), "Hair")]/../following-sibling::div[1]/a/text()',
        'height': '//ul[@class="star-characteristics"]//span[contains(text(), "Height")]/../following-sibling::div[1]/span/text()',
        'measurements': '',
        'nationality': '//ul[@class="star-characteristics"]//span[contains(text(), "Country")]/../following-sibling::div[1]/a/text()',
        'piercings': '',
        'tattoos': '',
        'weight': '//ul[@class="star-characteristics"]//span[contains(text(), "Weight")]/../following-sibling::div[1]/span/text()',

        'pagination': '/vod/search/performers?filter[pictures]=0&itemsPerPage=48&page=%s&source=performersoverview',
        'external_id': r'model/(.*)/'
    }

    name = 'MoviesErotikPerformer'
    network = 'Erotik'

    start_urls = [
        'https://api.erotik.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        meta = response.meta
        jsondata = json.loads(response.text)
        for performer in jsondata['performers']:
            meta['name'] = performer['name']['en']
            meta['image'] = performer['src']
            meta['url'] = "https://en.erotik.com" + performer['url']['en']
            yield scrapy.Request(meta['url'], callback=self.parse_performer, cookies=self.cookies, headers=self.headers, meta=meta)

    def get_height(self, response):
        old_height = super().get_height(response)
        height = old_height.lower()
        if "cm" in height:
            height = height.replace(" ", "")
            height = re.search(r'(\d+cm)', height)
            if height:
                return height.group(1)
        return old_height

    def get_weight(self, response):
        old_weight = super().get_weight(response)
        weight = old_weight.lower()
        if "kg" in weight:
            weight = weight.replace(" ", "")
            weight = re.search(r'(\d+kg)', weight)
            if weight:
                return weight.group(1)
        return old_weight
