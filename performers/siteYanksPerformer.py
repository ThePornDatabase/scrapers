import scrapy
from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteYanksPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[@class="profile_details"]/h2/text()',
        'image': '//div[@class="model_profile"]//img/@src',
        'height': '//span[contains(text(),"Height")]/following-sibling::text()[1]',
        'birthplace': '//span[contains(text(),"Hometown")]/following-sibling::text()[1]',
        'bio': '//p[@class="model_info"]/text()',
        'pagination': '/categories/Models/%s/latest/',
        'external_id': r'models\/(.*).html'
    }

    name = 'YanksPerformer'
    network = 'Yanks'

    start_urls = [
        'https://www.yanks.com'
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[@class="model"]')
        for performer in performers:
            performer_name = performer.xpath('.//h3/a/text()')
            if performer_name:
                performer_name = performer_name.get()
            else:
                performer_name = False
            performer = performer.xpath('./div/a/@href').get()
            if performer and "&" not in performer_name:
                yield scrapy.Request(
                    url=self.format_link(response, performer),
                    callback=self.parse_performer
                )

    def get_gender(self, response):
        return "Female"
