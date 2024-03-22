from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteMilfCandyPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/models/models_%s_d.html?g=f',
        'external_id': r'model/(.*)/'
    }

    name = 'MilfCandyPerformer'

    start_urls = [
        'https://tour.milfcandy.com',
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[contains(@class,"item-portrait")]')
        for performer in performers:
            item = PerformerItem()

            item['name'] = self.cleanup_title(performer.xpath('./div[1]/a/span/text()').get())
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
            item['network'] = 'Milf Candy'
            item['url'] = self.format_link(response, performer.xpath('./div[@class="timeDate"]/a/@href').get())

            yield item
