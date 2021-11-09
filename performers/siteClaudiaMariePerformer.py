from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteClaudiaMariePerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[@class="model_box"]/div[@class="filter_box"]/h1[@class="page_title"]/text()',
        'image': '//div[@class="model_img"]/img/@src',
        'pagination': '/tour/models/models_%s.html',
        'external_id': r'models/(.*).html'
    }

    name = 'ClaudiaMariePerformer'
    network = "Claudia Marie"
    parent = "Claudia Marie"

    start_urls = [
        'https://www.claudiamarie.com',
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[@class="update_details"]')
        for performer in performers:
            item = PerformerItem()

            name = performer.xpath('./a[1][contains(@href,"/models/")]/text()').get()
            if name:
                item['name'] = name.strip()
            else:
                item['name'] = ''

            image = performer.xpath('.//img/@src0_3x').get()
            if not image:
                image = performer.xpath('.//img/@src0_2x').get()
            if not image:
                image = performer.xpath('.//img/@src0_1x').get()

            if image:
                item['image'] = "https://www.claudiamarie.com" + image
            else:
                item['image'] = None
            item['image_blob'] = None

            url = performer.xpath('./a[1][contains(@href,"/models/")]/@href').get()
            if url:
                item['url'] = url.strip()
            else:
                item['url'] = ''

            item['network'] = "Claudia Marie"

            item['bio'] = ''
            item['gender'] = ''
            item['birthday'] = ''
            item['astrology'] = ''
            item['birthplace'] = ''
            item['ethnicity'] = ''
            item['nationality'] = ''
            item['haircolor'] = ''
            item['weight'] = ''
            item['height'] = ''
            item['measurements'] = ''
            item['tattoos'] = ''
            item['piercings'] = ''
            item['cupsize'] = ''
            item['fakeboobs'] = ''
            item['eyecolor'] = ''

            if item['name'] and item['url']:
                yield item
