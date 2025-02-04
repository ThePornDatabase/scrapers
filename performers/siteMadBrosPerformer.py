from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteMadBrosPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/my-friends/page/%s/',
        'external_id': r'model/(.*)/'
    }

    name = 'MadBrosPerformer'

    start_urls = [
        'https://madbrosx.com',
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[@class="mx-friends-item"]')
        for performer in performers:
            item = PerformerItem()

            item['name'] = self.cleanup_title(performer.xpath('.//div[contains(@class, "mx-heading-h4")]/a/text()').get())
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
            item['network'] = 'MadBros'
            item['url'] = self.format_link(response, performer.xpath('.//div[contains(@class, "mx-heading-h4")]/a/@href').get())

            yield item
