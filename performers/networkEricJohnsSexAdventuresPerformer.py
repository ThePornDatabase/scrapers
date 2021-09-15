import re
import scrapy
import dateparser

from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteEricJohnsSexAdventuresSpider(BasePerformerScraper):
    name = 'EricJohnsSexAdventuresPerformer'
    network = 'Eric Johns Sex Adventures'

    start_urls = [
        'https://ericjohnssexadventures.com',
    ]

    selector_map = {
        'name': '//article/section[1]/div/div/h2/text()',
        'image': '//div[@class="img-div"]/img/@src0_1x',
        'birthday': '//h3/following-sibling::p/strong[contains(text(), "Date")]/following-sibling::text()',
        'tattoos': '//h3/following-sibling::p/strong[contains(text(), "Tattoos")]/following-sibling::text()',
        'haircolor': '//h3/following-sibling::p/strong[contains(text(), "Hair")]/following-sibling::text()',
        'eyecolor': '//h3/following-sibling::p/strong[contains(text(), "Eye")]/following-sibling::text()',
        'measurements': '//h3/following-sibling::p/strong[contains(text(), "Measurements")]/following-sibling::text()',
        'astrology': '//h3/following-sibling::p/strong[contains(text(), "Astrological")]/following-sibling::text()',
        'height': '//h3/following-sibling::p/strong[contains(text(), "Height")]/following-sibling::text()',
        'weight': '//h3/following-sibling::p/strong[contains(text(), "Weight")]/following-sibling::text()',
        'birthplace': '//h3/following-sibling::p/strong[contains(text(), "Birthplace")]/following-sibling::text()',
        'pagination': '/models/models_%s_d.html',
        'external_id': r'girls/(.+)/?$'
    }

    def get_gender(self, response):
        return "Female"

    def get_performers(self, response):
        performers = response.xpath('//div[@class="content-div"]/h4/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer
            )

    def get_cupsize(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements'))
            if measurements:
                measurements = measurements.get()
                measurements = measurements.replace(" ", "").strip()
                if measurements and re.search(r'(.*-\d{2}-\d{2})', measurements):
                    measurements = re.search(r'(.*-\d{2}-\d{2})', measurements).group(1)
                    if measurements:
                        cupsize = re.search(r'(.*?)-.*', measurements).group(1)
                        if cupsize:
                            return cupsize.upper().strip()
        return ''

    def get_measurements(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements'))
            if measurements:
                measurements = measurements.get()
                measurements = measurements.replace(" ", "").strip()
                if measurements and re.search(r'\d{2}[a-zA-Z]?-\d{2}-\d{2}', measurements):
                    return measurements.strip()
        return ''

    def get_height(self, response):
        if 'height' in self.selector_map:
            height = self.process_xpath(response, self.get_selector_map('height'))
            if height:
                height = height.get()
                if "cm" in height:
                    height = re.sub(r'\s+', '', height)
                    height = re.search(r'(\d+cm)', height)
                    if height:
                        height = height.group(1)
                        return height.strip()
        return ''

    def get_weight(self, response):
        if 'weight' in self.selector_map:
            weight = self.process_xpath(response, self.get_selector_map('weight'))
            if weight:
                weight = weight.get()
                if "kg" in weight:
                    weight = re.search(r'(\d+\s?kg)', weight).group(1).strip()
                    weight = weight.replace(" ", "")
                return weight.strip()
        return ''

    def get_image(self, response):
        image = self.process_xpath(response, self.get_selector_map('image'))
        if image:
            image = self.format_link(response, image.get())
            return image.strip()
        return ''

    def get_birthday(self, response):
        birthday = self.process_xpath(response, self.get_selector_map('birthday'))
        if birthday:
            birthday = dateparser.parse(birthday.get()).isoformat()
            return birthday.strip()
        return ''
