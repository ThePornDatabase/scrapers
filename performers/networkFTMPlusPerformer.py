import re
from tpdb.items import PerformerItem
from tpdb.BasePerformerScraper import BasePerformerScraper


class NetworkFTMPlusPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/models?page=%s',
        'external_id': r'model/(.*)/'
    }

    name = 'FTMPlusPerformer'
    network = 'FTMPlus'

    start_urls = [
        'https://ftmplus.com',
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[@class="grid-item-model" and not(contains(@data-idset, "Id"))]')
        for performer in performers:
            item = PerformerItem()
            item['name'] = self.cleanup_title(performer.xpath('.//h4/text()').get())
            item['url'] = self.format_link(response, performer.xpath('./div/a/@href').get())
            item['gender'] = 'Male'
            image = performer.xpath('.//img/@data-src')
            if image:
                image = self.format_link(response, image.get())
                item['image'] = self.format_link(response, image)
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
                if "?" in item['image']:
                    item['image'] = re.search(r'(.*?)\?', item['image']).group(1)
            if not image:
                item['image'] = ''
                item['image_blob'] = ''
            item['network'] = 'FTMPlus'
            item['bio'] = ''
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
            yield item
