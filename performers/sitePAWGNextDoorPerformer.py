from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SitePAWGNextDoorPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/tour/models/models_%s_d.html',
        'external_id': r'model/(.*)/'
    }

    name = 'PAWGNextDoorPerformer'

    start_urls = [
        'https://www.pawgnextdoor.com',
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[@class="model"]')
        for performer in performers:
            item = PerformerItem()

            item['name'] = self.cleanup_title(performer.xpath('./p/a/text()').get())
            image = performer.xpath('.//img/@src0_2x')
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
            item['network'] = 'PAWG Next Door'
            item['url'] = self.format_link(response, performer.xpath('./div[1]/a/@href').get())

            yield item
