import re
import base64
import requests
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class ThisIsGlamourPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//h1/text()',
        'image': '//div[@class="product-page"]//img/@src',
        'image_blob': '//div[@class="product-page"]//img/@src',
        'birthplace': '//p[@class="mb-1 mt-3"]/a/span/text()',
        'nationality': '//div[contains(@class, "modelinfo")]/div[contains(text(), "COUNTRY")]/following-sibling::div[1]/text()',
        'eyecolor': '//div[contains(@class, "modelinfo")]/div[contains(text(), "EYE COLOUR")]/following-sibling::div[1]/text()',
        'haircolor': '//div[contains(@class, "modelinfo")]/div[contains(text(), "HAIR COLOUR")]/following-sibling::div[1]/text()',
        'height': '//div[contains(@class, "modelinfo")]/div[contains(text(), "HEIGHT")]/following-sibling::div[1]/text()',
        'weight': '//div[contains(@class, "modelinfo")]/div[contains(text(), "WEIGHT")]/following-sibling::div[1]/text()',
        'cupsize': '//div[contains(@class, "modelinfo")]/div[contains(text(), "BREASTS")]/following-sibling::div[1]/text()',
        'measurements': '//div[contains(@class, "modelinfo")]/div[contains(text(), "MEASUREMENT")]/following-sibling::div[1]/text()',
        'astrology': '//div[contains(@class, "modelinfo")]/div[contains(text(), "SIGN")]/following-sibling::div[1]/text()',
        'bio': '//div[@class="description"]/text()',
        'pagination': '/glamour-models/?start=%s&count=28',
        'external_id': 'models/(.+).html$'
    }

    name = 'ThisIsGlamourPerformer'
    network = 'This Is Glamour'
    phpsessid = ''

    start_urls = [
        'http://www.thisisglamour.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_next_page_url(self, base, page):
        page = str((int(page) - 1) * 28)
        url = self.format_url(base, self.get_selector_map('pagination') % page)
        return url

    def get_performers(self, response):
        cookies = response.headers.getlist('Set-Cookie')
        for cookie in cookies:
            if "PHPSESSID" in str(cookie):
                self.phpsessid = re.search(r'SESSID=(.*?);', str(cookie)).group(1)
        performers = response.xpath('//div[@class="product-item"]/h3/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer
            )

    def get_image(self, response):
        if 'image' in self.selector_map:
            image = self.process_xpath(response, self.get_selector_map('image')).get()
            if image:
                return image.strip()
        return ''

    def get_image_blob(self, response):
        image = self.get_image(response)
        if image:
            # ~ image = image.get().strip().replace("https://", "http://")
            if self.phpsessid:
                imagereq = requests.get(image, cookies={'PHPSESSID': self.phpsessid})
                image = base64.b64encode(imagereq.content).decode('utf-8')
                return image
        return None

    def get_url(self, response):
        url = re.search(r'(.*)\?', response.url).group(1)
        return url
