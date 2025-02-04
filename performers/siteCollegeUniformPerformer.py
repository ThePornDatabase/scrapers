import re
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteCollegeUniformPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[@class="title_bar"]/span/text()',
        'image': '//div[contains(@class, "model_bio_page")]//img/@src0_3x',
        'image_blob': True,
        'bio': '//div[contains(@class, "model_bio_page")]//comment()[contains(., "Bio Extra") and not(contains(., "Template"))]/following-sibling::text()',
        'gender': '',
        'astrology': '//div[contains(@class, "model_bio_page")]//text()[contains(., "Astrological")]',
        're_astrology': r':(.*)',
        'birthday': '',
        'birthplace': '',
        'cupsize': '',
        'ethnicity': '',
        'eyecolor': '//div[contains(@class, "model_bio_page")]//text()[contains(., "Eye")]',
        're_eyecolor': r':(.*)',
        'fakeboobs': '',
        'haircolor': '//div[contains(@class, "model_bio_page")]//text()[contains(., "Hair")]',
        're_haircolor': r':(.*)',
        'height': '//div[contains(@class, "model_bio_page")]//text()[contains(., "Height")]',
        're_height': r'(\d+)cm',
        'measurements': '//div[contains(@class, "model_bio_page")]//text()[contains(., "Measurements")]',
        'nationality': '//div[contains(@class, "model_bio_page")]//text()[contains(., "Nationality")]',
        're_nationality': r':(.*)',
        'piercings': '',
        'tattoos': '',
        'weight': '',

        'pagination': '/models/models_%s_d.html',
        'external_id': r'model/(.*)/'
    }

    name = 'CollegeUniformPerformer'
    network = 'College Uniform'

    start_urls = [
        'https://www.college-uniform.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="update_details"]/a[1]/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, cookies=self.cookies, headers=self.headers)

    def get_measurements(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements'))
            if measurements:
                measurements = measurements.get()
                measurements = measurements.replace("\r", "").replace("\n", "").replace("\t", "")
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
                if measurements and re.search(r'(\d+\w+-\d+-\d+)', measurements):
                    cupsize = re.search(r'(\d+\w+)-\d+-\d+', measurements)
                    if cupsize:
                        cupsize = cupsize.group(1)
                        return cupsize.strip()
        return ''

    def get_astrology(self, response):
        astrology = response.xpath('//div[contains(@class, "model_bio_page")]//text()[contains(., "Astrological")]')
        if astrology:
            astrology = astrology.get()
            astrology = astrology.replace("\r", "").replace("\n", "").replace("\t", "")
            astrology = re.search(r':(.*)', astrology)
            if astrology:
                astrology = astrology.group(1)
                return astrology.strip()
        return None

    def get_eyecolor(self, response):
        eyecolor = response.xpath('//div[contains(@class, "model_bio_page")]//text()[contains(., "Eye")]')
        if eyecolor:
            eyecolor = eyecolor.get()
            eyecolor = eyecolor.replace("\r", "").replace("\n", "").replace("\t", "")
            eyecolor = re.search(r':(.*)', eyecolor)
            if eyecolor:
                eyecolor = eyecolor.group(1)
                return eyecolor.strip()
        return None

    def get_haircolor(self, response):
        haircolor = response.xpath('//div[contains(@class, "model_bio_page")]//text()[contains(., "Hair")]')
        if haircolor:
            haircolor = haircolor.get()
            haircolor = haircolor.replace("\r", "").replace("\n", "").replace("\t", "")
            haircolor = re.search(r':(.*)', haircolor)
            if haircolor:
                haircolor = haircolor.group(1)
                return haircolor.strip()
        return None

    def get_nationality(self, response):
        nationality = response.xpath('//div[contains(@class, "model_bio_page")]//text()[contains(., "Nationality")]')
        if nationality:
            nationality = nationality.get()
            nationality = nationality.replace("\r", "").replace("\n", "").replace("\t", "")
            nationality = re.search(r':(.*)', nationality)
            if nationality:
                nationality = nationality.group(1)
                return nationality.strip()
        return None

    # ~ def get_image(self, response):
        # ~ image = super().get_image(response)
        # ~ image = image.replace("-2x", "-full")
        # ~ return image
