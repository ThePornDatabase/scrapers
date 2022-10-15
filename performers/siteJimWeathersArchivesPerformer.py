from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteJimWeathersArchivesPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/store/models/models_%s_d.html',
        'external_id': r'model/(.*)/'
    }

    name = 'JimWeathersArchivesPerformer'
    network = 'Jim Weathers Archives'

    start_urls = [
        'https://www.jimweathersarchives.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="update_details"]')
        for performer in performers:
            item = PerformerItem()

            item['name'] = performer.xpath('./a[1]/text()').get()
            image = performer.xpath('.//img/@src0_2x')
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
            item['network'] = 'Jim Weathers Archives'
            item['url'] = performer.xpath('./a[1]/@href').get()

            yield item
