import html

from tpdb.items import PerformerItem
from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteMongerInAsiaPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/categories/models_%s_d',
        'external_id': r'models/(.*).html'
    }

    name = 'MongerInAsiaPerformer'
    network = "Monger In Asia"

    start_urls = [
        'https://www.mongerinasia.com'
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[@class="model"]')
        for performer in performers:
            item = PerformerItem()

            name = performer.xpath('./div/p/text()').get()
            if name:
                item['name'] = html.unescape(name.strip().title())
            else:
                item['name'] = ''

            image = performer.xpath('.//img/@src').get()
            if image:
                item['image'] = image.strip()
            else:
                item['image'] = None
            item['image_blob'] = None

            item['url'] = response.url

            item['network'] = 'Monger in Asia'

            item['astrology'] = ''
            item['bio'] = ''
            item['birthday'] = ''
            item['birthplace'] = ''
            item['cupsize'] = ''
            item['ethnicity'] = ''
            item['eyecolor'] = ''
            item['fakeboobs'] = ''
            item['gender'] = 'Female'
            item['haircolor'] = ''
            item['height'] = ''
            item['measurements'] = ''
            item['nationality'] = ''
            item['piercings'] = ''
            item['tattoos'] = ''
            item['weight'] = ''

            yield item
