import re

import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper

# Everything is scraped from the paginated preview grid — the individual
# /x-new/new-set.php pages add nothing the listing doesn't already carry.
#
# Grid tiles come in two kinds. Photo galleries show "60 photos"; videos show
# "5:02 video", sometimes as "36 photos; 3:48 video" on a combined set. Matching
# the duration text is what separates the scenes from the galleries, so the
# regex must NOT be anchored or those combined sets are silently skipped.
DURATION_RE = r'\d+(:\d{2}){1,2} video'

# Set number prefixing the title ("1002 Kat Snow", "379_Serene Isley 2").
_LEADING_SET_NUM = re.compile(r'^\d+[\s_]+')
# Trailing number, either a set number ("Anabelle Pync 606") or a sequence
# marker ("Angelique Kithos 2").
_TRAILING_NUM = re.compile(r'[\s_]+\d+$')
# "Bonus Update - Carissa Montgomery", "Guest Gallery - Jackie Bound".
# Separator varies across the archive: 172 use "_", 141 use "-", 2 use ":".
_TITLE_PREFIX = re.compile(
    r'^(?:bonus(?:\s+\w+)?\s+update|guest\s+gallery|guest\s+feature)\s*[-_:]\s*',
    re.IGNORECASE)


class SiteDGBondageSpider(BaseSceneScraper):
    name = 'DGBondage'
    network = 'DGBondage'
    parent = 'DGBondage'
    site = 'DGBondage'

    start_url = 'https://dgbondage.com'

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
        'title': './/div[@class="album-block"]/h4//text()',
        'description': './/p[@class="setdesc"]//text()',
        'date': '',
        'image': './/img/@src',
        'performers': '',
        'tags': '',
        'duration': f'.//p[re:test(normalize-space(.), "{DURATION_RE}")]//text()',
        'trailer': '',
        'external_id': r'setid=(\d+)',
        'pagination': '/x-new/new-preview-grid.php?page=%s&user=dgbondage.com',
        'type': 'Scene',
    }

    # The eight "Featured Update" tiles (li.feat) are a promo rail repeated
    # verbatim on all 101 pages, so they are excluded — including them would
    # emit the same eight sets 101 times each. They never appear as regular
    # tiles, and their <h4> disagrees with their thumbnail's alt text, so their
    # metadata isn't trustworthy anyway.
    scene_block_xpath = (
        '//li[contains(@class,"prevgrid")][not(contains(@class,"feat"))]'
        f'[.//p[re:test(normalize-space(.), "{DURATION_RE}")]]'
    )
    # Any non-featured tile, video or gallery. Used only to detect the end of
    # the listing: page 101 is the last page with content but happens to hold
    # no videos, so counting videos would stop the crawl one page early.
    any_block_xpath = '//li[contains(@class,"prevgrid")][not(contains(@class,"feat"))]'

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
        total = len(response.xpath(self.any_block_xpath))
        self.logger.info(f'Page {page}: {len(blocks)} videos of {total} sets')

        for block in blocks:
            item = self.parse_block(response, block)
            if item:
                yield self.check_item(item, self.days)

        if total and page < self.limit_pages:
            yield scrapy.Request(self.get_next_page_url(self.start_url, page + 1),
                                 callback=self.parse,
                                 meta={'page': page + 1},
                                 headers=self.headers,
                                 dont_filter=True)

    def parse_block(self, response, block):
        link = block.xpath('.//a/@href').get() or ''
        match = re.search(self.get_selector_map('external_id'), link)
        if not match:
            self.logger.warning(f'No setid in listing link {link!r}')
            return None

        item = self.init_scene()
        item['id'] = match.group(1)
        item['url'] = self.format_link(response, link)

        item['title'] = self.text_of(block, self.get_selector_map('title'))
        item['description'] = self.text_of(block, self.get_selector_map('description'))
        item['performers'] = self.performers_from_title(item['title'])
        item['tags'] = []

        item['duration'] = self.duration_from_block(block)

        image = block.xpath(self.get_selector_map('image')).get()
        item['image'] = self.format_link(response, image) if image else ''
        item['image_blob'] = self.get_image_blob_from_link(item['image']) if item['image'] else None

        # Neither the listing nor the set page carries a date, so leave it
        # unset — the pipeline logs these as "Calculated".
        item['date'] = None
        item['trailer'] = ''
        item['tags'] = ['Bondage']
        item['site'] = self.site
        item['parent'] = self.parent
        item['network'] = self.network
        item['type'] = 'Scene'

        return item

    # ------------------------------------------------------------------ #
    # Field extraction                                                     #
    # ------------------------------------------------------------------ #

    def duration_from_block(self, block):
        text = self.text_of(block, self.get_selector_map('duration'))
        match = re.search(r'(\d+(?::\d{2}){1,2}) video', text)
        return self.duration_to_seconds(match.group(1)) if match else ''

    def performers_from_title(self, title):
        """Derive performers from the tile title.

        Titles are the set number plus the performer(s), in a handful of
        shapes: "1002 Kat Snow", "379_Serene Isley 2", "Anabelle Pync 606",
        "Bonus Update - Carissa Montgomery", "261 Lola Lynn and Nyxon".
        """
        if not title:
            return []

        name = _TITLE_PREFIX.sub('', title)
        name = _LEADING_SET_NUM.sub('', name)
        name = _TRAILING_NUM.sub('', name)
        # Sequence number glued to the last word ("Carissa Montgomery2"). The
        # lookbehind keeps names that legitimately contain a digit, like
        # "Kittie4u", intact.
        name = re.sub(r'(?<=[a-z])\d{1,2}$', '', name)

        performers = [p.strip() for p in re.split(r'\s+and\s+', name, flags=re.IGNORECASE)]
        return [self.unrun_together(p) for p in performers if p]

    @staticmethod
    def unrun_together(name):
        """Space out run-together CamelCase names and drop sequence digits.

        Part of the archive spells the performer as one token with a trailing
        sequence number ("CarissaMontgomery7", "TerraMizu3", "Pling3"). Names
        that are genuinely one word ("Nyxon", "Wenona", "Kittie4u") must survive
        untouched, so the split only fires on two or more CamelCase segments.
        """
        if ' ' in name:
            return name
        stripped = re.sub(r'\d+$', '', name)
        if re.fullmatch(r'(?:[A-Z][a-z]+){2,}', stripped):
            return ' '.join(re.findall(r'[A-Z][a-z]+', stripped))
        return stripped or name

    @staticmethod
    def text_of(node, xpath):
        """Collapse an xpath's text nodes into one clean string.

        The template pads every field with tabs and newlines, so a plain .get()
        returns e.g. '\\n\\t\\t\\t1002 Kat Snow\\t\\t\\t'.
        """
        if not xpath:
            return ''
        return ' '.join(''.join(node.xpath(xpath).getall()).split())
