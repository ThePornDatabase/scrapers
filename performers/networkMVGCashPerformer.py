import html

from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteMVGCashPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[contains(@class,"model modelfeature")]//h3/a/text()',
        'image': '//div[contains(@class,"model modelfeature")]/div/a/img/@src0_1x',
        'pagination': '/models/%s/latest/',
        'external_id': 'girls/(.+)/?$'
    }
    name = 'MVGCashPerformer'
    network = "MVG Cash"
    start_urls = [
        'https://italianshotclub.com',
        'https://lesbiantribe.com',
        'https://myslutwifegoesblack.com',
        'https://pornlandvideos.com',
        'https://sologirlsmania.com',
        'https://vangoren.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[contains(@class,"model modelfeature")]')
        for performer in performers:
            item = PerformerItem()
            name = performer.xpath('.//h3/a/text()').get()
            if name:
                item['name'] = html.unescape(name.strip().title())
            item['image'] = performer.xpath('./div/a/img/@src0_1x').get().strip()
            item['image_blob'] = None
            url = performer.xpath('.//h3/a/@href').get()
            if url:
                item['url'] = url.strip()
            item['network'] = 'MVG Cash'
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
