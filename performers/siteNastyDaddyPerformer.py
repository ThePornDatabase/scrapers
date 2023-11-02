import re
from tpdb.items import PerformerItem
from tpdb.BasePerformerScraper import BasePerformerScraper
from slugify import slugify


class NetworkPureEthnicPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/tour/models/models_%s_d.html',
        'external_id': r'model/(.*)/'
    }

    name = 'NastyDaddyPerformer'
    network = 'Nasty Daddy'

    start_urls = [
        'https://nastydaddy.com',
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[contains(@class, "model-thumb")]')
        for performer in performers:
            item = PerformerItem()
            item['name'] = self.cleanup_title(performer.xpath('./div[1]/a[1]/h5/text()').get())
            item['url'] = "https://nastydaddy.com/tour/models/" + slugify(item['name'].lower()) + ".html"
            item['gender'] = 'Male'
            image = performer.xpath('./div[1]/a/img/@src')
            if image:
                image = image.get()
                if "/content/" in image:
                    item['image'] = self.format_link(response, image)
                    item['image_blob'] = self.get_image_blob_from_link(item['image'])
                    if "?" in item['image']:
                        item['image'] = re.search(r'(.*?)\?', item['image']).group(1)
            if not image:
                item['image'] = ''
                item['image_blob'] = ''
            item['network'] = 'Nasty Daddy'
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
