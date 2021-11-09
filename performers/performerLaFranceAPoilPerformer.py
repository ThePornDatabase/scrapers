import html
from unidecode import unidecode
from scrapy import Selector

from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteLaFranceAPoilPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[contains(@class,"thumbstar")]//div[@class="pull-left"]/text()',
        'image': '//div[contains(@class,"thumbstar")]//img/@src',
        'pagination': '/portal/morestars.php?aff=&page=%s&tag=&video=&thid=&tr=&trlfap=&cp=&tunl=&iduser=&sort=name&lang=en',
        'external_id': 'girls/(.+)/?$'
    }

    name = 'LaFranceAPoilPerformer'
    network = 'La France a Poil'

    start_urls = [
        'https://www.lafranceapoil.com',
    ]

    cookies = {
        'disclaimerlfap': 'oui',
    }

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        response_text = response.text
        response_text = response_text.replace("\\", "")
        response_xpath = Selector(text=response_text)

        performers = response_xpath.xpath('//a[contains(@href,"amatrice=")]')
        for performer in performers:
            item = PerformerItem()

            name = performer.xpath('.//div[@class="pull-left"]/text()').get()
            if name:
                name = unidecode(name)
                item['name'] = html.unescape(name.strip().title())

            image = performer.xpath('.//img/@src').get()
            if image:
                item['image'] = image.strip()
            else:
                item['image'] = None
            item['image_blob'] = None

            url = performer.xpath('./@href').get()
            if url:
                item['url'] = "https://www.lafranceapoil.com/en/" + url.strip()

            item['network'] = 'La France a Poil'

            item['height'] = ''
            item['weight'] = ''
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
            item['measurements'] = ''
            item['nationality'] = ''
            item['piercings'] = ''
            item['tattoos'] = ''
            yield item

    def get_next_page_url(self, base, page):
        page = str(int(page) - 1)
        return self.format_url(base, self.get_selector_map('pagination') % page)
