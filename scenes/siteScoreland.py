import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class ScorelandSpider(BaseSceneScraper):
    name = 'Scoreland'
    site = 'Scoreland'
    parent = 'Scoreland'
    network = 'ScorePass'

    start_urls = [
        'https://www.scoreland.com',
    ]

    # The Score network (scoreland, naughtymag, pornmegaload, scorepass and the
    # analqts family) refuses this exit outright: TLS completes, the request goes
    # out, then the server kills the stream -- HTTP/2 reports INTERNAL_ERROR and
    # HTTP/1.1 just hangs. It is not a TLS fingerprint or a challenge page;
    # Playwright fails the same way and FlareSolverr reports "Challenge not
    # detected", so it is the source address. Routing through FlareSolverr, which
    # runs on a different host, reaches the site normally.
    custom_scraper_settings = {
        'AUTOTHROTTLE_ENABLED': True,
        'CONCURRENT_REQUESTS': 1,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'DOWNLOAD_DELAY': 2,
        'DOWNLOAD_TIMEOUT': 180,
        'DOWNLOADER_MIDDLEWARES': {
            'tpdb.helpers.scrapy_flare.FlareMiddleware': 542,
            'tpdb.middlewares.TpdbSceneDownloaderMiddleware': 543,
        },
    }

    # The scene page was rebuilt: the p-info block became a set of
    # div.stat rows, each a span.label ("Featuring: ", "Date: ", "Duration: ")
    # followed by a span.value, and the title/synopsis moved into div.p-desc.
    # The old title selector matched nothing, which left item['title'] as None
    # and crashed the pipeline on re.sub rather than merely yielding nothing.
    selector_map = {
        # p-desc carries an h2 of the title plus the synopsis as bare text
        # nodes after it. NB the title selector must start with "//" -- the base
        # class routes anything else to .css(), so an XPath like "(//h1)[1]"
        # raises SelectorSyntaxError and the whole scene is dropped.
        'title': '//div[contains(@class, "p-desc")]/h2/text()',
        'description': '//div[contains(@class, "p-desc")]/text()',
        'date': '//div[contains(@class, "stat")]/span[contains(text(), "Date")]/following-sibling::span/text()',
        'date_formats': ['%B %d, %Y'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[contains(@class, "stat")]/span[contains(text(), "Featuring")]/following-sibling::span/a/text()',
        'tags': '//a[contains(@href, "updates-tag")]/text()',
        'duration': '//div[contains(@class, "stat")]/span[contains(text(), "Duration")]/following-sibling::span/text()',
        're_duration': r'((?:\d{1,2}:)?\d{1,2}:\d{2})',
        'external_id': r'.*/(\d+)/',
        'trailer': '//div[contains(@class, "mr-lg")]//video/source[1]/@src',
        'pagination': '/big-boob-videos/?page=%s',
        'type': 'Scene',
    }

    def get_date(self, response):
        # Dates read "September 8th, 2026"; the ordinal suffix has to go before
        # %B %d, %Y will match.
        scenedate = self.process_xpath(response, self.get_selector_map('date')).get()
        if scenedate:
            scenedate = re.sub(r'(\d{1,2})(st|nd|rd|th)', r'\1', scenedate.strip())
            parsed = self.parse_date(scenedate, date_formats=self.get_selector_map('date_formats'))
            if parsed:
                return parsed.isoformat()
        return ''

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        # The card class is now "li-item compact h-100 video", so the old
        # contains(@class, "li-item video") could never match -- those two words
        # are no longer adjacent.
        scenes = response.xpath(
            '//div[contains(@class, "li-item") and contains(@class, "video")]'
            '//div[contains(@class, "item-img")]/a/@href').getall()
        for scene in scenes:
            # Card links carry a ?nats= affiliate token, and a scene URL with it
            # attached does not load at all -- the browser gets "This site can't
            # be reached". Stripping it is what the (previously commented out)
            # line below always did, and it is required again.
            scene = re.sub(r'\?nats=.*$', '', scene)
            if "step=signup" not in scene and "join." not in scene:
                yield scrapy.Request(url=scene, callback=self.parse_scene, meta=meta)
