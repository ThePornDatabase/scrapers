import html

from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteBondageCafeSpider(BasePerformerScraper):
    selector_map = {
        'name': '',
        'image': "",
        'pagination': '/models/models_%s.html',
        'external_id': 'girls/(.+)/?$'
    }

    name = 'BondageCafePerformer'

    start_urls = [
        'https://www.bondagecafe.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="model"]')
        for performer in performers:
            item = PerformerItem()

            name = performer.xpath('./p/a/text()').get()
            if name:
                item['name'] = html.unescape(name.strip().title())

            image = performer.xpath('.//img/@src0_3x|.//img/@src0_2x|.//img/@src0_1x').get()
            if image:
                item['image'] = "http://www.bondagecafe.com" + image.strip()
            else:
                item['image'] = None
            item['image_blob'] = None

            url = performer.xpath('./p/a/@href').get()
            if url:
                item['url'] = url.strip()

            item['network'] = 'Bondage Cafe'

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
