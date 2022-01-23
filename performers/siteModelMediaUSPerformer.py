import html
import string
from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteModelMediaUSPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/models?gender=female&sort=published_at&page=%s',
        'external_id': 'girls/(.+)/?$'
    }

    name = 'ModelMediaUSPerformer'

    start_urls = [
        'https://www.modelmediaus.com',
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[contains(@class, "portfolio-item")]')
        for performer in performers:
            item = PerformerItem()

            name = performer.xpath('./a/div/div/text()').get()
            if name:
                item['name'] = string.capwords(html.unescape(name.strip()))

            image = performer.xpath('./a/div/img/@src').get()
            if image:
                item['image'] = self.format_link(response, image).replace(" ", "%20")
            else:
                item['image'] = None
            item['image_blob'] = None

            url = performer.xpath('./a/@href').get()
            if url:
                item['url'] = self.format_link(response, url.strip()).replace(" ", "%20")

            item['network'] = 'Model Media US'

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
