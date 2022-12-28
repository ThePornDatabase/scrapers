from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteTGirlsHookupsPerformerSpider(BasePerformerScraper):
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

        'pagination': '/tour/models/%s/latest/?g=',
        'external_id': r'model/(.*)/'
    }

    name = 'TgirlsHookupPerformer'
    network = 'Tgirls Hookup'

    start_urls = [
        'https://www.tgirlshookup.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[contains(@class, "modelphoto")]/..')
        for performer in performers:
            item = PerformerItem()

            item['name'] = self.cleanup_title(performer.xpath('./h4/a/text()').get())
            item['image'] = self.format_link(response, performer.xpath('./div/a/img/@src0_2x').get())
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['bio'] = ''
            item['gender'] = 'Trans'
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
            item['network'] = 'Tgirls Hookup'
            item['url'] = self.format_link(response, performer.xpath('./h4/a/@href').get())

            yield item
