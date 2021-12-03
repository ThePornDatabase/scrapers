import html
import scrapy
from scrapy import Selector
from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class NetworkJavHDPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/en/models/top/%s',
        'external_id': 'girls/(.+)/?$'
    }

    name = 'JavHDPerformer'

    start_urls = [
        'https://javhd.com',
    ]

    headers = {
        'X-Requested-With': 'XMLHttpRequest',
    }

    cookies = {
        'locale': 'en',
    }

    def start_requests(self):
        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, self.page),
                                 callback=self.parse,
                                 meta={'page': self.page},
                                 headers=self.headers,
                                 cookies=self.cookies)

    def get_performers(self, response):
        jsondata = response.json()
        data = jsondata['template']
        data = data.replace("\n", "").replace("\t", "").replace("\r", "").replace("  ", " ").strip()
        data = data.replace("  ", " ").strip()
        data = data.replace("  ", " ").strip()
        data = data.replace("  ", " ").strip()
        sel = Selector(text=data)
        performers = sel.xpath('//thumb-component')
        for performer in performers:
            item = PerformerItem()

            name = performer.xpath('./@title')
            if name:
                item['name'] = html.unescape(name.get().strip().title())

            image = performer.xpath('./@url-thumb')
            if image:
                item['image'] = self.format_link(response, image.get())
            else:
                item['image'] = None

            item['image_blob'] = None

            url = performer.xpath('./@link-content')
            if url:
                item['url'] = self.format_link(response, url.get().strip()).replace(" ", "%20")
            else:
                item['url'] = response.url

            item['network'] = 'JavHD'

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
