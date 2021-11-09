import html

from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteCruelGirlfriendSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[@class="update_details"]/a[1]/text()',
        'image': "//div[contains(@class,'image_area')]/img[@class='img-responsive']/@src",
        'pagination': '/cggirls%s.html',
        'external_id': 'girls/(.+)/?$'
    }

    name = 'CruelGirlfriendPerformer'
    network = "Cruel Girlfriend"

    start_urls = [
        'https://cruelgf.com',
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[contains(@class,"col-md-third")]')
        for performer in performers:
            item = PerformerItem()

            name = performer.xpath('.//div[contains(@class,"Name")]/text()').get()
            if name:
                item['name'] = html.unescape(name.strip().title())

            image = performer.xpath('.//a/img/@src').get()
            if image:
                item['image'] = self.format_link(response, image).replace(" ", "%20")
            else:
                item['image'] = None
            item['image_blob'] = None

            url = performer.xpath('.//a/@href').get()
            if url:
                item['url'] = self.format_link(response, url.strip()).replace(" ", "%20")

            item['network'] = 'Cruel Girlfriend'

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
