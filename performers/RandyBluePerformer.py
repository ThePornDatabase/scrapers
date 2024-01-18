import re
from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteRandyBluePerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/models/models_%s_d.html',
        'external_id': r'model/(.*)/'
    }

    name = 'RandyBluePerformer'

    start_urls = [
        'https://www.randyblue.com',
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[@class="model"]')
        for performer in performers:
            item = PerformerItem()

            item['name'] = self.cleanup_title(performer.xpath('.//h3/a/text()').get())
            image = performer.xpath('.//picture/source[1]/@srcset')
            if image:
                image = image.get()
                if " " in image:
                    image = re.search(r'(.*) ', image).group(1)
                item['image'] = self.format_link(response, image)
                item['image_blob'] = self.get_image_blob_from_link(image)
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
            item['network'] = 'RandyBlue'
            item['url'] = self.format_link(response, performer.xpath('.//h3/a/@href').get())

            yield item
