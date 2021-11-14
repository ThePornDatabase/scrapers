import scrapy
from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteZFilmzPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//h1/text()',
        'image': '',
        'haircolor': '//dt[contains(text(), "Hair")]/following-sibling::dd[1]/text()',
        'eyecolor': '//dt[contains(text(), "Eye")]/following-sibling::dd[1]/text()',
        'pagination': '/en/collections/page/%s?media=video',
        'external_id': r'models/(.*).html'
    }

    name = 'ZFilmzPerformer'
    network = "Z-Filmz"

    start_urls = [
        'https://www.z-filmz-originals.com/'
    ]

    def start_requests(self):
        url = "https://www.z-filmz-originals.com/en/models"
        yield scrapy.Request(url,
                             callback=self.parse,
                             meta={'page': self.page},
                             headers=self.headers,
                             cookies=self.cookies)

    def get_performers(self, response):
        performers = response.xpath('//div[contains(@class,"card")]/a')
        for performer in performers:
            image = performer.xpath('./img/@src').get()
            performer = performer.xpath('./@href').get()
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer, meta={'image': image})

    def get_gender(self, response):
        gender = response.xpath('//dt[contains(text(), "Sex")]/following-sibling::dd[1]/text()')
        if gender:
            gender = gender.get()
            if gender.lower() != "female" and gender.lower() != "male":
                gender = "Trans"
            return gender.title().strip()
