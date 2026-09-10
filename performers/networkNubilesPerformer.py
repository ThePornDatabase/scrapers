import re
import json
import hashlib
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
        # Serialize to one request at a time across ALL domains and add a real gap
        # between hits — nubiles drops connections when 32 sites x 2 paginations fire
        # back-to-back.
        'CONCURRENT_REQUESTS': 1,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'DOWNLOAD_DELAY': 5,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 5,
        'AUTOTHROTTLE_MAX_DELAY': 30,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,
        "LOG_LEVEL": 'INFO',
        "EXTENSIONS": {'scrapy.extensions.logstats.LogStats': None},
        'DOWNLOADER_MIDDLEWARES': {
            'tpdb.middlewares.TpdbPerformerDownloaderMiddleware': 543,
            # Disabled — proxy routes requests through an IP nubiles.net blocks,
            # causing TLS ConnectionLost. Match scenes-scraper config.
            'tpdb.custommiddlewares.CustomProxyMiddleware': None,
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
        },
    }

    # Must match the UA Scrapy actually sends (forced upstream). Used when posting
    # /turnstile/verify so the server-side session UA fingerprint stays consistent.
    USER_AGENT = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 '
                  'Edg/107.0.1418.62')

    # Nubiles.net drops the connection if these browser headers are missing.
    headers = {
        'User-Agent': USER_AGENT,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Sec-Ch-Ua': '"Microsoft Edge";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
    }

    cookies = {'18-plus-modal': 'hidden'}

    name = 'NubilesPerformer'
    network = "Nubiles"
    parent = "Nubiles"

    start_urls = [
        "https://anilos.com",
        ## "https://badteenspunished.com",
        "https://bountyhunterporn.com",
        "https://brattymilf.com",
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

        for link in self.start_urls:
            base = link.rstrip('/')
            site = re.search(r'https?://(.*?)\.', link).group(1)
            for pagination in self.paginations:
                # The server bounces /model/gallery/... -> /turnstile/challenge -> back.
                # Follow redirects manually so the dupefilter doesn't block the second hop.
                meta = {
                    'page': self.page,
                    'site': site,
                    'pagination': pagination,
                    'gender': 'Female' if 'female' in pagination else 'Male',
                    'base_link': base,
                    'dont_redirect': True,
                    'handle_httpstatus_list': [301, 302, 303, 307, 308],
                }
                yield scrapy.Request(
                    url=self.get_next_page_url(link, self.page, pagination),
                    callback=self.captcha_or_parse,
                    meta=meta,
                    headers=self.headers,
                    cookies=self.cookies,
                )

    def captcha_or_parse(self, response):
        """Follow redirects manually, intercept Security Check page if served,
        otherwise defer to the normal parse() flow."""
        if response.status in (301, 302, 303, 307, 308):
            location = response.headers.get('Location', b'').decode('latin1')
            if location.startswith('/'):
                location = response.meta.get('base_link', '') + location
            yield scrapy.Request(
                url=location,
                callback=self.captcha_or_parse,
                meta=dict(response.meta),
                headers=self.headers,
                dont_filter=True,
            )
            return
        if 'turnstileConfig' in response.text and 'Security Check' in response.text:
            yield from self._solve_captcha(response)
        else:
            yield from self.parse(response)

    def _solve_captcha(self, response):
        m = re.search(r"var\s+turnstileConfig\s*=\s*(\{.*?\});", response.text)
        if not m:
            self.logger.error("Captcha page detected but turnstileConfig not parseable")
            return
        try:
            config = json.loads(m.group(1))
        except ValueError as e:
            self.logger.error(f"turnstileConfig is not valid JSON: {e}")
            return
        try:
            nonce = self._solve_pow(config['challenge'], config['difficulty'])
        except Exception as e:
            self.logger.error(f"PoW solve failed: {e}")
            return

        base = response.meta.get('base_link') or (
            f"{response.url.split('/')[0]}//{response.url.split('/')[2]}"
        )
        verify_url = base + '/turnstile/verify'
        payload = {
            'nonce': str(nonce),
            'timestamp': config['timestamp'],
            'difficulty': config['difficulty'],
            'environmentChecks': {
                'screenWidth': 1920, 'screenHeight': 1080,
                'hasCanvas': True, 'hasWebGL': True, 'colorDepth': 24,
                'timezoneOffset': 300, 'languages': 'en-US,en',
                'platform': 'Win32', 'cookieEnabled': True,
            },
            'returnTo': config['returnTo'],
        }
        verify_headers = dict(self.headers) if self.headers else {}
        verify_headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': self.USER_AGENT,
            'Referer': response.url,
            'Origin': base,
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
        })

        self.logger.info(f"Solved PoW for {base} (nonce={nonce}); submitting verify")
        yield scrapy.Request(
            url=verify_url,
            method='POST',
            body=json.dumps(payload),
            headers=verify_headers,
            callback=self._after_verify,
            meta=dict(response.meta),
            dont_filter=True,
        )

    def _after_verify(self, response):
        try:
            result = response.json()
        except ValueError:
            self.logger.error(f"Non-JSON from /turnstile/verify: {response.text[:200]}")
            return
        if not result.get('success'):
            self.logger.error(f"Verification rejected: {result}")
            return

        base = response.meta.get('base_link', '')
        redirect_to = result.get('redirectTo') or response.meta.get('pagination', '/').replace('%s', '0')
        if not redirect_to.startswith('http'):
            redirect_to = base + redirect_to

        self.logger.info(f"Verified, re-requesting {redirect_to}")
        # Back through captcha_or_parse rather than straight to parse: some sites
        # redirect their model gallery elsewhere after verification (brattymilf.com
        # sends /model/gallery/... to /model/first-update/...), and this request
        # still carries dont_redirect from start(), so parse would be handed a
        # bodyless 301 and silently yield nothing.
        yield scrapy.Request(
            url=redirect_to,
            callback=self.captcha_or_parse,
            meta=response.meta,
            headers=self.headers,
            dont_filter=True,
        )

    @staticmethod
    def _solve_pow(challenge, difficulty):
        """Find a nonce such that SHA-256(challenge + ':' + nonce) has `difficulty` leading zero bits."""
        target = 1 << (256 - difficulty)
        nonce = 0
        while True:
            h = hashlib.sha256(f"{challenge}:{nonce}".encode()).digest()
            if int.from_bytes(h, 'big') < target:
                return nonce
            nonce += 1

    def parse(self, response, **kwargs):
        meta = self.copy_meta(response)
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
        meta = self.copy_meta(response)
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
        meta = self.copy_meta(response)
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
