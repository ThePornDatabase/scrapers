import html

from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteLasVegasAmateursPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/tour/models/models_%s_d.html',
        'external_id': 'girls/(.+)/?$'
    }

    name = 'LasVegasAmateursPerformer'

    start_urls = [
        'http://lasvegasamateurs.com',
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[@class="modelPic"]')
        for performer in performers:
            item = PerformerItem()

            name = performer.xpath('./div/p/a/text()').get()
            if name:
                item['name'] = html.unescape(name.strip().title())

            image = performer.xpath('.//a/img/@src0_2x').get()
            if image:
                item['image'] = "https://lasvegasamateurs.com/" + image.replace(" ", "%20")
            else:
                item['image'] = None
            item['image'] = None

            item['image_blob'] = None

            url = performer.xpath('./a[contains(@href, "/models/")][1]/@href').get()
            if url:
                item['url'] = self.format_link(response, url.strip()).replace(" ", "%20")

            item['network'] = 'Las Vegas Amateurs'

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
