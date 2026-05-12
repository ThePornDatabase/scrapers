import re
import pycountry
from requests import get
import scrapy
import html

from tpdb.BasePerformerScraper import BasePerformerScraper


class NubilesPerformerSpider(BasePerformerScraper):
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
        'name': '//div[contains(@class, "model-profile-desc")]/h2/text()',
        'image': '//div[contains(@class, "model-profile")]/div[1]/img/@src',
        'bio': '//p[@class="model-bio"]//text()',
        'nationality': '//p[contains(text(), "Location")]/following-sibling::p[1]/text()',
        'birthplace': '//p[contains(text(), "Location")]/following-sibling::p[1]/text()',
        'height': '//p[contains(text(), "Height")]/following-sibling::p[1]/text()',
        'astrology': '//p[contains(text(), "Zodiac")]/following-sibling::p[1]/text()',
        'measurements': '//p[contains(text(), "Figure")]/following-sibling::p[1]/text()',
        'cupsize': '//p[contains(text(), "Figure")]/following-sibling::p[1]/text()',
        're_cupsize': r'(\d{1,3}\w+?)-\d',
        'pagination': '/model/gallery/%s',
        'external_id': r'profile/\d+/.+$'
    }

    custom_scraper_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.62',
        'CONCURRENT_REQUESTS': 1,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        "LOG_LEVEL": 'INFO',
        "EXTENSIONS": {'scrapy.extensions.logstats.LogStats': None},
    }

    name = 'NubilesPerformer'
    network = "Nubiles"
    parent = "Nubiles"

    start_urls = [
        "https://anilos.com",
        "https://badteenspunished.com",
        "https://bountyhunterporn.com",
        "https://brattysis.com",
        "https://cheatingsis.com",
        "https://cumswappingsis.com",
        "https://daddyslilangel.com",
        "https://datingmystepson.com",
        "https://deeplush.com",
        "https://detentiongirls.com",
        "https://doublepies.com",
        "https://driverxxx.com",
        "https://familyswap.xxx",
        "https://hotcrazymess.com",
        "https://momlover.com",
        "https://momsteachsex.com",
        "https://myfamilypies.com",
        "https://nfbusty.com",
        "https://nubilefilms.com",
        "https://nubiles-casting.com",
        "https://nubiles-porn.com",
        "https://nubiles.net",
        "https://nubileset.com",
        "https://nubilesunscripted.com",
        "https://petitehdporn.com",
        "https://petiteballerinasfucked.com",
        "https://princesscum.com",
        "https://realitysis.com",
        "https://stepsiblingscaught.com",
        "https://teacherfucksteens.com",
        "https://thatsitcomshow.com",
        "https://thepovgod.com",
    ]

    paginations = [
        '/model/gallery/gender/female/%s',
        '/model/gallery/gender/male/%s',
    ]
    async def start(self):
        ip = get('https://api.ipify.org').content.decode('utf8')
        print('My public IP address is: {}'.format(ip))

        meta = {}
        meta['page'] = self.page
        for link in self.start_urls:
            meta['site'] = re.search(r'https?://(.*?)\.', link).group(1)
            for pagination in self.paginations:
                meta['pagination'] = pagination
                if "female" in pagination:
                    meta['gender'] = "Female"
                else:
                    meta['gender'] = "Male"
                yield scrapy.Request(url=self.get_next_page_url(link, self.page, meta['pagination']), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def parse(self, response, **kwargs):
        meta = response.meta
        if "count" not in meta:
            perf_list = response.xpath('//div[contains(@class, "content-grid-item")]//div[@class="img-wrapper"]')
            meta['count'] = len(perf_list)

        performers = self.get_performers(response)
        count = 0
        for performer in performers:
            count += 1
            yield performer

        if count:
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                meta['page'] = meta['page'] + 1
                print('NEXT PAGE: ' + str(meta['page']))
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page'], meta['pagination'], meta['count']), callback=self.parse, meta=meta)                                     

    def get_performers(self, response):
        meta = response.meta
        performers = response.xpath('//div[contains(@class, "content-grid-item")]//div[@class="img-wrapper"]')
        for performer in performers:
            image = performer.xpath('.//img/@data-srcset')
            if image and meta['gender'] == "Female":
                image = image.get()
                image = self.extract_largest_srcset_image(image)
                meta['image'] = image
                meta['image_blob'] = self.get_image_blob_from_link(image)

            performer = performer.xpath('./a/@href').get()
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, meta=meta)

    def get_next_page_url(self, base, page, pagination, count=10):
        page = (page - 1) * count
        return self.format_url(base, pagination % page)
    
    def get_image(self, response):
        meta = response.meta
        image = super().get_image(response)
        if meta['gender'] != "Female":
            image = ""
        return image
    
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
        return ""

    def get_name(self, response):
        name = super().get_name(response)
        if name:
            name = name.strip()
            if " " not in name:
                performer_id = re.search(r'profile/(\d+)/', response.url)
                if performer_id:
                    performer_id = performer_id.group(1)
                    name = name + " " + performer_id
        return name.strip()

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

    def extract_largest_srcset_image(self, srcset: str):
        srcset = html.unescape(srcset)

        parts = [p.strip() for p in srcset.split(",") if p.strip()]

        largest_url = None
        largest_width = -1

        pattern = re.compile(r"(https?://\S+?)\s+(\d+)w")

        for part in parts:
            match = pattern.search(part)
            if not match:
                continue
            
            url, width = match.groups()
            width = int(width)

            if width > largest_width:
                largest_width = width
                largest_url = url

        return largest_url
