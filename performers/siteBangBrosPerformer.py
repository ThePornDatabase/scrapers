import string
from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteBangBrosPornstarSpider(BasePerformerScraper):
    selector_map = {
        'name': '',
        'image': "",
        'pagination': '/girls/new/%s',
        'external_id': ''
    }

    name = 'BangBrosPerformer'
    network = 'Bang Bros'

    start_urls = [
        'https://bangbros.com',
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[@class="echThumb"]')
        for performer in performers:
            item = PerformerItem()

            item['name'] = string.capwords(performer.xpath('./a/span[@class="thmb_ttl"]/text()').get().strip())
            image = performer.xpath('./a//span[@class="thmb_pic"]/img/@src|./a//span[@class="thmb_pic"]/img/@data-original')
            if image:
                item['image'] = self.format_link(response, image.get().strip())
            else:
                item['image'] = None
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['gender'] = "Female"
            item['url'] = self.format_link(response, performer.xpath('./a/@href').get().strip())
            item['network'] = 'Bang Bros'
            item['astrology'] = ''
            item['bio'] = ''
            item['birthday'] = ''
            item['birthplace'] = ''
            item['cupsize'] = ''
            item['ethnicity'] = ''
            item['eyecolor'] = ''
            item['fakeboobs'] = ''
            item['haircolor'] = ''
            item['height'] = ''
            item['measurements'] = ''
            item['nationality'] = ''
            item['piercings'] = ''
            item['tattoos'] = ''
            item['weight'] = ''

            yield item
