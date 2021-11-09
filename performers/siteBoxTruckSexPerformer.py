import html

from tpdb.items import PerformerItem
from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteBoxTruckSexPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//h3[@class="mg-md"]/text()',
        'image': '//div[contains(@class,"bigmodelpic")]/img/@src',
        'pagination': '/tour/models/models_%s.html',
        'external_id': r'models/(.*).html'
    }

    name = 'BoxTruckSexPerformer'
    network = "Box Truck Sex"

    start_urls = [
        'https://www.boxtrucksex.com'
    ]

    def get_performers(self, response):
        performers = response.xpath('//li[contains(@class,"featured-video")]')
        for performer in performers:
            item = PerformerItem()

            name = performer.xpath('.//h5/a/text()').get()
            if name:
                item['name'] = html.unescape(name.strip().title())
            else:
                item['name'] = ''

            image = performer.xpath('./a/img/@src0_1x').get()
            if image:
                image = "https://www.boxtrucksex.com" + image.strip()
                item['image'] = image.strip()
            else:
                item['image'] = None
            item['image_blob'] = None

            url = performer.xpath('.//h5/a/@href').get()
            if url:
                item['url'] = url.strip()

            item['network'] = 'Box Truck Sex'

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
