import re
import string

import scrapy
from deep_translator import GoogleTranslator

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class JavKOVideoSpider(BaseSceneScraper):
    name = 'KOVideo'
    network = 'KO Video'
    parent = 'KO Video'

    start_urls = [
        'https://ko-video.com',
    ]

    # The shop was rebuilt.  None of the old p-workPage__ / works/list / actress
    # selectors exist any more -- the listing is ul.item_list and each product page
    # keeps its facts in a dl inside div.detail_product, with the synopsis in
    # p.deitail_txt (the site's own spelling).  The モデル row lists body-type
    # categories rather than performer names, and no cast is published anywhere on
    # the rebuilt page, so performers are left empty rather than guessed at.
    selector_map = {
        # the only h1 is the logo; the product title is the first h2 in a title_bar
        'title': '//div[contains(@class, "title_bar")]/h2/text()',
        'description': '//p[contains(@class, "deitail_txt")]//text()',
        'date': '//div[contains(@class, "detail_product")]//dt[contains(text(), "商品発売日")]/following-sibling::dd[1]/text()',
        're_date': r'(\d{4}/\d{2}/\d{2})',
        'date_formats': ['%Y/%m/%d'],
        'image': '',
        'back': '',
        'performers': '',
        'tags': '//div[contains(@class, "detail_product")]//dt[contains(text(), "ジャンル") or contains(text(), "モデル")]/following-sibling::dd[1]/a/text()',
        'duration': '//div[contains(@class, "detail_product")]//dt[contains(text(), "収録時間")]/following-sibling::dd[1]/text()',
        'trailer': '',
        'external_id': r'product_code=([^&]+)',
        'pagination': '/products/list.php?disp_number=20&pageno=%s',
        'type': 'Jav',
    }

    custom_scraper_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.57',
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 10,
        'CONCURRENT_REQUESTS': 1,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'DOWNLOADER_MIDDLEWARES': {},
        'DOWNLOAD_MAXSIZE': 0,
        'DOWNLOAD_TIMEOUT': 100000,
        'DOWNLOAD_WARNSIZE': 0,
        'RETRY_ENABLED': True,
        "LOG_LEVEL": 'INFO',
        "EXTENSIONS": {'scrapy.extensions.logstats.LogStats': None},
        "MEDIA_ALLOW_REDIRECTS": True,
        "HTTPERROR_ALLOWED_CODES": [404],
    }

    def get_scenes(self, response):
        for card in response.xpath('//ul[contains(@class, "item_list")]/li[.//a[contains(@href, "detail.php")]]'):
            link = card.xpath('.//a[contains(@href, "detail.php")]/@href').get()
            if not link or not re.search(self.get_selector_map('external_id'), link):
                continue

            meta = dict(response.meta)
            meta['id'] = re.search(self.get_selector_map('external_id'), link).group(1)
            image = card.xpath('.//img/@src').get()
            if image:
                meta['image'] = self.format_link(response, image)

            yield scrapy.Request(url=self.format_link(response, link), callback=self.parse_scene,
                                 meta=meta, headers=self.headers, cookies=self.cookies)

    @staticmethod
    def translate(text):
        """A translation failure should cost the field, not the whole item."""
        try:
            return GoogleTranslator(source='ja', target='en').translate(text) or ''
        except Exception:
            return ''

    def get_title(self, response):
        # a second title_bar h2 heads the "ranking" strip, so only the first is taken
        title = response.xpath(self.get_selector_map('title')).get()
        title = title.strip() if title else ''
        if not title:
            return ''
        translated = self.translate(title.lower())
        title = string.capwords(translated) if translated else title
        return title + " - " + response.meta['id']

    def get_description(self, response):
        description = ' '.join(response.xpath(self.get_selector_map('description')).getall())
        description = self.cleanup_description(re.sub(r'\s+', ' ', description))
        if not description:
            return ''
        return self.translate(description) or description

    def get_tags(self, response):
        tags = []
        for tag in response.xpath(self.get_selector_map('tags')).getall():
            tag = tag.strip()
            if not tag:
                continue
            translated = self.translate(tag.lower())
            tags.append(string.capwords(translated) if translated else tag)
        for extra in ('Asian', 'JAV', 'Gay'):
            if extra not in tags:
                tags.append(extra)
        return tags

    def get_performers(self, response):
        return []

    def get_duration(self, response):
        duration = response.xpath(self.get_selector_map('duration')).get()
        if duration:
            duration = re.search(r'(\d+)\s*分', duration)
            if duration:
                return str(int(duration.group(1)) * 60)
        return None

    def get_back_image(self, response):
        """The first gallery still stands in for the sleeve back."""
        back = response.xpath('//a[contains(@data-slide-index, "0")]/img/@src').get()
        if not back:
            back = response.xpath('//img[contains(@src, "/gallery/")]/@src').get()
        return self.format_link(response, back.strip()) if back else ''

    def parse_scene(self, response):
        item = SceneItem()
        item['title'] = self.get_title(response)
        if not item['title']:
            return
        item['description'] = self.get_description(response)
        item['site'] = self.get_site(response)
        item['date'] = self.get_date(response)

        item['image'] = response.meta.get('image', '')
        item['image_blob'] = self.get_image_blob_from_link(item['image']) if item['image'] else None

        item['back'] = self.get_back_image(response)
        item['back_blob'] = self.get_image_blob_from_link(item['back']) if item['back'] else ''

        item['performers'] = self.get_performers(response)
        item['tags'] = self.get_tags(response)
        item['id'] = response.meta['id']
        item['trailer'] = self.get_trailer(response)
        item['duration'] = self.get_duration(response)
        item['url'] = self.get_url(response)
        item['network'] = self.network
        item['parent'] = self.parent
        item['type'] = 'JAV'

        item = self.check_item(item, self.days)
        if item:
            yield item
