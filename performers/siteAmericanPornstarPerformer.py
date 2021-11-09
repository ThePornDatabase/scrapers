import html

from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteAmericanPornstarSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[@class="update_details"]/a[1]/text()',
        'image': "//div[contains(@class,'image_area')]/img[@class='img-responsive']/@src",
        'pagination': '/models/models_%s_d.html',
        'external_id': 'girls/(.+)/?$'
    }

    name = 'AmericanPornstarPerformer'
    network = "American Pornstar"

    start_urls = [
        'http://american-pornstar.com',
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

            image = performer.xpath('.//img/@src0_3x|.//img/@src0_2x|.//img/@src0_1x').get()
            if image:
                item['image'] = "http://american-pornstar.com" + image.strip()
            else:
                item['image'] = None
            item['image_blob'] = None

            url = performer.xpath('./a[1]/@href').get()
            if url:
                item['url'] = url.strip()

            item['network'] = 'American Pornstar'

            item['astrology'] = ''
            item['bio'] = ''
            item['birthday'] = ''
            item['birthplace'] = ''
            item['cupsize'] = ''
            item['ethnicity'] = ''
            item['eyecolor'] = ''
            item['fakeboobs'] = ''
            item['gender'] = ''
            item['haircolor'] = ''
            item['height'] = ''
            item['measurements'] = ''
            item['nationality'] = ''
            item['piercings'] = ''
            item['tattoos'] = ''
            item['weight'] = ''

            yield item
