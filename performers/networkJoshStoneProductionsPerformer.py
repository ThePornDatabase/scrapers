import html
from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class NetworkJoshStoneProductionsPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/tour3/models/models_%s.html',
        'external_id': 'girls/(.+)/?$'
    }

    name = 'JoshStoneProductionsPerformer'
    network = "Josh Stone Productions"

    start_urls = [
        'https://www.trans500.com/',
    ]

    def get_gender(self, response):
        return 'Trans'

    def get_performers(self, response):
        performers = response.xpath('//div[contains(@class,"text-center pad_bottom_15")]')
        for performer in performers:
            item = PerformerItem()

            name = performer.xpath('./h3/text()').get()
            if name:
                item['name'] = html.unescape(name.strip().title())

            image = performer.xpath('./a/img/@src').get()
            if image:
                item['image'] = image.strip()
            else:
                item['image'] = None
            item['image_blob'] = None

            url = performer.xpath('./a/@href').get()
            if url:
                item['url'] = "https://www.trans500.com" + url.strip()

            item['network'] = 'Josh Stone Productions'

            item['astrology'] = ''
            item['bio'] = ''
            item['birthday'] = ''
            item['birthplace'] = ''
            item['cupsize'] = ''
            item['ethnicity'] = ''
            item['eyecolor'] = ''
            item['fakeboobs'] = ''
            item['gender'] = 'Trans'
            item['haircolor'] = ''
            item['height'] = ''
            item['measurements'] = ''
            item['nationality'] = ''
            item['piercings'] = ''
            item['tattoos'] = ''
            item['weight'] = ''

            yield item
