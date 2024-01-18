from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteBustyNetworkPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/pornstars/?page=%s',
        'external_id': r'model/(.*)/'
    }

    name = 'BustyNetworkPerformer'

    start_urls = [
        'http://bustynetwork.com',
    ]

    def get_performers(self, response):
        performers = response.xpath('//article')
        for performer in performers:
            item = PerformerItem()

            item['name'] = self.cleanup_title(performer.xpath('.//h3/text()').get())
            image = performer.xpath('.//img/@src')
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
            item['network'] = 'Busty Network'
            item['url'] = self.format_link(response, performer.xpath('./a[1]/@href').get())

            yield item
