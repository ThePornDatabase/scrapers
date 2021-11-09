import html
from urllib.parse import urlparse

from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class NetworkNebraskaCoedsPornstarSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[@class="update_details"]/a[1]/text()',
        'image': "//div[contains(@class,'image_area')]/img[@class='img-responsive']/@src",
        'pagination': '/models/models_%s_d.html',
        'external_id': r'girls/(.+)/?$'
    }

    name = 'NebraskaCoedsPerformer'
    network = "Nebraska Coeds"

    start_urls = [
        'https://tour.nebraskacoeds.com',
        'https://www.springbreaklife.com',
        'https://tour.southbeachcoeds.com',
        'https://tour.afterhoursexposed.com',
        'https://tour.eurocoeds.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="modelPic"]')
        for performer in performers:
            item = PerformerItem()

            name = performer.xpath('./div[@class="modelName"]/p/a/text()').get()
            if name:
                item['name'] = html.unescape(name.strip().title())

            image = performer.xpath('./a/img/@src0_3x|./a/img/@src0_2x|./a/img/@src0_1x|./a/img/@src0').get()
            if image:
                item['image'] = image.strip()
            else:
                item['image'] = None
            item['image_blob'] = None

            url = performer.xpath('./a[1]/@href').get()
            if url:
                if "sets.php" in url:
                    uri = urlparse(response.url)
                    base = uri.scheme + "://" + uri.netloc
                    url = base + "/" + url.strip()
                item['url'] = url.strip()

            item['network'] = 'Nebraska Coeds'

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
