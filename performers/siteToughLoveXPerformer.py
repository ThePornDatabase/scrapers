import html
import re
import string
from urllib.parse import urlsplit, urlunsplit, quote
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteToughLoveXPerformerSpider(BasePerformerScraper):
    name = 'ToughLoveXPerformer'
    site = 'ToughLoveX'
    parent = 'ToughLoveX'
    network = 'Radical Entertainment'

    start_url = 'https://tour.toughlovex.com'

    # Used for models the feed leaves with an empty gender field
    default_gender = 'Female'

    selector_map = {
        'external_id': r'',
        # An empty gender= is a superset of the default listing.  No order_by -
        # adding one can drop models that have no publish_date.
        'pagination': '/_next/data/<buildID>/models.json?page=%s&gender=',
    }

    # The listing carries only name/slug/thumb/gender.  Birthdate, Birthplace,
    # Eyes, Hair, Height, Weight, Measurements and Bio live on the per-model
    # endpoint, so each model is fetched individually.
    detail_url = '/_next/data/%s/models/%s.json'

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
        count = 0
        for model in response.json()['pageProps']['models']['data']:
            if not model.get('name'):
                continue
            count += 1
            meta = self.copy_meta(response)
            link = self.format_url(self.start_url, self.detail_url % (meta['buildID'], model['slug']))
            yield scrapy.Request(link, callback=self.parse_performer_detail, meta=meta, headers=self.headers, cookies=self.cookies)

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

    def clean_gender(self, gender):
        """The feed mixes case ('female'/'Female') and uses 'shemale' for trans models."""
        if not gender or not gender.strip():
            return self.default_gender
        gender = string.capwords(gender.strip())
        if gender == 'Shemale':
            return 'Transgender Female'
        return gender

    def parse_performer_detail(self, response):
        performer = response.json()['pageProps']['model']
        item = self.init_performer()

        # Names come through the feed in block capitals
        item['name'] = string.capwords(performer['name'])

        item['image'] = self.clean_url(self.get_field(performer, 'thumb'))
        if item['image']:
            item['image_blob'] = self.get_image_blob_from_link(item['image'])

        item['gender'] = self.clean_gender(performer.get('gender'))

        # 'Bio' is the real biography; 'details' is a near-always-empty CMS field
        item['bio'] = self.clean_bio(self.get_field(performer, 'Bio', 'bio', 'details'))

        birthday = self.get_field(performer, 'Birthdate', 'birthdate')
        if birthday and re.search(r'\b(19|20)\d{2}\b', birthday):
            birthday = self.parse_date(birthday, date_formats=['%Y-%m-%d', '%Y/%m/%d', '%m/%d/%Y', '%B %d, %Y', '%b %d, %Y'])
            if birthday:
                item['birthday'] = birthday.strftime('%Y-%m-%d')

        # Birthplaces here are US cities ("Salem, Oregon"), so the trailing part is
        # a state rather than a nationality - left for TPDB to resolve.
        item['birthplace'] = self.get_field(performer, 'Birthplace', 'birthplace')

        item['measurements'] = self.get_field(performer, 'Measurements', 'measurements')
        if item['measurements']:
            cupsize = re.search(r'(\d+\w+)-', item['measurements'])
            if cupsize:
                item['cupsize'] = cupsize.group(1)

        item['eyecolor'] = self.get_field(performer, 'Eyes', 'eyes')
        item['haircolor'] = self.get_field(performer, 'Hair', 'hair')

        height = self.get_field(performer, 'Height', 'height')
        if height:
            item['height'] = self.get_height(height)

        weight = self.get_field(performer, 'Weight', 'weight')
        if weight:
            item['weight'] = self.get_weight(weight)

        item['url'] = f"{self.start_url}/models/{performer['slug']}"
        item['site'] = self.site
        item['network'] = self.network

        yield item

    def get_height(self, height):
        """Accepts 5'4\", 5’4”, 5'4, 162cm, or 162 cm.  Returns 'NNNcm' or None."""
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
