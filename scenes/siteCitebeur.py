import re
import json
import html
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteCitebeur(BaseSceneScraper):
    name = 'Citebeur'
    site = 'Citebeur'
    parent = 'Citebeur'
    network = 'Citebeur'

    start_urls = ['https://www.citebeur.com']

    selector_map = {
        'title': '//div[contains(@class, "col-12 text-center")]/h1/text()',
        'description': '//div[contains(@class, "col-12")]/h2/text()',
        'date': '',
        'image': '//div[contains(@class, "d-block embed-responsive embed-responsive-16by9 mb-2 rounded ")]/img/@src',
        'performers': '//i[contains(@class,"fa-star ")]/following-sibling::text()',
        # The wrapper class picked up an lh10 modifier; match the tag anchors instead
        'tags': '//a[contains(@href, "/en/videos/")]/h3/text()',
        'external_id': r'detail/(\d+)-',
        'trailer': '//video[contains(@class, "embed-responsive-item obj-cover d-none")]/source/@src',
        'pagination': '/en/videos?page=%s'
    }

    custom_scraper_settings = {
        'TWISTED_REACTOR': 'twisted.internet.asyncioreactor.AsyncioSelectorReactor',
        'AUTOTHROTTLE_ENABLED': True,
        'USE_PROXY': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 60,
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 2,
        'DOWNLOADER_MIDDLEWARES': {
            # 'tpdb.helpers.scrapy_flare.FlareMiddleware': 542,
            'tpdb.middlewares.TpdbSceneDownloaderMiddleware': 543,
            'tpdb.custommiddlewares.CustomProxyMiddleware': 350,
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': 500,
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
            yield scrapy.Request(url=self.get_next_page_url(link, self.page), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_next_page_url(self, base, page):
        page = str(int(page) -1)
        return self.format_url(base, self.get_selector_map('pagination') % page)

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        # The gallery was rebuilt: div.video-gallery is gone and each card is now a
        # bare anchor to /en/videos/detail/<id>-<slug>, repeated several times per
        # card (thumbnail, title and preview all link to it), hence the dedupe.
        scenes = response.xpath('//a[contains(@href, "/videos/detail/")]/@href').getall()
        for scene in dict.fromkeys(scenes):
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_ld(self, response):
        """The scene page publishes a full schema.org VideoObject.

        It carries the title, description, still, release date and cast, all of
        which the rebuilt markup no longer exposes as addressable elements.
        """
        for block in response.xpath('//script[@type="application/ld+json"]/text()').getall():
            try:
                data = json.loads(block)
            except ValueError:
                continue
            for entry in (data if isinstance(data, list) else [data]):
                if isinstance(entry, dict) and 'VideoObject' in str(entry.get('@type')):
                    return entry
        return {}

    def get_title(self, response):
        """A handful of scenes ship without JSON-LD; og:title still covers those,
        and returning None here crashes the pipeline's re.sub."""
        title = (self.get_ld(response).get('name')
                 or response.xpath('//meta[@property="og:title"]/@content').get()
                 or response.xpath('//h1//text()').get() or '')
        title = re.sub(r'\s*[|–-]\s*[^|–-]*$', '', title.strip()) if ' | ' in title else title.strip()
        return self.cleanup_title(title) if title else ''

    def get_description(self, response):
        ld = self.get_ld(response)
        text = ld.get('text') or ld.get('description') or ''
        if not text:
            text = response.xpath('//meta[@property="og:description"]/@content').get() or ''
        if not text:
            return ''
        # the long-form "text" field embeds escaped anchor markup
        text = re.sub(r'<[^>]+>', ' ', html.unescape(text))
        return self.cleanup_description(re.sub(r'\s+', ' ', text))

    def get_date(self, response):
        published = self.get_ld(response).get('datePublished') or self.get_ld(response).get('uploadDate')
        if published:
            published = re.search(r'(\d{4}-\d{2}-\d{2})', published)
            if published:
                return published.group(1)
        return None

    def get_image(self, response):
        image = self.get_ld(response).get('thumbnailUrl') or ''
        image = image.strip()
        if not image:
            return ''
        return self.format_link(response, image)

    def get_performers(self, response):
        actors = self.get_ld(response).get('actor') or []
        if isinstance(actors, dict):
            actors = [actors]
        return [a.get('name').strip() for a in actors
                if isinstance(a, dict) and a.get('name') and a['name'].strip()]

    def get_trailer(self, response):
        trailer = self.get_ld(response).get('contentUrl') or ''
        return trailer.strip()

    def get_duration(self, response):
        duration = response.xpath('//span[@class="mx-1" and contains(text(), "Time")]/text()')
        if duration:
            duration = duration.get()
            duration = "".join(duration).replace("\n", "").replace("\t", "").replace(" ", "").lower()
            duration = re.search(r'(\d+)min', duration)
            if duration:
                duration = duration.group(1)
                duration = str(int(duration) * 60)
                return duration
        return None
