import re
import pycountry
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class NetworkOxygenEnterprisesPerformerSpider(BasePerformerScraper):

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

    selector_map = {
        'name': '//h1/text()',
        'image': '//div[@class="model-img"]//img/@src',
        'image_blob': True,
        'birthday': '//span[@class="que" and contains(text(), "DATE OF")]/following-sibling::span[@class="ans"][1]/text()',
        'birthplace': '//span[@class="que" and contains(text(), "NATIONALITY")]/following-sibling::span[@class="ans"][1]/text()',

        'pagination': '/models/?page=%s&latest=1',
        'external_id': r'model/(.*)/'
    }

    name = 'OxygenEnterprisesPerformer'
    network = 'Oxygen Enterprises'

    start_urls = [
        'https://dreamtranny.com',
        'https://jeffsmodels.com',
    ]

    def get_next_page_url(self, base, page):
        if "dreamtranny" in base:
            pagination = "/models/?page=%s&gender=trans_girl"
        elif "jeffsmodels" in base:
            pagination = "/models/?page=%s&gender=female"
        return self.format_url(base, pagination % page)

    def get_performers(self, response):
        performers = response.xpath('//div[@class="item-wrapper"]/a[1]/@href').getall()
        for performer in performers:
            if '?nats' in performer:
                performer = re.search(r'(.*)\?nats', performer).group(1)
            if '?&nats' in performer:
                performer = re.search(r'(.*)\?\&nats', performer).group(1)
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, cookies=self.cookies, headers=self.headers)

    def get_gender(self, response):
        if "dreamtranny" in response.url:
            return 'Transgender Female'
        elif "jeffsmodels" in response.url:
            return 'Female'
        return None

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

