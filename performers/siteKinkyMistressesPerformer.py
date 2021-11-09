import html
from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteKinkyMistressesPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/Kinky-Mistresses-%s-models.htm',
        'external_id': 'girls/(.+)/?$'
    }

    name = 'KinkyMistressesPerformer'

    start_urls = [
        'https://www.kinkymistresses.com',
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[@class="modelsgrid"]/div')
        for performer in performers:
            item = PerformerItem()

            name = performer.xpath('./h3/a/text()').get()
            if name:
                item['name'] = html.unescape(name.strip().title())

            image = performer.xpath('./a/img/@src').get()
            if image:
                item['image'] = "https://www.kinkymistresses.com" + image
            else:
                item['image'] = None
            item['image_blob'] = None

            item['url'] = "https://www.kinkymistresses.com/" + performer.xpath('./a/@href').get()
            item['network'] = 'Kinky Mistresses'
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
