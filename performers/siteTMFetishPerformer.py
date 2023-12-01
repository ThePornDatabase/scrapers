from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteTMFetishPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '',
        'image': '',
        'image_blob': True,

        'pagination': '/models/models_%s_d.html?g=f',
        'external_id': r'model/(.*)/'
    }

    name = 'TMFetishPerformer'
    network = 'TMFetish'

    start_urls = [
        'https://www.tmfetish.com',
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[@class="model"]')
        for performer in performers:
            item = PerformerItem()

            item['name'] = self.cleanup_title(performer.xpath('.//p/a/text()').get())
            image = performer.xpath('.//img/@src0_2x')
            if image:
                item['image'] = self.format_link(response, image.get())
            else:
                item['image'] = None
            item['image_blob'] = self.get_image_blob_from_link(item['image'])

            url = performer.xpath('./div[1]/a/@href').get()
            if url:
                item['url'] = url.strip()

            item['network'] = 'TMFetish'

            item['astrology'] = ''
            item['bio'] = ''
            item['birthday'] = ''
            item['birthplace'] = ''
            item['cupsize'] = ''
            item['ethnicity'] = ''
            item['eyecolor'] = ''
            item['fakeboobs'] = ''
            item['gender'] = "Female"
            item['haircolor'] = ''
            item['height'] = ''
            item['measurements'] = ''
            item['nationality'] = ''
            item['piercings'] = ''
            item['tattoos'] = ''
            item['weight'] = ''

            yield item
