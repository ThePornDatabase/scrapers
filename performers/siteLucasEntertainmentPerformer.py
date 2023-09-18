import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteLucasEntertainmentPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//h2[@class="visible-xs"]/text()',
        'image': '//img[contains(@class,"lazy main-photo")]/@data-original',
        'image_blob': True,
        'bio': '//p[@class="plain-link"]/following-sibling::p[1]/text()',
        'gender': '',
        'astrology': '',
        'birthday': '',
        'birthplace': '',
        'cupsize': '',
        'ethnicity': '',
        'eyecolor': '',
        'fakeboobs': '',
        'haircolor': '',
        'height': '',
        'measurements': '',
        'nationality': '',
        'piercings': '',
        'tattoos': '',
        'weight': '',

        'pagination': '/models/page/%s/',
        'external_id': r'model/(.*)/'
    }

    name = 'LucasEntertainmentPerformer'
    network = 'Lucas Entertainment'

    start_urls = [
        'https://www.lucasentertainment.com',
    ]

    def get_gender(self, response):
        return 'Male'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="scene-item"]/a[1]/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, cookies=self.cookies, headers=self.headers)
