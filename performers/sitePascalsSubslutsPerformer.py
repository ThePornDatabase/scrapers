import html
import re
import string
from urllib.parse import urlsplit, urlunsplit, quote
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


# Template for Next.js sites that serve their model list as JSON from
# /_next/data/<buildID>/models.json.  The buildID changes with every site
# deploy, so it is scraped from the homepage on each run and substituted
# into the pagination string.
#
# Combines the field handling from the post-2024 buildID performer scrapers
# (DireDesires, NylonPerv, XFUL, LegendaryX, LucidFlix, ZFilmz, Jav888,
# FreakMobMedia, BlackBullChallenge, LezKey, BenefitMonkey, MongerInAsia).
# The JSON key names vary between sites ("Eyes" vs "Eye Color", "Birthdate"
# vs "birthdate", "Born" vs "location"), so each field is looked up against
# every variant seen so far.
#
# Fill in: name/site/parent/network, start_url, default_gender, and check
# the pagination sort parameters and the JSON keys against a real response.
class SitePascalsSubslutsPerformerSpider(BasePerformerScraper):
    name = 'PascalsSubslutsPerformer'
    site = 'PascalsSubsluts'
    parent = 'PascalsSubsluts'
    network = 'PascalsSubsluts'

    start_url = 'https://www.pascalssubsluts.com'

    # Used when the JSON has no gender field
    default_gender = 'Female'
    # Set if the whole site is one ethnicity (e.g. MongerInAsia used 'Asian'), else leave None
    default_ethnicity = None

    selector_map = {
        'external_id': r'',
        # order_by has been seen as publish_date, publish_dates, and name (with sort_by=asc)
        'pagination': '/_next/data/<buildID>/sluts.json?page=%s&order_by=publish_date&sort_by=desc',
    }

    async def start(self):
        meta = {}
        meta['page'] = self.page
        yield scrapy.Request(self.start_url, callback=self.start_requests_2, meta=meta, headers=self.headers, cookies=self.cookies)

    def start_requests_2(self, response):
        meta = self.copy_meta(response)
        buildId = re.search(r'\"buildId\":\"(.*?)\"', response.text)
        if buildId:
            meta['buildID'] = buildId.group(1)
            link = self.get_next_page_url(self.start_url, self.page, meta['buildID'])
            yield scrapy.Request(link, callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

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
                print('NEXT PAGE: ' + str(meta['page']))
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page'], meta['buildID']), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_next_page_url(self, base, page, buildID):
        pagination = self.get_selector_map('pagination')
        pagination = pagination.replace("<buildID>", buildID)
        return self.format_url(base, pagination % page)

    @staticmethod
    def clean_url(url):
        """Percent-encode unsafe characters (e.g. spaces) in the URL path."""
        if not url:
            return url
        parts = urlsplit(url)
        return urlunsplit(parts._replace(path=quote(parts.path, safe='/')))


    @staticmethod
    def clean_bio(text):
        """Strip HTML from a bio, keeping <br> and </p> as line breaks."""
        if not text:
            return None
        text = re.sub(r'<\s*br\s*/?\s*>', '\n', text, flags=re.IGNORECASE)
        text = re.sub(r'</\s*(p|div|li)\s*>', '\n', text, flags=re.IGNORECASE)
        text = re.sub(r'<[^>]+>', '', text)
        text = html.unescape(text).replace('\xa0', ' ')
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'[ \t]*\n[ \t]*', '\n', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip() or None
    
    @staticmethod
    def get_field(performer, *keys):
        """Return the first non-empty value found under any of the given keys."""
        for key in keys:
            if key in performer and performer[key]:
                value = performer[key]
                if isinstance(value, str):
                    value = value.strip()
                if value:
                    return value
        return None

    def get_performers(self, response):
        jsondata = response.json()
        jsondata = jsondata['pageProps']['models']['data']
        for performer in jsondata:
            item = self.init_performer()

            item['name'] = self.get_field(performer, 'name')

            item['image'] = self.clean_url(self.get_field(performer, 'thumb'))
            if item['image']:
                item['image_blob'] = self.get_image_blob_from_link(item['image'])

            gender = self.get_field(performer, 'gender')
            if gender:
                item['gender'] = string.capwords(gender)
            else:
                item['gender'] = self.default_gender

            # The Age field is free text: sometimes a full date ("November 11, 1986",
            # "Nov 11, 1986"), sometimes just a number of years ("32", "Dirty 30").
            # Only parse values that contain a four-digit year, since dateparser
            # would otherwise turn a bare "32" into the year 2032.
            # MongerInAsia returned a 1969 epoch date for unknown birthdays.
            birthday = self.get_field(performer, 'Birthdate', 'birthdate', 'Age')
            if birthday and re.search(r'\b(19|20)\d{2}\b', birthday) and "1969" not in birthday:
                birthday = self.parse_date(birthday, date_formats=['%Y-%m-%d', '%Y/%m/%d', '%m/%d/%Y', '%m-%d-%Y', '%B %d, %Y', '%b %d, %Y', '%B %d %Y', '%b %d %Y', '%d %B %Y', '%d %b %Y', '%B %Y', '%b %Y'])
                if birthday:
                    item['birthday'] = birthday.strftime('%Y-%m-%d')

            item['birthplace'] = self.get_field(performer, 'Born', 'born', 'location')
            if item['birthplace'] and "," in item['birthplace']:
                nationality = re.search(r', ([^,]*)$', item['birthplace'])
                if nationality:
                    item['nationality'] = nationality.group(1).strip()

            if self.get_field(performer, 'Nationality', 'nationality'):
                item['nationality'] = self.get_field(performer, 'Nationality', 'nationality')

            if self.get_field(performer, 'Ethnicity', 'ethnicity'):
                item['ethnicity'] = self.get_field(performer, 'Ethnicity', 'ethnicity')

            bio = self.get_field(performer, 'Bio', 'bio')
            if bio:
                item['bio'] = self.clean_bio(bio)

            item['measurements'] = self.get_field(performer, 'Measurements', 'measurements')
            if item['measurements']:
                cupsize = re.search(r'(\d+\w+)-', item['measurements'])
                if cupsize:
                    item['cupsize'] = cupsize.group(1)

            item['astrology'] = self.get_field(performer, 'Zodiac', 'zodiac', 'astrology', 'Astrological Sign', 'astrological_sign')

            item['eyecolor'] = self.get_field(performer, 'Eyes', 'Eye Color', 'eyes', 'eye_color')
            item['haircolor'] = self.get_field(performer, 'Hair', 'Hair Color', 'hair', 'hair_color')

            height = self.get_field(performer, 'Height', 'height')
            if height:
                item['height'] = self.get_height(height)

            weight = self.get_field(performer, 'Weight', 'weight')
            if weight:
                item['weight'] = self.get_weight(weight)

            if self.default_ethnicity:
                item['ethnicity'] = self.default_ethnicity

            item['url'] = f"{self.start_url}/sluts/{performer['slug']}"
            item['site'] = self.site
            item['network'] = self.network

            yield item

    def get_height(self, height):
        """Accepts 5'4", 5’4”, 5'4, 162cm, or 162 cm.  Returns 'NNNcm' or None."""
        if not height:
            return None
        height = str(height).replace("’", "'").replace("‘", "'").replace("”", '"').replace("“", '"')
        if "'" in height:
            height = re.sub(r'[^0-9\']', '', height)
            feet = re.search(r'(\d+)\'', height)
            feet = int(feet.group(1)) * 12 if feet else 0
            inches = re.search(r'\'(\d+)', height)
            inches = int(inches.group(1)) if inches else 0
            if feet or inches:
                return str(int((feet + inches) * 2.54)) + "cm"
            return None
        if re.search(r'cm', height, re.IGNORECASE):
            cm = re.search(r'(\d+)', height)
            if cm:
                return cm.group(1) + "cm"
        return None

    def get_weight(self, weight):
        """Accepts '120 lbs', '120', '54 kilos', or '54kg'.  Returns 'NNkg' or None."""
        if not weight:
            return None
        weight = str(weight).lower()
        number = re.search(r'(\d+)', weight)
        if not number:
            return None
        number = int(number.group(1))
        if "kilo" in weight or "kg" in weight:
            return str(number) + "kg"
        return str(int(number * .453592)) + "kg"
