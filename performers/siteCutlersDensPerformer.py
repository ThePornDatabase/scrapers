from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteCutlersDenPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': './/h3/a/text()',
        'image': './/div[@class="item"]//img/@src0_1x',
        'image_blob': True,

        'pagination': '/models//models_%s.html?g=',
        'external_id': r'model/(.*)/'
    }

    name = 'CutlersDenPerformer'
    network = 'Cutlers Den'

    start_urls = [
        'https://cutlersden.com',
    ]

    def get_gender(self, response):
        return 'Male'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="item"]')
        for performer in performers:
            item = PerformerItem()

            item['name'] = super().get_name(performer)
            image = performer.xpath('.//img/@src0_1x')
            if image:
                item['image'] = "https://cutlersden.com/" + image.get()
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
            else:
                item['image'] = ''
                item['image_blob'] = ''
            item['bio'] = ''
            item['gender'] = 'Male'
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
            item['network'] = 'Cutlers Den'
            item['url'] = performer.xpath('./div/a/@href').get()

            yield item
