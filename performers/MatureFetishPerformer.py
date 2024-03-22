from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteMatureFetishPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/en/models/%s?sort=&q=&sex=female',
        'external_id': r'model/(.*)/'
    }

    name = 'MatureFetishPerformer'

    start_urls = [
        'https://maturefetish.com',
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[@class="grid-tile-model"]')
        for performer in performers:
            item = PerformerItem()

            item['name'] = self.cleanup_title(performer.xpath('./div/a/text()').get())
            image = performer.xpath('.//img/@data-src')
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
            item['network'] = 'Mature NL'
            item['url'] = self.format_link(response, performer.xpath('./a/@href').get())

            yield item
