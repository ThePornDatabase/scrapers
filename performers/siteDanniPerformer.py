import re
from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteDanniPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/models/models_%s_d',
        'external_id': r'model/(.*)/'
    }

    name = 'DanniPerformer'

    start_urls = [
        'https://www.danni.com',
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[@class="danni-card"]')
        for performer in performers:
            item = PerformerItem()

            item['name'] = self.cleanup_title(performer.xpath('.//div[contains(@class, "card-name")]/a/text()').get())
            image = performer.xpath('.//img/@src0_2x|.//img/@src0_1x')
            if image:
                item['image'] = self.format_link(response, image.get())
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
            else:
                item['image'] = ""
                item['image_blob'] = ""
            if "?" in item['image']:
                item['image'] = re.search(r'(.*)\?', item['image']).group(1)
            item['bio'] = ''
            item['gender'] = 'Female'
            item['astrology'] = ''
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
            item['network'] = 'Sexual Prime'
            item['url'] = self.format_link(response, performer.xpath('./a[1]/@href').get())

            yield item
