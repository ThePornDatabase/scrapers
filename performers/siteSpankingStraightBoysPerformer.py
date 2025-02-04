import re
from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteSpankingStraightBoysPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/tour/models/models_%s.html',
        'external_id': '',
    }

    name = 'SpankingStraightBoysPerformer'

    start_urls = [
        'https://spankingstraightboys.com',
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[@class="update_details"]')
        for performer in performers:
            item = PerformerItem()

            item['name'] = self.cleanup_title(performer.xpath('./a[1]/text()').get())
            image = performer.xpath('./a/img/@src0_1x')
            if image:
                item['image'] = self.format_link(response, image.get())
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
            else:
                item['image'] = ""
                item['image_blob'] = ""
            if "?" in item['image']:
                item['image'] = re.search(r'(.*)\?', item['image']).group(1)
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
            item['network'] = 'Spanking Straight Boys'
            item['url'] = self.format_link(response, performer.xpath('./a[1]/@href').get())

            yield item
