import html

from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class NetworkOlderWomanFunPornstarSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[@class="update_details"]/a[1]/text()',
        'image': "//div[contains(@class,'image_area')]/img[@class='img-responsive']/@src",
        'pagination': '/tour2/models/models_%s_d.html',
        'external_id': 'girls/(.+)/?$'
    }

    name = 'OlderWomanFunPerformer'
    network = "Older Woman Fun"

    start_urls = [
        'https://www.olderwomanfun.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="update_details"]')
        for performer in performers:
            item = PerformerItem()

            name = performer.xpath('./a[1]/text()').get()
            if name:
                item['name'] = html.unescape(name.strip().title())

            image = performer.xpath('.//img/@src0_2x').get()
            if image:
                item['image'] = self.format_link(response, image.strip())
            else:
                item['image'] = None
            item['image_blob'] = None

            item['url'] = performer.xpath('./a[1]/@href').get().strip()

            item['network'] = 'Older Woman Fun'

            item['astrology'] = ''
            item['bio'] = ''
            item['birthday'] = ''
            item['birthplace'] = ''
            item['cupsize'] = ''
            item['ethnicity'] = ''
            item['eyecolor'] = ''
            item['fakeboobs'] = ''
            item['gender'] = 'Female'
            item['haircolor'] = ''
            item['height'] = ''
            item['measurements'] = ''
            item['nationality'] = ''
            item['piercings'] = ''
            item['tattoos'] = ''
            item['weight'] = ''

            yield item
