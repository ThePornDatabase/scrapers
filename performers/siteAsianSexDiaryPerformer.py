from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteAsianSexDiaryPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/models/page/%s/?sortby=date',
        'external_id': r'model/(.*)/'
    }

    name = 'SiteAsianSexDiaryPerformer'

    start_urls = [
        'https://asiansexdiary.com/',
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[contains(@class, "fsp-model")]')
        for performer in performers:
            item = PerformerItem()

            item['name'] = self.cleanup_title(performer.xpath('.//h4/text()').get())
            image = performer.xpath('.//amp-img/@src')
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
            item['network'] = 'Vegas Dreamworks'
            item['url'] = self.format_link(response, performer.xpath('./a/@href').get())

            yield item
