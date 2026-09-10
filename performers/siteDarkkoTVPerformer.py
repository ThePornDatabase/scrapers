import re
import string
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class siteDarkkoTVPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//h1/text()',
        're_name': r'erformer (.*?)$',
        'image': '//meta[@property="og:image"]/@content',
        'image_blob': True,
        'bio': '//div[contains(@class, "modelBioInfo ")]//text()',
        'astrology': '',
        'birthday': '//div[contains(@class, "vitalStats")]/ul/li/text()[contains(., "Date of Birth")]',
        're_birthday': r'(\w+ \d{1,2}, \d{4})',
        'birthplace': '//div[contains(@class, "vitalStats")]/ul/li/text()[contains(., "Birthplace")]',
        're_birthplace': r'Birthplace:\s*(.*)',
        'cupsize': '',
        'ethnicity': '//div[contains(@class, "vitalStats")]/ul/li/text()[contains(., "Ethnicity")]',
        're_ethnicity': r'Ethnicity:\s*(.*)',
        'eyecolor': '',
        'haircolor': '',
        'height': '//div[contains(@class, "vitalStats")]/ul/li/text()[contains(., "Height")]',
        're_height': r'(\d+cm)',
        'weight': '//div[contains(@class, "vitalStats")]/ul/li/text()[contains(., "Weight")]',
        're_weight': r'(\d+kg)',
        'measurements': '//div[contains(@class, "vitalStats")]/ul/li/text()[contains(., "Measurements")]',
        're_measurements': r'(\d+\w+-\d+-\d+)',

        'pagination': '',
        'external_id': r'model/(.*)/'
    }

    name = 'DarkkoTVPerformer'
    network = 'DarkkoTV'

    start_url = 'https://darkkotv.com'

    paginations = [
        '/models/models_%s_d.html?g=m',
        '/models/models_%s_d.html?g=f',
        # '/models/models_%s.html?g=tf',
        # '/models/models_%s.html?g=tm',
        # '/models/models_%s.html?g=nb',
    ]

    async def start(self):
        meta = {}
        meta['page'] = self.page

        for pagination in self.paginations:
            meta['pagination'] = pagination
            yield scrapy.Request(url=self.get_next_page_url(self.start_url, self.page, meta['pagination']), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def parse(self, response, **kwargs):
        performers = self.get_performers(response)
        count = 0
        for performer in performers:
            count += 1
            yield performer

        if count:
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                meta = self.copy_meta(response)
                meta['page'] = meta['page'] + 1
                print('NEXT PAGE: ' + str(meta['pagination']) % meta['page'])
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page'], meta['pagination']), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_next_page_url(self, base, page, pagination):
        return self.format_url(base, pagination % page)
    
    def get_gender(self, response):
        meta = self.copy_meta(response)
        gender = 'Female'
        if "g=f" in meta['pagination']:
            gender = 'Female'
        if "g=m" in meta['pagination']:
            gender = 'Male'
        if "g=tf" in meta['pagination']:
            gender = 'Trans Female'
        if "g=tm" in meta['pagination']:
            gender = 'Trans Male'
        if "g=nb" in meta['pagination']:
            gender = 'Non Binary'
        return gender

    def get_performers(self, response):
        performers = response.xpath('//h4/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, meta=response.meta)

    def get_cupsize(self, response):
        if 'cupsize' in self.selector_map and self.get_selector_map('cupsize'):
            cupsize = self.process_xpath(response, self.get_selector_map('cupsize')).get()
            return cupsize.strip()
        else:
            if 'measurements' in self.selector_map:
                measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
                if measurements and re.search(r'(\d+\w+-\d+-\d+)', measurements):
                    cupsize = re.search(r'(\d+\w+)-\d+-\d+', measurements)
                    if cupsize:
                        cupsize = cupsize.group(1)
                        return cupsize.strip()
        return ''

    def get_image(self, response):
        image = super().get_image(response)
        if image and "-2x" in image:
            image = image.replace("-2x", "-4x")
            return image
        return None
    
    def get_fakeboobs(self, response):
        meta = self.copy_meta(response)
        fakeboobs = 'no'
        if "g=f" in meta['pagination']:
            boob_text = response.xpath('//div[contains(@class, "vitalStats")]/ul/li/text()[contains(., "Natural Breasts")]')
            if boob_text:
                boob_text = boob_text.get().replace("\r", "").replace("\n", "").replace("\t", "")
                if "No" in boob_text:
                    fakeboobs = 'yes'
        return fakeboobs
    
    def get_name(self, response):
        name = super().get_name(response)
        if name:
            name = name.lower()
            name = name.replace("darkko tv bio for model", "")
            return string.capwords(name.strip())
        return None