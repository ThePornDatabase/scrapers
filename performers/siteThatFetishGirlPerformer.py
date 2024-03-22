from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteThatFetishGirlPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/models/models_%s_d.html?g=f',
        'external_id': r'model/(.*)/'
    }

    name = 'ThatFetishGirlPerformer'

    start_urls = [
        'https://thatfetishgirl.com',
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[contains(@class,"updateItem ")]')
        for performer in performers:
            item = PerformerItem()

            item['name'] = self.cleanup_title(performer.xpath('./p/a/text()').get())
            image = performer.xpath('.//img/@src0_3x|.//img/@src0_2x|.//img/@src0_1x')
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
            item['network'] = 'That Fetish Girl'
            item['url'] = self.format_link(response, performer.xpath('./div/a/@href').get())

            yield item
