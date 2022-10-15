from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteOldjePerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/models/%s',
        'external_id': r'model/(.*)/'
    }

    name = 'OldjePerformer'
    network = 'Oldje'

    start_urls = [
        'https://www.oldje.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="model_photo left"]')
        for performer in performers:
            item = PerformerItem()

            item['name'] = performer.xpath('.//div[contains(@class, "model_name")]/text()').get()
            image = performer.xpath('./a/img/@src')
            if image:
                image = image.get()
                item['image'] = self.format_link(response, image)
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
            else:
                item['image'] = ''
                item['image_blob'] = ''
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
            item['network'] = 'Oldje'
            item['url'] = performer.xpath('./a[1]/@href').get()

            yield item
