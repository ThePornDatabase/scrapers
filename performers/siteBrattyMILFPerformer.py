import re
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class BrattyMILFPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[contains(@class, "model-profile-desc")]/h2/text()',
        'image': '//div[@class="row model-profile"]/div/img/@src',
        'bio': '//h2[contains(text(), "Biography")]/following-sibling::p/text()',
        'height': '//h5[contains(text(), "Height")]/following-sibling::p[1]/text()',
        'nationality': '//h5[contains(text(), "Location")]/following-sibling::p[1]/text()',
        'measurements': '//h5[contains(text(), "Figure")]/following-sibling::p[1]/text()',
        'pagination': '/model/gallery/%s',
        'external_id': r'model/(.*)/'
    }

    custom_settings = {'DOWNLOADER_MIDDLEWARES': {'tpdb.mymiddlewares.CustomProxyMiddleware': 350, 'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 400}}

    name = 'BrattyMILFPerformer'
    network = 'Nubiles'

    start_urls = [
        'https://brattymilf.com',
    ]

    def get_next_page_url(self, base, page):
        page = str((int(page) - 1) * 16)
        return self.format_url(base, self.get_selector_map('pagination') % page)

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//figcaption/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer
            )

    def get_measurements(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements and re.match(r'\d+.*?-.*?\d+.*?-.*?\d+', measurements):
                measurements = measurements.replace("B", "").replace("W", "").replace("H", "")
                return measurements.strip()
        return ''

    def get_cupsize(self, response):
        if 'cupsize' in self.selector_map:
            cupsize = self.process_xpath(response, self.get_selector_map('cupsize')).get()
            if cupsize:
                if 'measurements' in self.selector_map:
                    measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
                    if measurements and re.match(r'\d+.*?-.*?\d+.*?-.*?\d+', measurements):
                        breasts = re.search(r'(\d+).*?-.*?\d+.*?-.*?\d+', measurements).group(1)
                        cupsize = breasts.strip() + cupsize.strip()
                        if cupsize:
                            return cupsize.strip()
                return cupsize.strip()
        return ''

    def get_image(self, response):
        image = self.process_xpath(response, self.get_selector_map('image')).get()
        if image:
            image = "https:" + image
            return self.format_link(response, image)
        return ''
