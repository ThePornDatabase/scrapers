import html
from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteMatureNLPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/en/models/%s',
        'external_id': 'girls/(.+)/?$'
    }

    name = 'MatureNLPerformer'

    start_urls = [
        'https://www.mature.nl',
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[@class="grid-item"]')
        for performer in performers:
            item = PerformerItem()

            name = performer.xpath('.//div[@class="card-label"]/a/text()')
            if name:
                item['name'] = html.unescape(name.get().strip().title())

            image = performer.xpath('.//img/@data-src')
            if image:
                image = image.get()
                image = image.replace(" ", "%20")
                item['image'] = self.format_link(response, image)
            else:
                item['image'] = None

            item['image_blob'] = self.get_image_blob_from_link(item['image'])

            url = performer.xpath('.//div[@class="card-label"]/a/@href')
            if url:
                item['url'] = self.format_link(response, url.get().strip()).replace(" ", "%20")
            else:
                item['url'] = response.url

            item['network'] = 'Mature NL'

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
