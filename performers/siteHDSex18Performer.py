import scrapy
from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteHDSex18PerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[@class="main-content"]//div[@class="model-right"]//h2[@class="title"]/text()',
        'image': '//div[@class="main-content"]//div[@class="model-left"]//img/@src',
        'bio': '',
        'gender': '',
        'astrology': '',
        'birthday': '',
        'birthplace': '',
        'cupsize': '',
        'ethnicity': '',
        'eyecolor': '//span[@class="label fix-w" and contains(text(), "Eyes")]/following-sibling::a/text()',
        'fakeboobs': '',
        'haircolor': '//span[@class="label fix-w" and contains(text(), "Hair")]/following-sibling::a/text()',
        'height': '',
        'measurements': '',
        'nationality': '',
        'piercings': '',
        'tattoos': '',
        'weight': '',

        'pagination': '/models/%s/?sort_by=model_id&gender_id=0',
        'external_id': r'model/(.*)/'
    }

    name = 'HDSex18Performer'
    network = 'HDSex18'

    start_urls = [
        'https://hdsex18.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="thumb-model"]/div/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, cookies=self.cookies, headers=self.headers)
