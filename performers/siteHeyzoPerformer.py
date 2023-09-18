import re
import string
import scrapy
from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteHeyzoPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[contains(@id, "woman_portfolio")]/ul/li[contains(text(), "Name:")]/text()',
        're_name': r': (.*)',
        'image': '//div[contains(@id, "woman_portfolio")]//img/@src',
        'height': '//div[contains(@id, "woman_portfolio")]/ul/li[contains(text(), "Tall")]/text()',
        're_height': r'(\d+)',
        'measurements': '//div[contains(@id, "woman_portfolio")]/ul/li[contains(text(), "B:")]/text()',
        'birthplace': '//div[contains(@id, "woman_portfolio")]/ul/li[contains(text(), "From")]/text()',
        'pagination': '/girls?page=%s',
        'external_id': r'model\/(.*)/'
    }

    name = 'HeyzoPerformer'
    network = 'Heyzo'
    parent = 'Heyzo'
    site = 'Heyzo'

    max_pages = 1

    def start_requests(self):
        url = "https://en.heyzo.com/actor_all.html"
        yield scrapy.Request(url, callback=self.get_performers)

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        meta = response.meta
        performers = response.xpath('//h1[@class="long"]/following-sibling::ul/li/a[1]')
        for performer in performers:
            meta['name'] = performer.xpath('./img/@alt').get()
            meta['alt_image'] = performer.xpath('./img/@src').get()
            performer = performer.xpath('./@href').get()
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, meta=meta)

    def get_measurements(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements'))
            if measurements:
                measurements = measurements.get()
                measurements = measurements.replace("\r", "").replace("\n", "").replace("\t", "").replace(":", "")
                measurements = re.sub('[^a-zA-Z0-9]', '', measurements)
                if measurements and re.search(r'(B\d{2,3}W\d{2,3}H\d{2,3})', measurements):
                    bust = re.search(r'B(\d{2,3})', measurements).group(1)
                    if bust:
                        bust = round(int(bust) / 2.54)
                    waist = re.search(r'W(\d{2,3})', measurements).group(1)
                    if waist:
                        waist = round(int(waist) / 2.54)
                    hips = re.search(r'H(\d{2,3})', measurements).group(1)
                    if hips:
                        hips = round(int(hips) / 2.54)

                    cupsize = response.xpath('//div[contains(@id, "woman_portfolio")]/ul/li[contains(text(), "Cups")]/text()')
                    if cupsize:
                        cupsize = cupsize.get()
                        cupsize = cupsize.lower().replace("cups of a brassiere", "")
                        cupsize = re.sub('[^a-zA-Z]', '', cupsize)

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

    def get_height(self, response):
        height = super().get_height(response)
        if height and int(height) > 30:
            height = height + "cm"
        return height

    def get_image(self, response):
        meta = response.meta
        image = super().get_image(response)
        if ".com/" not in image:
            return self.format_link(response, meta['alt_image'])
        return image

    def get_birthplace(self, response):
        birthplace = super().get_birthplace(response)
        birthplace = birthplace.lower().replace("from", "")
        birthplace = re.sub('[^a-zA-Z,]', '', birthplace)
        birthplace = string.capwords(birthplace.strip())
        return birthplace
