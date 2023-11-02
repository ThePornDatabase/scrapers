from tpdb.items import PerformerItem
from tpdb.BasePerformerScraper import BasePerformerScraper


class NetworkPureEthnicPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/tour/models/models_%s.html',
        'external_id': r'model/(.*)/'
    }

    name = 'PureEthnicPerformer'
    network = 'Pure Ethnic'

    start_urls = [
        'https://www.pureethnic.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="update_details"]')
        for performer in performers:
            item = PerformerItem()
            item['name'] = self.cleanup_title(performer.xpath('./a[1]/text()').get())
            item['url'] = self.format_link(response, performer.xpath('./a[1]/@href').get())
            item['gender'] = 'Female'
            image = performer.xpath('.//img/@src0_2x')
            if image:
                item['image'] = self.format_link(response, image.get())
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
            else:
                item['image'] = ''
                item['image_blob'] = ''
            item['network'] = 'Pure Ethnic'
            item['bio'] = ''
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
            yield item
