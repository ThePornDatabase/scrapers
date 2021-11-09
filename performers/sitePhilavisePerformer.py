from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class PhilavisePerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/models/models_%s.html',
        'external_id': r'models/(.*)/'
    }

    name = 'PhilavisePerformer'

    start_urls = [
        'https://philavise.com',
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[@class="updateItem model"]')
        for performerrow in performers:

            item = PerformerItem()
            image = performerrow.xpath('./div/a/img/@src0_1x').get()
            if image:
                item['image'] = "https://www.philavise.com" + image.strip()
            else:
                image = None
            item['image_blob'] = None
            performer = performerrow.xpath('./p/a/text()').get()
            if performer:
                item['name'] = performer.strip()
            else:
                performer = False
            url = performerrow.xpath('./div/a/@href').get()
            if url:
                item['url'] = url.strip()
            else:
                url = False

            item['network'] = "Philavise"
            item['bio'] = ''
            item['gender'] = ''
            item['astrology'] = ''
            item['birthday'] = ''
            item['birthplace'] = ''
            item['ethnicity'] = ''
            item['nationality'] = ''
            item['haircolor'] = ''
            item['eyecolor'] = ''
            item['weight'] = ''
            item['height'] = ''
            item['measurements'] = ''
            item['tattoos'] = ''
            item['piercings'] = ''
            item['cupsize'] = ''
            item['fakeboobs'] = ''

            if performer and image and url:
                yield item
            item.clear()
