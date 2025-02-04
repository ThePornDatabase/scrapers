from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteExpliciteArtPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/visitor/pornstars/page%s.html',
        'external_id': r'model/(.*)/'
    }

    name = 'ExpliciteArtPerformer'

    start_urls = [
        'https://www.explicite-art.com',
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[contains(@class, "pornstar")]')
        for performer in performers:
            item = PerformerItem()

            item['name'] = self.cleanup_title(performer.xpath('./div/text()').get())
            image = performer.xpath('.//img/@src')
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
            item['network'] = 'Explicite-Art'
            item['url'] = self.format_link(response, performer.xpath('.//a/@href').get())

            yield item
