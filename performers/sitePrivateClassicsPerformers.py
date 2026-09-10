import re
import string
import scrapy
from tpdb.BasePerformerScraper import BasePerformerScraper


class SitePrivateClassicsPerformerSpider(BasePerformerScraper):
    selector_map = {
        'height': '//p[contains(text(), "Height")]/strong/text()',
        'weight': '//p[contains(text(), "Weight")]/strong/text()',
        'birthplace': '//div[contains(@class, "user-tools")]/following-sibling::div[contains(@class, "content-info")]/p[contains(text(), "Birth")]/strong/text()',
        'nationality': '//p[contains(text(), "Nationality")]/strong/text()',
        'astrology': '//p[contains(text(), "Sign")]/strong/text()',
        'haircolor': '//p[contains(text(), "Hair color")]/strong/text()',
        'eyecolor': '//p[contains(text(), "Eye color")]/strong/text()',
        'measurements': '//p[contains(text(), "Measurements")]/strong/text()',
        'tattoos': '//p[contains(text(), "Tattoos")]/strong/text()',
        'piercings': '//p[contains(text(), "Piercings")]/strong/text()',
        'bio': '//div[contains(@class,"content-info-model")]/p[@class="description"]/text()',
        'pagination': '/en/pornstars/%s/',
        'external_id': r'models\/(.*).html'
    }

    name = 'PrivateClassicsPerformer'
    network = 'Private Classics'

    start_urls = [
        'https://www.privateclassics.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        meta = self.copy_meta(response)
        performers = response.xpath('//article[contains(@class, "model")]')
        for performer in performers:
            perf_url = performer.xpath('./figure/a/@href').get()
            perf_id = re.search(r'.*/(\d+)', perf_url).group(1)
            perf_name = performer.xpath('.//h1/a/text()')
            if perf_name:
                perf_name = perf_name.get().strip()
                if " " not in perf_name:
                    perf_name = perf_name + " " + perf_id
            meta['name'] = perf_name

            image = performer.xpath('.//figure/a/img/@src')
            if image:
                meta['image'] = self.format_link(response, image.get().strip())
                meta['image_blob'] = self.get_image_blob_from_link(meta['image'])
                bare_image = re.search(r'(.*)\?', meta['image'])
                if bare_image:
                    meta['image'] = bare_image.group(1)

            meta['gender'] = "Female"
            meta['site'] = "Private Classics"
            meta['network'] = "Private Classics"

            yield scrapy.Request(url=self.format_link(response, perf_url), callback=self.parse_performer, meta=meta)

    def get_measurements(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements and re.match('(.*-.*-.*)', measurements):
                return measurements.strip()
        return ''

    def get_cupsize(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements and re.match('(.*-.*-.*)', measurements):
                cupsize = re.search(r'(?:\s+)?(.*)-.*-', measurements).group(1)
                if cupsize:
                    return cupsize.strip()
        return ''

    def get_height(self, response):
        height = super().get_height(response)
        if not height.replace("-", "").strip():
            height = ""
        if "cm" in height:
            height = re.sub('[^a-z0-9]', '', height.lower())
            height = re.search(r'(\d+cm)', height).group(1)
        return height

    def get_weight(self, response):
        weight = super().get_weight(response)
        if not weight.replace("-", "").strip():
            weight = ""
        if "kg" in weight:
            weight = re.sub('[^a-z0-9]', '', weight.lower())
            weight = re.search(r'(\d+kg)', weight).group(1)
        return weight

    def get_tattoos(self, response):
        tattoos = super().get_tattoos(response)
        if not tattoos.replace("-", "").strip():
            tattoos = ""
        return tattoos

    def get_piercings(self, response):
        piercings = super().get_piercings(response)
        if not piercings.replace("-", "").strip():
            piercings = ""
        return piercings
    
    def get_network(self, response):
        return "Private Classics"
    
    def get_site(self, response):
        return "Private Classics"
