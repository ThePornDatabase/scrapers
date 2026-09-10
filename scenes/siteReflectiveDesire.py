import json
import re

import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class ReflectiveDesireSpider(BaseSceneScraper):
    name = 'ReflectiveDesire'
    network = 'Reflective Desire'
    parent = 'Reflective Desire'
    site = 'Reflective Desire'

    start_urls = [
        'https://reflectivedesire.com/videos/pain/?sort=chrono',
        'https://reflectivedesire.com/videos/pleasure/?sort=chrono&priority=videos',
        'https://reflectivedesire.com/videos/solos/?sort=chrono',
        'https://reflectivedesire.com/videos/devices/?sort=chrono',
        'https://reflectivedesire.com/videos/extras/?sort=chrono',
    ]

    custom_scraper_settings = {
        'TWISTED_REACTOR': 'twisted.internet.asyncioreactor.AsyncioSelectorReactor',
        'AUTOTHROTTLE_ENABLED': True,
        # ~ 'USE_PROXY': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 60,
        'CONCURRENT_REQUESTS': 1,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'DOWNLOAD_DELAY': 5,
        'PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT': 60000,  # 60s
        'DOWNLOADER_MIDDLEWARES': {
            # 'tpdb.helpers.scrapy_flare.FlareMiddleware': 542,
            'tpdb.middlewares.TpdbSceneDownloaderMiddleware': 543,
            # ~ 'tpdb.custommiddlewares.CustomProxyMiddleware': 350,
            # ~ 'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': 500,
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': 550,
        },
        'DOWNLOAD_HANDLERS': {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        }
    }

    async def start(self):
        meta = {}
        meta['page'] = self.page
        meta['playwright'] = True
        for link in self.start_urls:
            yield scrapy.Request(link, callback=self.get_scenes, meta=meta, headers=self.headers, cookies=self.cookies)

    selector_map = {
        'title': '//h1/text()',
        'description': '//meta[@name="description"]/@content',
        'date': '//meta[@name="description"]/@content',
        're_date': r'Posted ([a-zA-Z]*? \d{4})',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//span[contains(text(), "Performers")]/a/text()',
        'tags': '//span[contains(text(), "Categories")]/a/text()',
        'external_id': r'.*\/(.*?)\/',
        'trailer': '',
    }

    def get_scenes(self, response):
        # The listing was rebuilt: main/section[1]//article/a is gone and the cards
        # are a.video-cover-link.  The "browse other categories" strip at the foot
        # of the page uses the same class, so scene cards are told apart by their
        # hover-preview attribute -- without this the category pages (/videos/pain/,
        # /videos/extras/ and so on) are scraped as dateless, castless scenes.
        scenes = response.xpath('//a[contains(@class, "video-cover-link")][@data-preload-loops]/@href').getall()
        for scene in dict.fromkeys(scenes):
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene,
                                     meta={'playwright': True})

    def get_ld(self, response):
        """The scene page publishes a schema.org VideoObject. The old date came from
        a "Posted <month> <year>" line in the meta description, which the rebuilt
        page no longer carries -- uploadDate replaces it, and the same block also
        supplies the runtime and the teaser."""
        for block in response.xpath('//script[@type="application/ld+json"]/text()').getall():
            try:
                data = json.loads(block)
            except ValueError:
                continue
            for entry in (data if isinstance(data, list) else [data]):
                if isinstance(entry, dict) and 'VideoObject' in str(entry.get('@type')):
                    return entry
        return {}

    def get_duration(self, response):
        runtime = re.search(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?',
                            self.get_ld(response).get('duration') or '')
        if not runtime or not any(runtime.groups()):
            return None
        hours, minutes, seconds = (int(x) if x else 0 for x in runtime.groups())
        return str(hours * 3600 + minutes * 60 + seconds)

    def get_trailer(self, response):
        return (self.get_ld(response).get('contentUrl') or '').strip()

    def get_tags(self, response):
        tags = ['Bondage', 'Fetish', 'Latex / Rubber / Vinyl']
        tags2 = super().get_tags(response)
        for tag in tags2:
            tags.append(tag)
        return tags

    def get_date(self, response):
        # The rebuilt meta description dropped the "Posted <month> <year>" line the
        # old regex keyed on, and its fallback silently stamped every scene with
        # today's date.  The VideoObject carries the real release date.
        published = re.search(r'(\d{4}-\d{2}-\d{2})', self.get_ld(response).get('uploadDate') or '')
        if published:
            return published.group(1)

        date = self.process_xpath(response, self.get_selector_map('date'))
        if date:
            date = self.get_from_regex(date.get(), 're_date')
            if date:
                date = date.replace(" ", " 1, ")
                return self.parse_date(date).isoformat()
        return None

    def get_performers(self, response):
        performers = self.process_xpath(response, self.get_selector_map('performers'))
        if performers:
            performers = performers.getall()
            return list(map(lambda x: x.replace("Follow ", "").strip(), performers))
        return []
