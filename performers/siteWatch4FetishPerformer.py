import scrapy
from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteWatch4FetishPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[@class="channal-details-info"]/h3/text()',
        'image': '//div[@class="channal-image"]/img/@src0_1x',
        'image_blob': True,
        'height': '//td[contains(text(), "Height:")]/following-sibling::td/text()',
        'nationality': '//td[contains(text(), "Country:")]/following-sibling::td/text()',
        'bio': '//strong[contains(text(), "About me")]/following-sibling::text()',
        'pagination': '/models/models_%s.html',
        'external_id': r'models/(.*)/'
    }

    name = 'Watch4FetishPerformer'
    network = "Watch4Fetish"

    start_urls = [
        'https://www.watch4fetish.com',
    ]

    def get_performers(self, response):
        performers = response.xpath('//a[@class="model_thumb"]/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer
            )

    def get_gender(self, response):
        return "Female"
