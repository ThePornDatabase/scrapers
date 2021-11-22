import html

from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SitePOVPervPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/models?order=created_at&page=%s',
        'external_id': 'girls/(.+)/?$'
    }

    name = 'POVPervPerformer'

    start_urls = [
        'https://tour.povperv.com',
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[@class="model-item"]')
        for performer in performers:
            item = PerformerItem()

            name = performer.xpath('.//h3/a/text()')
            if name:
                item['name'] = html.unescape(name.get().strip().title())

            image = performer.xpath('./div[@class="thumb-wrap"]/img[1]/@src')
            if image:
                item['image'] = self.format_link(response, image.get())
            else:
                item['image'] = None

            item['image_blob'] = None

            url = performer.xpath('.//h3/a/@href')
            if url:
                item['url'] = self.format_link(response, url.get().strip()).replace(" ", "%20")
            else:
                item['url'] = response.url

            item['network'] = 'POV Perv'

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
