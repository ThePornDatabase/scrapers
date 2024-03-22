import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteDownblouseWowPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[contains(@class,"modelinfo")]/p/strong[contains(text(), "Name")]/following-sibling::text()[1]',
        'image': '//div[contains(@class,"modelpic")]/img/@src',
        'image_blob': True,
        'cupsize': '//div[contains(@class,"modelinfo")]/p/strong[contains(text(), "Bra")]/following-sibling::text()[1]',

        'pagination': '/show.php?a=147_%s',
        'external_id': r'model/(.*)/'
    }

    name = 'DownblouseWowPerformer'
    network = 'Downblouse Wow'

    start_urls = [
        'https://downblousewow.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="itemminfo"]/p/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, cookies=self.cookies, headers=self.headers)
