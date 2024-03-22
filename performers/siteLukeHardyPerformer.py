import re
import string
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteLukeHardyPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[@class="modelBioBlock"]/h2/text()',
        'image': '//div[@class="bioPic"]/img/@src',
        'image_blob': True,
        'bio': '//div[@class="modelBioBlock"]/div[@class="aboutGirl"]/p/text()',
        'astrology': '//div[@class="modelBioBlock"]//li[contains(text(), "Sign:")]/span/text()',
        'height': '//div[@class="modelBioBlock"]//li[contains(text(), "Height:")]/span/text()',
        'measurements': '//div[@class="modelBioBlock"]//li[contains(text(), "Measurements:")]/span/text()',

        'pagination': '',
        'external_id': r'model/(.*)/'
    }

    name = 'LukeHardyPerformer'
    network = 'Luke Hardy'

    cookies = {"name": "_warning_page", "value": "1"}

    start_urls = [
        '',
    ]

    def start_requests(self):
        meta = {}

        for c in string.ascii_uppercase:
            link = f"https://www.lukehardyxxx.com/army/models.php?letter={c}"
        # ~ link = f"https://www.lukehardyxxx.com/army/models.php?letter=A"
            yield scrapy.Request(link, callback=self.get_performers, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="modelPhoto"]/a/@href').getall()
        for performer in performers:
            if "model-" in performer:
                link = f"https://www.lukehardyxxx.com/army/{performer}"
                yield scrapy.Request(link, callback=self.parse_performer, cookies=self.cookies, headers=self.headers)

    def get_measurements(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            measurements = measurements.replace(" ", "")
            if measurements and re.search(r'(\d+\w+-\d+-\d+)', measurements):
                measurements = re.search(r'(\d+\w+-\d+-\d+)', measurements).group(1)
                return measurements.strip()
        return ''

    def get_cupsize(self, response):
        if 'cupsize' in self.selector_map and self.get_selector_map('cupsize'):
            cupsize = self.process_xpath(response, self.get_selector_map('cupsize')).get()
            return cupsize.strip()
        else:
            if 'measurements' in self.selector_map:
                measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
                measurements = measurements.replace(" ", "")
                if measurements and re.search(r'(\d+\w+-\d+-\d+)', measurements):
                    cupsize = re.search(r'(\d+\w+)-\d+-\d+', measurements)
                    if cupsize:
                        cupsize = cupsize.group(1)
                        return cupsize.strip()
        return ''

    def get_height(self, response):
        height = super().get_height(response)
        height = height.lower().replace(" ", "").replace("feet", "'").replace("and", "").replace("inches", "\"")
        if "'" in height:
            height = re.sub(r'[^0-9\']', '', height)
            feet = re.search(r'(\d+)\'', height)
            if feet:
                feet = feet.group(1)
                feet = int(feet) * 12
            else:
                feet = 0
            inches = re.search(r'\'(\d+)', height)
            if inches:
                inches = inches.group(1)
                inches = int(inches)
            else:
                inches = 0
            return str(int((feet + inches) * 2.54)) + "cm"
        return None

    def get_image(self, response, path=None):
        force_update = self.settings.get('force_update')
        if force_update:
            force_update = True
        force_fields = self.settings.get('force_fields')
        if force_fields:
            force_fields = force_fields.split(",")

        if not force_update or (force_update and "image" in force_fields):
            if 'image' in self.get_selector_map():
                image = self.get_element(response, 'image', 're_image')
                if isinstance(image, list):
                    image = image[0]
                image = image.replace(" ", "%20")
                if path:
                    return self.format_url(path, image)
                else:
                    return f"https://www.lukehardyxxx.com/army/{image}"
            return ''
