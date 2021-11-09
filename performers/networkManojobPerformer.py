import html

from tpdb.items import PerformerItem
from tpdb.BasePerformerScraper import BasePerformerScraper


class NetworkManojobPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//h3[@class="mg-md"]/text()',
        'image': '//div[contains(@class,"bigmodelpic")]/img/@src',
        'haircolor': '//div[contains(@class,"modeldetail")]/strong[contains(text(),"Hair")]/following-sibling::text()[1]',
        'ethnicity': '//div[contains(@class,"modeldetail")]/strong[contains(text(),"Race")]/following-sibling::text()[1]',
        'nationality': '//div[contains(@class,"modeldetail")]/strong[contains(text(),"Country")]/following-sibling::text()[1]',
        'height': '//div[contains(@class,"modeldetail")]/strong[contains(text(),"Height")]/following-sibling::text()[1]',
        'weight': '//div[contains(@class,"modeldetail")]/strong[contains(text(),"Weight")]/following-sibling::text()[1]',
        'pagination': '/performers/%s',
        'external_id': r'models/(.*).html'
    }

    name = 'ManojobPerformer'
    network = "Manojob"

    start_urls = [
        'https://www.finishesthejob.com'
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[contains(@class,"card performer")]')
        for performer in performers:
            item = PerformerItem()

            name = performer.xpath('.//a[contains(@class,"primary")]/text()').get()
            if name:
                name = name.replace("More ", "")
                item['name'] = html.unescape(name.strip().title())

            image = performer.xpath('.//span/img/@src').get()
            if image:
                item['image'] = image.strip()
            else:
                item['image'] = None
            item['image_blob'] = None

            url = performer.xpath('.//a[contains(@class,"primary")]/@href').get()
            if url:
                item['url'] = url.strip()

            item['network'] = 'Manojob'

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
