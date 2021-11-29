import re
import html
from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteVirtualTabooPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/pornstars?page=%s',
        'external_id': 'girls/(.+)/?$'
    }

    name = 'VirtualTabooPerformer'

    start_urls = [
        'https://virtualtaboo.com',
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[@class="actor-list"]/div[@class="item"]')
        for performer in performers:
            item = PerformerItem()

            name = performer.xpath('./a[@class="title"]/text()')
            if name:
                item['name'] = html.unescape(name.get().strip().title())

            image = performer.xpath('./a/@style')
            if image:
                image = image.get()
                image = re.search(r'.*(https.*?\.jpg).*', image).group(1)
                item['image'] = self.format_link(response, image)
            else:
                item['image'] = None

            item['image_blob'] = None

            url = performer.xpath('./a[1]/@href')
            if url:
                item['url'] = self.format_link(response, url.get().strip()).replace(" ", "%20")
            else:
                item['url'] = response.url

            item['network'] = 'POVR'

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
