from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteSweetFemondomPerformerSpider(BasePerformerScraper):
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

        'pagination': '/tour/models/%s/latest/?g=f',
        'external_id': r'model/(.*)/'
    }

    name = 'SweetFemdomFemalePerformer'
    network = 'Sweet Femdom'

    start_urls = [
        'https://sweetfemdom.com',
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[@class="item-portrait"]')
        for performer in performers:
            item = PerformerItem()

            item['name'] = self.cleanup_title(performer.xpath('.//h4/a/text()').get())
            item['image'] = self.format_link(response, performer.xpath('./a/img/@src0_1x').get())
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
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
            item['network'] = 'Sweet Femdom'
            item['url'] = self.format_link(response, performer.xpath('./a/@href').get())

            yield item
