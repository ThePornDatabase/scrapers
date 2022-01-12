import html
from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteTwoTgirlsPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/performers?page=%s',
        'external_id': 'girls/(.+)/?$'
    }

    name = 'TwoTgirlsPerformer'

    start_urls = [
        'https://twotgirls.com',
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[contains(@class, "performer-list-block")]')
        for performer in performers:
            item = PerformerItem()

            name = performer.xpath('./h3/a/text()')
            if name:
                item['name'] = html.unescape(name.get().strip().title())

            image = performer.xpath('./a/img/@src')
            if image:
                image = image.get()
                item['image'] = self.format_link(response, image)
            else:
                item['image'] = None

            item['image_blob'] = None

            url = performer.xpath('./h3/a/@href')
            if url:
                item['url'] = self.format_link(response, url.get().strip()).replace(" ", "%20")
            else:
                item['url'] = response.url

            item['network'] = 'Two Tgirls'

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
