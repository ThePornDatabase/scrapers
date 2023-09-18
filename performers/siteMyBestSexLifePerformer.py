from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteMyBestSexLifePerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/models/models_%s_p.html',
        'external_id': r'model/(.*)/'
    }

    name = 'MyBestSexLifePerformer'
    network = 'My Best Sex Life'

    start_urls = [
        'https://mybestsexlife.com',
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[contains(@class, "item-model")]')
        for performer in performers:
            item = PerformerItem()

            item['name'] = self.cleanup_title(performer.xpath('.//h4/a/center/text()').get())
            item['image'] = self.format_link(response, performer.xpath('.//img/@src0_1x').get()).replace("content//", "content/")
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
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
            item['network'] = 'My Best Sex Life'
            item['url'] = performer.xpath('.//h4/a/@href').get()

            yield item
