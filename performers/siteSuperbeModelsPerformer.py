import scrapy
from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteSuperbeModelsPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[contains(@class,"section-boxed")]//h1/text()',
        'image': '//img[contains(@class, "poster-thumb")]/@src',
        'birthplace': '//div[contains(@class, "api-list")]/div[contains(text(), "Birth Place")]/span/text()',
        'birthday': '//div[contains(@class, "api-list")]/div[contains(text(), "Birth Date")]/span/text()',
        'nationality': '//div[contains(@class, "api-list")]/div[contains(text(), "Nationality")]/span/text()',
        'fakeboobs': '//div[contains(@class, "api-list")]/div[contains(text(), "Tits Type")]/span/text()',
        'bio': '//div[contains(@class,"api-description")]//text()[not(contains(.,"Watch all scenes"))]',
        'pagination': '/pornstars/sex/girls.en.html?order=activity&page=%s',
        'external_id': r'models\/(.*).html'
    }

    name = 'SuperbeModelsPerformer'
    network = "Superbe Models"

    start_urls = [
        'https://superbe.com'
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[@class="global-actor-card"]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer)

    def get_gender(self, response):
        return "Female"

    def get_fakeboobs(self, response):
        fakeboobs = response.xpath(self.get_selector_map('fakeboobs'))
        if fakeboobs:
            fakeboobs = fakeboobs.get().lower()
            if "natural" in fakeboobs:
                return "No"
            if "enhanced" in fakeboobs:
                return "Yes"
        return ''
