import html
import re
import string
from urllib.parse import urlsplit, urlunsplit, quote
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteNikkiZeeXXXPerformerSpider(BasePerformerScraper):
    name = 'NikkiZeeXXXPerformer'
    site = 'nikkizee Studio'
    parent = 'nikkizee Studio'
    network = 'nikkizee Studio'

    start_url = 'https://nikkizee.com'

    # Used for models the feed leaves with an empty gender field
    default_gender = 'Female'

    selector_map = {
        'external_id': r'',
        # An empty gender= is a superset of the default listing.  No order_by -
        # adding one can drop models that have no publish_date.
        'pagination': '/_next/data/<buildID>/models.json?page=%s&gender=',
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

    def clean_gender(self, gender):
        """The feed mixes case ('female'/'Female') and uses 'shemale' for trans models."""
        if not gender or not gender.strip():
            return self.default_gender
        gender = string.capwords(gender.strip())
        if gender == 'Shemale':
            return 'Transgender Female'
        return gender

    def get_performers(self, response):
        jsondata = response.json()
        jsondata = jsondata['pageProps']['models']['data']
        for performer in jsondata:
            if not performer.get('name'):
                continue
            item = self.init_performer()

            # Names come through the feed in block capitals
            item['name'] = string.capwords(performer['name'])

            item['image'] = self.clean_url(performer['thumb'])
            if item['image']:
                item['image_blob'] = self.get_image_blob_from_link(item['image'])

            item['gender'] = self.clean_gender(performer.get('gender'))

            # The only free-text field the feed carries
            item['bio'] = self.clean_bio(performer.get('details'))

            item['url'] = f"{self.start_url}/models/{performer['slug']}"
            item['site'] = self.site
            item['network'] = self.network

            yield item
