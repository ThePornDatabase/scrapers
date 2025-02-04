from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteHammerBoysPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/models/models_%s.html',
        'external_id': r'model/(.*)/'
    }

    name = 'HammerBoysPerformer'

    start_urls = [
        'https://hammerboys.tv',
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[contains(@class, "updateItem")]')
        for performer in performers:
            item = PerformerItem()

            item['name'] = self.cleanup_title(performer.xpath('.//p/a/text()').get())
            image = performer.xpath('.//img/@src0')
            if image:
                item['image'] = self.format_link(response, image.get())
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
            else:
                item['image'] = ""
                item['image_blob'] = ""
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
            item['network'] = 'HammerBoys'
            item['url'] = self.format_link(response, performer.xpath('.//p/a/@href').get())

            yield item
