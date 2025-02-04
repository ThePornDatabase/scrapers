from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class NetworkCarnalPlusPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/models?page=%s',
        'external_id': r'model/(.*)/'
    }

    name = 'CarnalPlusPerformer'

    start_urls = [
        'https://www.carnalplus.com',
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[@class="grid-item-model"]')
        for performer in performers:
            item = PerformerItem()

            item['name'] = self.cleanup_title(performer.xpath('.//h4/text()').get())
            image = performer.xpath('.//img[contains(@class, "stdimage")]/@src')
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
            item['network'] = 'CarnalPlus'
            perflink = performer.xpath('./div/a/@href')
            if perflink:
                item['url'] = self.format_link(response, perflink.get())
                yield item
