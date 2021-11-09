import html

from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteGirlsFuckGirlsPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[@class="update_details"]/a[1]/text()',
        'image': "//div[contains(@class,'image_area')]/img[@class='img-responsive']/@src",
        'pagination': '/models/%s/latest/?g=',
        'external_id': r'girls/(.+)/?$'
    }

    name = 'GirlsFuckGirlsPerformer'
    network = "Girls Fuck Girls"

    start_urls = [
        'http://girlsfuckgirls.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="item-portrait"]')
        for performer in performers:
            item = PerformerItem()

            name = performer.xpath('.//h4/a/text()').get()
            if name:
                item['name'] = html.unescape(name.strip().title())

            image = performer.xpath('./a/img/@src0_1x').get()
            if image:
                item['image'] = "http://girlsfuckgirls.com" + image.strip()
            else:
                item['image'] = None
            item['image_blob'] = None

            url = performer.xpath('./a[1]/@href').get()
            if url:
                item['url'] = url.strip()

            item['network'] = 'Girls Fuck Girls'

            item['astrology'] = ''
            item['bio'] = ''
            item['birthday'] = ''
            item['birthplace'] = ''
            item['cupsize'] = ''
            item['ethnicity'] = ''
            item['eyecolor'] = ''
            item['fakeboobs'] = ''
            item['gender'] = ''
            item['haircolor'] = ''
            item['height'] = ''
            item['measurements'] = ''
            item['nationality'] = ''
            item['piercings'] = ''
            item['tattoos'] = ''
            item['weight'] = ''

            yield item
