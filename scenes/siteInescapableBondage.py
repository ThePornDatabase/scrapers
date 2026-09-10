import re

import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper

# The tour is a static template with no API. Scene links live in the paginated
# /pageN.html listings; each listing block carries the title, model and date,
# and the scene page adds the description, duration and media URLs. The date
# only exists on the listing, so it rides along in meta.


class SiteInescapableBondageSpider(BaseSceneScraper):
    name = 'InescapableBondage'
    network = 'Inescapable Bondage'
    parent = 'Inescapable Bondage'
    site = 'Inescapable Bondage'

    start_url = 'https://www.inescapablebondage.com'

    custom_scraper_settings = {
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 30,
        'CONCURRENT_REQUESTS': 2,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 2,
        'DOWNLOAD_DELAY': 1,
        'RETRY_HTTP_CODES': [429, 408, 500, 502, 503, 504, 522, 524],
        'RETRY_PRIORITY_ADJUST': -1,
    }

    selector_map = {
        'title': '//div[@id="videotitle"]//text()',
        'description': '//div[@id="videodetailsright"]//text()',
        'date': '',
        'image': '',
        'performers': '//div[@id="videomodel"]//text()',
        'tags': '',
        'duration': '//div[@id="videospecs"]//text()',
        'trailer': '',
        'external_id': r'-(\d+)\.html',
        'pagination': '/page%s.html',
        'type': 'Scene',
    }

    # Listing anchors that wrap a real scene card. The tour also renders a
    # "Featuring:" sidebar linking to /videos/ pages already covered by the
    # listing, so anchoring on bigcontenttitle both selects the cards and
    # de-duplicates in one step.
    scene_block_xpath = '//a[contains(@href,"/videos/")][.//div[@class="bigcontenttitle"]]'

    async def start(self):
        yield scrapy.Request(self.get_next_page_url(self.start_url, self.page),
                             callback=self.parse,
                             meta={'page': self.page},
                             headers=self.headers,
                             cookies=self.cookies,
                             dont_filter=True)

    def parse(self, response, **kwargs):
        page = response.meta.get('page', 1)
        blocks = response.xpath(self.scene_block_xpath)
        self.logger.info(f'Listing page {page}: {len(blocks)} scenes')

        for block in blocks:
            link = block.xpath('./@href').get()
            if not link or not re.search(self.get_selector_map('external_id'), link):
                continue

            meta = {
                'page': page,
                'listing_title': self.text_of(block, './/div[@class="bigcontenttitle"]//text()'),
                'listing_performers': self.text_of(block, './/div[@class="bigcontentmodel"]//text()'),
                'listing_date': self.text_of(block, './/div[@class="bigcontentdate"]//text()'),
                'listing_image': block.xpath('.//img/@src').get() or '',
            }
            yield scrapy.Request(self.format_link(response, link),
                                 callback=self.parse_scene,
                                 meta=meta,
                                 headers=self.headers)

        # Pagination runs out silently: page6.html and beyond still return 200
        # with the sidebar links but no scene cards, so an empty page is the
        # only reliable stop signal.
        if blocks and page < self.limit_pages:
            yield scrapy.Request(self.get_next_page_url(self.start_url, page + 1),
                                 callback=self.parse,
                                 meta={'page': page + 1},
                                 headers=self.headers,
                                 dont_filter=True)

    def parse_scene(self, response):
        item = self.init_scene()

        item['id'] = self.get_id(response)
        if not item['id']:
            self.logger.warning(f'No scene id in {response.url}')
            return

        item['title'] = (self.text_of(response, self.get_selector_map('title'))
                         or response.meta.get('listing_title', ''))
        item['description'] = self.text_of(response, self.get_selector_map('description'))
        item['date'] = self.get_date(response)
        item['url'] = response.url

        item['performers'] = self.get_performers(response)
        item['tags'] = []

        item['duration'] = self.get_duration(response)

        item['image'] = self.get_image(response)
        item['image_blob'] = self.get_image_blob_from_link(item['image']) if item['image'] else None

        item['trailer'] = self.get_trailer(response)
        item['site'] = self.site
        item['parent'] = self.parent
        item['network'] = self.network
        item['type'] = 'Scene'

        yield self.check_item(item, self.days)

    # ------------------------------------------------------------------ #
    # Field extraction                                                     #
    # ------------------------------------------------------------------ #

    def get_id(self, response):
        match = re.search(self.get_selector_map('external_id'), response.url)
        return match.group(1) if match else None

    def get_date(self, response):
        # "May 31, 2026" — listing only; the scene page carries no date at all.
        listing_date = response.meta.get('listing_date', '')
        if not listing_date:
            return None
        parsed = self.parse_date(listing_date, date_formats=['%b %d, %Y'])
        return parsed.isoformat()[:10] if parsed else None

    def get_performers(self, response):
        # The listing gives a bare "Emily Marilyn, Mina Meow"; the scene page
        # prefixes a category ("Femdom: Mina Meow"), so prefer the listing and
        # strip the prefix when falling back.
        names = response.meta.get('listing_performers', '')
        if not names:
            names = self.text_of(response, self.get_selector_map('performers'))
            names = re.sub(r'^[^:]{1,20}:\s*', '', names)
        return [n.strip() for n in names.split(',') if n.strip()]

    def get_duration(self, response):
        # "15min. 22sec. - Photos: -1 photos". The jwplayer 'duration' field is
        # hardcoded to 15 on every scene, so it can't be used.
        specs = self.text_of(response, self.get_selector_map('duration'))
        match = re.search(r'(?:(\d+)\s*hr\.?)?\s*(\d+)\s*min\.?\s*(\d+)\s*sec\.?', specs, re.IGNORECASE)
        if not match:
            return ''
        hours = int(match.group(1) or 0)
        return str(hours * 3600 + int(match.group(2)) * 60 + int(match.group(3)))

    def get_image(self, response):
        match = re.search(r"'image':\s*'([^']+)'", response.text)
        if match:
            return match.group(1)
        return response.meta.get('listing_image', '')

    def get_trailer(self, response):
        match = re.search(r"'file':\s*\"([^\"]+)\"", response.text)
        return match.group(1) if match else ''

    @staticmethod
    def text_of(node, xpath):
        """Collapse an xpath's text nodes into a single clean string.

        The template pads every field with tabs and newlines, so a plain
        .get() would return e.g. '\\n\\t\\t\\t\\tImpact Play            '.
        """
        if not xpath:
            return ''
        return ' '.join(''.join(node.xpath(xpath).getall()).split())
