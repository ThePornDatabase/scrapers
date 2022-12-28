from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteJapanBoyzPerformerPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '',
        'image': '',
        'image_blob': True,
        'bio': '',
        'gender': '',
        'astrology': '',
        'birthday': '',
        'birthplace': '',
        'cupsize': '',
        'ethnicity': '',
        'eyecolor': '',
        'fakeboobs': '',
        'haircolor': '',
        'height': '',
        'measurements': '',
        'nationality': '',
        'piercings': '',
        'tattoos': '',
        'weight': '',

        'pagination': '/models/models_%s.html?g=m',
        'external_id': r'model/(.*)/'
    }

    name = 'JapanBoyzPerformer'
    network = 'Japan Boyz'

    start_urls = [
        'https://www.japanboyz.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[contains(@class,"m-content")]')
        for performer in performers:
            item = PerformerItem()

            item['name'] = self.cleanup_title(performer.xpath('.//div[contains(@class, "m-name")]/a/text()').get())
            item['image'] = self.format_link(response, performer.xpath('.//div[contains(@class, "m-img")]/a/img/@src').get())
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['bio'] = ''
            item['gender'] = 'Male'
            item['astrology'] = ''
            item['birthday'] = ''
            item['birthplace'] = ''
            item['cupsize'] = ''
            item['ethnicity'] = 'Asian'
            item['eyecolor'] = ''
            item['fakeboobs'] = ''
            item['haircolor'] = ''
            item['height'] = ''
            item['measurements'] = ''
            item['nationality'] = ''
            item['piercings'] = ''
            item['tattoos'] = ''
            item['weight'] = ''
            item['network'] = 'Japan Boyz'
            item['url'] = self.format_link(response, performer.xpath('./div/a/@href').get())

            yield item
