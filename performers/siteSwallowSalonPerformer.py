import requests
from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteSwallowSalonPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/models/models_%s.html',
        'external_id': r'model/(.*)/'
    }

    name = 'SwallowSalonPerformer'

    start_urls = [
        'https://www.swallowsalon.com',
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[@class="update_details"]')
        for performer in performers:
            item = PerformerItem()

            item['name'] = self.cleanup_title(performer.xpath('./a[1]/text()').get())
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
            item['network'] = 'Swallow Salon'
            item['url'] = self.format_link(response, performer.xpath('./a[1]/@href').get())

            yield item

    def get_image_from_link(self, image):
        if image:
            req = requests.get(image, headers={'referer': "https://www.swallowsalon.com/"}, verify=False)
            if req and req.ok:
                return req.content
        return None
