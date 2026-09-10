import re
import string
import scrapy
import pycountry
true = True
false = False


from tpdb.BasePerformerScraper import BasePerformerScraper
class SiteKarupsPerformerPerformerSpider(BasePerformerScraper):

    COUNTRY_ALIASES = {
        # Major common informal names
        "United States": "United States of America",
        "USA": "United States of America",
        "U.S.A.": "United States of America",
        "United States Of America": "United States of America",

        "United Kingdom": "United Kingdom of Great Britain and Northern Ireland",
        "UK": "United Kingdom of Great Britain and Northern Ireland",
        "U.K.": "United Kingdom of Great Britain and Northern Ireland",
        "Britain": "United Kingdom of Great Britain and Northern Ireland",
        "Great Britain": "United Kingdom of Great Britain and Northern Ireland",

        "Russia": "Russian Federation",
        "Russian Federation": "Russian Federation",

        "Czech Republic": "Czechia",
        "Slovak Republic": "Slovakia",

        # Common adult-site short forms
        "South Korea": "Korea, Republic of",
        "North Korea": "Korea, Democratic People's Republic of",
        "Iran": "Iran, Islamic Republic of",
        "Venezuela": "Venezuela, Bolivarian Republic of",
        "Syria": "Syrian Arab Republic",
        "Moldova": "Moldova, Republic of",
        "Bolivia": "Bolivia, Plurinational State of",
        "Tanzania": "Tanzania, United Republic of",
        "Laos": "Lao People's Democratic Republic",
        "Vietnam": "Viet Nam",
        "Brunei": "Brunei Darussalam",
        "Cape Verde": "Cabo Verde",

        # Countries often written casually
        "Ivory Coast": "Côte d'Ivoire",
        "Congo": "Congo",
        "Republic of Congo": "Congo",
        "Democratic Republic of Congo": "Congo, The Democratic Republic of the",
        "DR Congo": "Congo, The Democratic Republic of the",
        "D.R.C.": "Congo, The Democratic Republic of the",

        "Palestine": "Palestine, State of",
        "East Timor": "Timor-Leste",
        "Macau": "Macao",

        # Regional / ambiguous but common
        "Hong Kong": "Hong Kong",
        "Taiwan": "Taiwan, Province of China",

        # Accented/variant spellings
        "Curacao": "Curaçao",
        "Curaçao": "Curaçao",
        "Saint Martin": "Saint Martin (French part)",
        "St Martin": "Saint Martin (French part)",
        "St. Martin": "Saint Martin (French part)",
        "Saint Kitts": "Saint Kitts and Nevis",
        "St Kitts": "Saint Kitts and Nevis",

        # Common short/simple forms
        "UAE": "United Arab Emirates",
        "U.A.E.": "United Arab Emirates",
        "Emirates": "United Arab Emirates",

        "Dominican": "Dominican Republic",
        "Dominica Island": "Dominica",  # not the same as Dominican Republic

        # Historical but still seen
        "Swaziland": "Eswatini",
        "Burma": "Myanmar",
    }

    # Age-gate only.  A logged-in members session was pasted here; never commit one.
    cookies = {"warningHidden": "hide"}

    selector_map = {
        'birthplace': '//section[@class="model-section"]//span[contains(text(), "Place of Birth")]/following-sibling::span/text()',
        'height': '//section[@class="model-section"]//span[contains(text(), "Height")]/following-sibling::span/text()',
        'measurements': '//section[@class="model-section"]//span[contains(text(), "Measurements")]/following-sibling::span/text()',
        'nationality': '//section[@class="model-section"]//span[contains(text(), "Place of Birth")]/following-sibling::span/text()',

        'pagination': '/models/page%s.html',
        'external_id': r'model/(.*)/'
    }

    name = 'KarupsPerformer'
    network = 'Karups'

    start_urls = [
        'https://www.karups.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        meta = self.copy_meta(response)
        performers = response.xpath('//div[@class="item-inside"]')
        for performer in performers:
            perf_url = performer.xpath('./a/@href').get()
            perf_id = re.search(r'-(\d+)', perf_url).group(1)
            perf_name = performer.xpath('.//span[@class="title"]/text()').get().strip()
            if " " not in perf_name:
                perf_name = perf_name + " " + perf_id
            meta['name'] = string.capwords(perf_name)
            meta['url'] = self.format_link(response, perf_url)
            meta['id'] = perf_id

            image = performer.xpath('.//img/@src').get()
            image_id = re.search(r'(\d+)', image)
            if image and image not in response.url and image_id:
                meta['image'] = self.format_link(response, image)
                meta['image_blob'] = self.get_image_blob_from_link(meta['image'])

            yield scrapy.Request(url=self.format_link(response, perf_url), callback=self.parse_performer, meta=meta)

    def get_measurements(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
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

    def get_height(self, response):
        if 'height' in self.selector_map:
            height = self.process_xpath(response, self.get_selector_map('height')).get()
            if height:
                str_height = re.findall(r'(\d{1,2})', height)
                if len(str_height):
                    feet = int(str_height[0])
                    if len(str_height) > 1:
                        inches = int(str_height[1])
                    else:
                        inches = 0
                    heightcm = str(round(((feet*12)+inches) * 2.54)) + "cm"
                    return heightcm.strip()
        return ''

    def get_birthplace_code(self, response):
        birthplace = self.get_birthplace(response)
        if not birthplace:
            return ""

        birthplace = birthplace.strip()
        country = pycountry.countries.get(name=birthplace)

        if not country and birthplace in self.COUNTRY_ALIASES:
            alias = self.COUNTRY_ALIASES[birthplace]
            country = pycountry.countries.get(name=alias)

        if not country:
            try:
                matches = pycountry.countries.search_fuzzy(birthplace)
                if matches:
                    country = matches[0]
            except LookupError:
                country = None

        return country.alpha_2 if country else ""
