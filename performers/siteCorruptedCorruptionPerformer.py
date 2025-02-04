from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteCorruptedCorruptionPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/models/models_%s.html?g=f',
        'external_id': r'model/(.*)/'
    }

    name = 'CorruptedCorruptionPerformer'

    start_urls = [
        'https://collectivecorruption.com',
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[@class="model"]')
        for performer in performers:
            item = PerformerItem()

            perf_name
            item['name'] = self.cleanup_title(perf_name.strip())
            image = performer.xpath('')
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
            item['network'] = ''
            item['url'] = self.format_link(response, performer.xpath('').get())

            yield item
