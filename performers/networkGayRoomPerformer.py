from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class NetworkGayRoomPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/models?page=%s',
        'external_id': r'model/(.*)/'
    }

    name = 'GayRoomPerformer'
    network = 'GayRoom'

    start_urls = [
        'https://bathhousebait.com',
        'https://boysdestroyed.com',
        'https://damnthatsbig.com',
        'https://gaycastings.com',
        'https://gaycreeps.com',
        'https://gayviolations.com',
        'https://massagebait.com',
        'https://menpov.com',
        'https://officecock.com',
        'https://outhim.com',
        'https://showerbait.com',
        'https://thickandbig.com',
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[contains(@class,"actor-thumb flex flex-col")]')
        for performer in performers:
            item = PerformerItem()

            item['name'] = self.cleanup_title(performer.xpath('.//a/span/text()').get())
            item['image'] = self.format_link(response, performer.xpath('.//img/@src').get())
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['bio'] = ''
            item['gender'] = 'Male'
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
            item['network'] = 'GayRoom'
            link = self.format_link(response, performer.xpath('./div[1]/a/@href').get())
            if "join" in link:
                link = response.url
            item['url'] = link

            yield item
