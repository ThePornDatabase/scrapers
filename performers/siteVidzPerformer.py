import html
from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteZvidzPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/models/models.html?page=%s&sw=&s=d',
        'external_id': 'girls/(.+)/?$'
    }

    name = 'ZvidzPerformer'

    start_urls = [
        'https://www.zvidz.com',
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[contains(@class, "model-grid-item")]')
        for performer in performers:
            item = PerformerItem()

            name = performer.xpath('.//div[@class="model-name"]/text()')
            if name:
                item['name'] = html.unescape(name.get().strip().title())

            image = performer.xpath('./a/div/img/@src')
            if image:
                image = image.get()
                item['image'] = self.format_link(response, image)
            else:
                item['image'] = None

            item['image_blob'] = None

            url = performer.xpath('./a/@href')
            if url:
                item['url'] = self.format_link(response, url.get().strip()).replace(" ", "%20")
            else:
                item['url'] = response.url

            item['network'] = 'Zvidz'

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
