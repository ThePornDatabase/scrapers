import re
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteJavDatabasePerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//span[@property="name" and contains(@class, "current")]/text()',
        'image': '//div[@class="idol-portrait"]/a/img[contains(@class, "lazyload")]/@data-src',
        'image_blob': True,
        'birthday': '//b[contains(text(), "DOB:") and not(contains(./following-sibling::text(), "Unknown"))]//following-sibling::a[1]/text()',
        'birthplace': '//b[contains(text(), "Birthplace:") and not(contains(./following-sibling::text(), "Unknown"))]//following-sibling::a[1]/text()',
        'haircolor': '//b[contains(text(), "Hair Color") and not(contains(./following-sibling::text(), "Unknown"))]//following-sibling::a[1]/text()',
        'measurements': '//b[contains(text(), "Measurements") and not(contains(./following-sibling::text(), "Unknown"))]//following-sibling::text()[1]',

        'pagination': '/idols/page/%s/?_sort_=newest',
        'external_id': r'model/(.*)/'
    }

    custom_scraper_settings = {
        'USER_AGENT':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.62',
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 10,
        'CONCURRENT_REQUESTS': 1,
        # ~ 'DOWNLOAD_DELAY': 60,
        # ~ 'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'CONCURRENT_REQUESTS_PER_IP': 1,
    }

    name = 'JavDatabasePerformer'
    network = 'JavDatabase'

    start_urls = [
        'https://www.javdatabase.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[contains(@class, "card-body")]/p/a[contains(@href, "javdatabase")]/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, cookies=self.cookies, headers=self.headers)

    def get_measurements(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements'))
            if measurements:
                measurements = measurements.get()
                measurements = measurements.replace("\r", "").replace("\n", "").replace("\t", "").replace(":", "")
                measurements = re.search(r'(\d+)-(\d+)-(\d+)', measurements)
                if measurements:
                    bust = measurements.group(1)
                    if bust:
                        bust = round(int(bust) / 2.54)
                    waist = measurements.group(2)
                    if waist:
                        waist = round(int(waist) / 2.54)
                    hips = measurements.group(3)
                    if hips:
                        hips = round(int(hips) / 2.54)

                    cupsize = response.xpath('//b[contains(text(), "Cup:") and not(contains(./following-sibling::text(), "Unknown"))]//following-sibling::a[1]/text()')
                    if cupsize:
                        cupsize = cupsize.get()
                        cupsize = re.sub('[^a-zA-Z]', '', cupsize.strip())
                        if cupsize:
                            cupsize = cupsize.strip()
                            cupsize = cupsize.upper()
                    if not cupsize:
                        cupsize = ""
                    if bust and waist and hips:
                        measurements = str(bust) + cupsize + "-" + str(waist) + "-" + str(hips)

                    if measurements:
                        return measurements.strip()
        return ''

    def get_cupsize(self, response):
        cupsize = self.get_measurements(response)
        if cupsize:
            cupsize = re.search(r'(.*?)-', cupsize).group(1)
            return cupsize
        return ""

    def get_birthday(self, response):
        javdate = response.xpath(self.get_selector_map('birthday'))
        if javdate and "??" not in javdate:
            return javdate.get()
        return ""

    def get_image(self, response):
        image = super().get_image(response)
        # ~ print(image)
        return image
