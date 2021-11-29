import datetime
import re
import scrapy

from scrapy import Selector
from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class PornCZPerformerSpider(BasePerformerScraper):
    name = 'PornCZPerformer'
    network = 'PornCZ'

    start_urls = [
        'https://www.porncz.com'
    ]

    headers = {
        'x-requested-with': 'XMLHttpRequest'
    }

    cookies = {
        'age-verified': '1',
    }

    selector_map = {
        'external_id': r'models/(.*)/',
        'pagination': '/en/models?do=next&_=%s'
    }

    def start_requests(self):
        yield scrapy.Request(url="https://www.porncz.com/en/models",
                             callback=self.parse,
                             meta={'page': 0},
                             headers=self.headers, cookies=self.cookies)

    def parse(self, response, **kwargs):
        count = 0
        if response.meta['page']:
            performers = self.get_performers(response)
            count = len(performers)
            for performer in performers:
                yield performer
        if count or not response.meta['page']:
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                meta = response.meta
                meta['page'] = meta['page'] + 1
                timetext = datetime.datetime.utcnow().strftime("%H%M%S%f")
                yield scrapy.Request(url=self.get_next_page_url(response.url, timetext),
                                     callback=self.parse,
                                     meta=meta,
                                     headers=self.headers, cookies=self.cookies)

    def get_performers(self, response):
        item_list = []
        jsondata = response.json()
        jsondata = jsondata['snippets']
        jsondata = jsondata['snippet-modelsGrid-modelItemsAppend'].lower()
        jsonsel = Selector(text=jsondata)
        performers = jsonsel.xpath('//div[contains(@class,"color_12-shadow-sm-hover")]')
        count = 0
        for performer in performers:
            count = count + 1
            item = PerformerItem()
            item['bio'] = ''
            item['gender'] = ''
            item['birthday'] = ''
            item['astrology'] = ''
            item['birthplace'] = ''
            item['ethnicity'] = ''
            item['nationality'] = ''
            item['haircolor'] = ''
            item['measurements'] = ''
            item['tattoos'] = ''
            item['piercings'] = ''
            item['fakeboobs'] = ''
            item['eyecolor'] = ''
            item['cupsize'] = ''
            item['height'] = ''
            item['weight'] = ''
            item['network'] = "PornCZ"
            name = performer.xpath('./div/h3/a/text()').get()
            if name:
                item['name'] = name.strip().title()

            url = performer.xpath('./a/@href').get()
            if url:
                item['url'] = "https://www.porncz.com/" + url.strip()

            image = performer.xpath('./a/img/@data-src').get()
            if image:
                item['image'] = "https://www.porncz.com" + image.strip()

            item['image_blob'] = None

            descline = performer.xpath('./a/div/p/text()').get()
            if descline:
                descline = descline.replace("-", "").strip()
                if re.search('size:(.*)weight', descline):
                    cupsize = re.search('size:(.*)weight', descline).group(1)
                    if cupsize:
                        item['cupsize'] = cupsize.strip().title()

                if re.search(r'(\d+\ kg)', descline):
                    weight = re.search(r'(\d+\ kg)', descline).group(1)
                    if weight:
                        item['weight'] = weight.strip().title()

                if re.search(r'(\d+\ cm)', descline):
                    height = re.search(r'(\d+\ cm)', descline).group(1)
                    if height:
                        item['height'] = height.strip().title()

            item_list.append(item.copy())
            item.clear()

        return item_list

    def get_next_page_url(self, base, page):
        url = self.format_url(base, self.get_selector_map('pagination') % page)
        return url
