import re
import scrapy
from tpdb.BasePerformerScraper import BasePerformerScraper


class SitePrivatePerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[contains(@class, "bio-pornstar")]/h1/text()',
        'image': '//a[contains(@class, "picture-pornstar")]/picture/source[1]/@srcset',
        'measurements': '//ul[contains(@class, "model-facts")]//em[contains(text(), "Measurements")]/following-sibling::text()',
        'height': '//ul[contains(@class, "model-facts")]//em[contains(text(), "Height")]/following-sibling::text()',
        'weight': '//ul[contains(@class, "model-facts")]//em[contains(text(), "Weight")]/following-sibling::text()',
        'birthplace': '//ul[contains(@class, "model-facts")]//em[contains(text(), "Birth")]/following-sibling::text()',
        'nationality': '//ul[contains(@class, "model-facts")]//em[contains(text(), "Nationality")]/following-sibling::text()',
        'astrology': '//ul[contains(@class, "model-facts")]//em[contains(text(), "Sign")]/following-sibling::text()',
        'haircolor': '//ul[contains(@class, "model-facts")]//em[contains(text(), "Hair")]/following-sibling::text()',
        'eyecolor': '//ul[contains(@class, "model-facts")]//em[contains(text(), "Eye")]/following-sibling::text()',
        'tattoos': '//ul[contains(@class, "model-facts")]//em[contains(text(), "Tattoos")]/following-sibling::text()',
        'piercings': '//ul[contains(@class, "model-facts")]//em[contains(text(), "Piercings")]/following-sibling::text()',
        'bio': '//ul[contains(@class, "model-facts")]/li/div/text()',
        'pagination': '/pornstars/%s/',
        'external_id': r'models\/(.*).html'
    }

    name = 'PrivatePerformer'
    network = 'Private'

    start_urls = [
        'https://www.private.com',
    ]

    def get_gender(self, response):
        bio = super().get_bio(response)
        if bio:
            bio = bio.lower()
            if " she " in bio or " her " in bio or " girl " in bio or " babe " in bio:
                return "Female"
            if " he " in bio:
                return "Male"
        return ""

    def get_performers(self, response):
        performers = response.xpath('//div[@class="model"]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer)

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

    def get_image(self, response):
        image = super().get_image(response)
        if "%" in image:
            return re.search(r'(.*?)%', image).group(1)
        if " " in image:
            return re.search(r'(.*?) ', image).group(1)
        return image

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

    def get_haircolor(self, response):
        haircolor = super().get_haircolor(response)
        if not haircolor.replace("-", "").strip():
            haircolor = ""
        return haircolor

    def get_eyecolor(self, response):
        eyecolor = super().get_eyecolor(response)
        if not eyecolor.replace("-", "").strip():
            eyecolor = ""
        return eyecolor

    def get_birthplace(self, response):
        birthplace = super().get_birthplace(response)
        if not birthplace.replace("-", "").strip():
            birthplace = ""
        return birthplace

    def get_astrology(self, response):
        astrology = super().get_astrology(response)
        if not astrology.replace("-", "").strip():
            astrology = ""
        return astrology

    def get_nationality(self, response):
        nationality = super().get_nationality(response)
        if not nationality.replace("-", "").strip():
            nationality = ""
        return nationality

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
