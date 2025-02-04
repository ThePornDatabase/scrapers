from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteSexUnderwaterPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/models/models_%s.html',
        'external_id': r'model/(.*)/'
    }

    name = 'SexUnderwaterPerformer'

    start_urls = [
        'https://sexunderwater.com',
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[@class="model"]')
        for performer in performers:
            item = PerformerItem()

            name = performer.xpath('.//p/a[contains(@href, "/models/")]/text()').getall()
            name = "".join(name).replace("\n", "").replace("\r", "").replace("\t", "").strip()
            item['name'] = self.cleanup_title(name)
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
            item['network'] = 'Sex Underwater'
            item['url'] = self.format_link(response, performer.xpath('./div[1]/a/@href').get())

            yield item
