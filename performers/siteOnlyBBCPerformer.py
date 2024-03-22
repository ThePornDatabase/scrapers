import re
import scrapy
from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteOnlyBBCPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//h2/a/following-sibling::text()',
        'image': '//img[contains(@class,"model_bio_thumb")]/@src0_1x',

        'height': '//span[@class="model_bio_heading"]/following-sibling::text()[contains(.,"Height")]',
        'eyecolor': '//span[@class="model_bio_heading"]/following-sibling::text()[contains(.,"Eye Color")]',
        'haircolor': '//span[@class="model_bio_heading"]/following-sibling::text()[contains(.,"Hair Color")]',
        'measurements': '//span[@class="model_bio_heading"]/following-sibling::text()[contains(.,"Measurements")]',
        'piercings': '//span[@class="model_bio_heading"]/following-sibling::text()[contains(.,"Piercings")]',
        'astrology': '//span[@class="model_bio_heading"]/following-sibling::text()[contains(.,"Astrological")]',
        'bio': '//span[@class="model_bio_heading"]/following-sibling::comment()[contains(.,"Bio Extra Field") and not(contains(.,"Accompanying"))]/following-sibling::text()',

        'pagination': '/tour/models/models_%s_d.html?g=f',
        'external_id': 'models/(.+).html$'
    }

    name = 'OnlyBBCPerformer'
    network = 'Only BBC'

    start_urls = [
        'https://www.onlybbc.com'
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[@class="model"]/div/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer
            )

    def get_name(self, response):

        name = self.process_xpath(response, self.get_selector_map('name')).get().strip()
        name = re.sub(r'[^a-zA-Z0-9 ]', '', name)
        return name.strip()

    def get_gender(self, response):
        return "Female"

    def get_height(self, response):
        height = super().get_height(response)
        if height:
            tot_inches = 0
            if re.search(r'(\d+)[\'\"]', height):
                feet = re.search(r'(\d+)\'', height)
                if feet:
                    feet = feet.group(1)
                    tot_inches = tot_inches + (int(feet) * 12)
                inches = re.search(r'\d+?\'(\d+)', height)
                if inches:
                    inches = inches.group(1)
                    inches = int(inches)
                    tot_inches = tot_inches + inches
                height = str(int(tot_inches * 2.54)) + "cm"
                return height
        return None

    def get_eyecolor(self, response):
        if 'eyecolor' in self.selector_map:
            eyecolor = self.process_xpath(response, self.get_selector_map('eyecolor')).get()
            if eyecolor:
                eyecolor = eyecolor.replace("&nbsp;", "").replace("\n", "")
                eyecolor = re.search(r'Eye Color:\s+(.*?)\s{3}', eyecolor)
                if eyecolor:
                    eyecolor = eyecolor.group(1)
                    return eyecolor.strip()
        return ''

    def get_haircolor(self, response):
        if 'haircolor' in self.selector_map:
            haircolor = self.process_xpath(response, self.get_selector_map('haircolor')).get()
            if haircolor:
                haircolor = haircolor.replace("&nbsp;", "").replace("\n", "")
                haircolor = re.search(r'Hair Color:\s+(.*?)\s{3}', haircolor)
                if haircolor:
                    haircolor = haircolor.group(1)
                    return haircolor.strip()
        return ''

    def get_piercings(self, response):
        if 'piercings' in self.selector_map:
            piercings = self.process_xpath(response, self.get_selector_map('piercings')).get()
            if piercings:
                piercings = piercings.replace("&nbsp;", "").replace("\n", "")
                piercings = re.search(r'Piercings:\s+(.*?)\s{3}', piercings)
                if piercings:
                    piercings = piercings.group(1)
                    return piercings.strip()
        return ''

    def get_measurements(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements:
                measurements = measurements.replace("\n", "").replace("\r", "")
                measurements = re.search('Measurements:(.*)', measurements).group(1)
                return measurements.strip()
        return ''

    def get_cupsize(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements:
                measurements = measurements.replace("\n", "").replace("\r", "")
                measurements = re.search('Measurements:(.*)', measurements).group(1)
                if measurements:
                    measurements = measurements.strip()
                    if re.search(r'(\d+\w+)-', measurements):
                        cupsize = re.search(r'(\d+\w+)-', measurements).group(1)
                        return cupsize.strip().upper()
        return ''

    def get_astrology(self, response):
        if 'astrology' in self.selector_map:
            astrology = self.process_xpath(response, self.get_selector_map('astrology')).get()
            if astrology:
                astrology = astrology.replace("\n", "").replace("\r", "")
                astrology = re.search('Sign:(.*)', astrology).group(1)
                return astrology.strip()
        return ''
