import string
import scrapy
from tpdb.BasePerformerScraper import BasePerformerScraper


class SitePJGirlsPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[contains(@class, "model")]/h1/text()',
        'image': '//div[contains(@class, "model")]/div/img/@src',
        'eyecolor': '//div[@class="intro"]/div/strong[contains(text(), "EYES")]/following-sibling::text()',
        'haircolor': '//div[@class="intro"]/div/strong[contains(text(), "HAIR")]/following-sibling::text()',
        'height': '//div[@class="info"]/div/strong[contains(text(), "HEIGHT")]/following-sibling::text()[1]',
        'weight': '//div[@class="info"]/div/strong[contains(text(), "WEIGHT")]/following-sibling::text()[1]',
        'pagination': '/jav-models/page/%s',
        'external_id': r'model\/(.*)/'
    }

    name = 'PJGirlsPerformer'
    network = 'PJGirls'

    max_pages = 1

    start_urls = [
        'https://www.pjgirls.com/en/models/',
    ]

    def start_requests(self):
        url = "https://www.pjgirls.com/en/models/"
        yield scrapy.Request(url, callback=self.get_performers,
                             meta={'page': self.page},
                             headers=self.headers,
                             cookies=self.cookies)

    def get_performers(self, response):
        performers = response.xpath('//div[contains(@class, "thumb")]/h2/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer
            )

    def get_name(self, response):
        name = self.process_xpath(response, self.get_selector_map('name')).getall()
        name = " ".join(name)
        return string.capwords(name.strip())

    def get_gender(self, response):
        return 'Female'

    def get_nationality(self, response):
        return "Czech"
