from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SitePerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/models/models_%s.html',
        'external_id': r'model/(.*)/'
    }

    name = 'VRGoddessPerformer'

    start_urls = [
        'https://www.vrgoddess.com',
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[@class="modelPic"]')
        for performer in performers:
            item = PerformerItem()

            item['name'] = self.cleanup_title(performer.xpath('.//p/a/text()').get())
            image = performer.xpath('./a/img/@src0_2x')
            if image:
                item['image'] = self.format_link(response, image.get()).replace("-2x", "-full")
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
            item['network'] = 'NebraskaCoeds'
            item['url'] = self.format_link(response, performer.xpath('./a[1]/@href').get())

            yield item
