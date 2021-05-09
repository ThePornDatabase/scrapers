import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class PuffyPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '.title span::text',
        'image': "//div[contains(@class,'image_area')]/img[@class='img-responsive']/@src",
        'nationality': '//dt[contains(text(),"Nationality")]/following-sibling::dd[1]/text()',
        'cupsize': '//dt[contains(text(),"Breast")]/following-sibling::dd[1]/text()',
        'weight': '//dt[contains(text(),"Weight")]/following-sibling::dd[1]/text()',
        'height': '//dt[contains(text(),"Height")]/following-sibling::dd[1]/text()',
        'pagination': '/girls/page-%s/?tag=&sort=recent&pussy=&site=',
        'external_id': 'girls/(.+)/?$'
    }

    name = 'PuffyNetworkPerformer'
    network = "Puffy Network"
    parent = "Puffy Network"

    start_urls = [
        'https://www.puffynetwork.com/',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.css('#models a.img02::attr(href)').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer
            )

    def get_cupsize(self, response):
        if 'cupsize' in self.selector_map:
            cupsize = self.process_xpath(response, self.get_selector_map('cupsize')).get().strip().replace("-","")
            return cupsize
        return ''
