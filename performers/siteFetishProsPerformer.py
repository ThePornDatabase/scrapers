import html
from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteFetishProsPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/updates/models/models_%s_d.html',
        'external_id': 'girls/(.+)/?$'
    }

    name = 'FetishProsPerformer'

    start_urls = [
        'https://www.fetishpros.com',
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[@class="model"]')
        for performer in performers:
            item = PerformerItem()

            name = performer.xpath('./p/a/text()')
            if name:
                item['name'] = html.unescape(name.get().strip().title())

            image = performer.xpath('./div/a/img/@src0_2x')
            if image:
                image = image.get()
                item['image'] = self.format_link(response, image)
            else:
                item['image'] = None

            item['image_blob'] = None

            url = performer.xpath('./p/a/@href')
            if url:
                item['url'] = self.format_link(response, url.get().strip()).replace(" ", "%20")
            else:
                item['url'] = response.url

            item['network'] = 'Fetish Pros'

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
