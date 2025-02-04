from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteExposedLatinasPerformerPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/tour/models/models_%s.html',
        'external_id': r'model/(.*)/'
    }

    name = 'ExposedLatinasPerformer'

    start_urls = [
        'https://sexmex.xxx',
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[contains(@class, "col-xs-16")]')
        for performer in performers:
            item = PerformerItem()

            item['name'] = self.cleanup_title(performer.xpath('.//h5//text()').get())
            image = performer.xpath('./div[1]/a/img/@src')
            if image:
                item['image'] = self.format_link(response, image.get())
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
            else:
                item['image'] = ""
                item['image_blob'] = ""
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
            item['network'] = 'SexMex'
            item['url'] = self.format_link(response, performer.xpath('./div[1]/a/@href').get())

            yield item
