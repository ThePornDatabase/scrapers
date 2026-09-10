import re
import os
import json
import hashlib
import requests
from urllib.parse import urlparse
from requests import get
from datetime import date, timedelta, datetime
import dateparser
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
true = True
false = False


class NubilesSpider(BaseSceneScraper):
    name = 'Nubiles'
    network = 'nubiles'

    # Must match the UA that Scrapy actually sends (forced by TpdbSceneDownloaderMiddleware).
    # Server binds the PoW-verified session to this UA — mismatch → 429.
    USER_AGENT = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 '
                  'Edg/107.0.1418.62')

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

    custom_scraper_settings = {
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 10,
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 2,
        'DOWNLOADER_MIDDLEWARES': {
            'tpdb.middlewares.TpdbSceneDownloaderMiddleware': 543,
            # Disabled — sends Scrapy requests through a different IP than
            # get_verified_cookies() used to solve the PoW, invalidating the session.
            # 'tpdb.custommiddlewares.CustomProxyMiddleware': 350,
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
        },
    }

    cookies = [{
                "hostOnly": true,
                "httpOnly": false,
                "name": "18-plus-modal",
                "path": "/",
                "sameSite": "unspecified",
                "secure": false,
                "session": false,
                "storeId": "0",
                "value": "hidden"
            }
        ]

    start_urls = [
        "https://anilos.com",
        "https://badteenspunished.com",
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

    selector_map = {
        'title': '//*[contains(@class, "content-pane-title")]/h2/text()',
        'description': '//div[contains(@class, "content-pane-description")]/p/text()',
        'date': '//span[@class="date"]/text()',
        'image': '//video/@poster|//img[@class="fake-video-player-cover"]/@src',
        'performers': '//a[@class="content-pane-performer model"]/text()',
        'tags': '//*[@class="categories"]//a/text()',
        'external_id': '(\\d+)',
        'trailer': '//div[contains(@class,"video-container")]//source[contains(@src, ".mp4") and contains(@src,"1280")]/@src|//div[contains(@class,"video-container")]//source[contains(@src, ".mp4") and contains(@src,"960")]/@src|//div[contains(@class,"video-container")]//source[contains(@src, ".mp4") and contains(@src,"640")]/@src|//meta[@property="og:video"]/@content',
        'pagination': '/video/gallery/%s'
    }

    async def start(self):
        try:
            ip = get('https://api.ipify.org', timeout=5).content.decode('utf8')
            print('My public IP address is: {}'.format(ip))
        except Exception as e:
            print(f'Could not resolve public IP: {e}')

        for link in self.start_urls:
            # The server bounces /video/gallery -> /turnstile/challenge -> /video/gallery
            # to issue session state. We follow redirects manually with dont_filter=True so
            # the dupefilter doesn't block the second hop back to /video/gallery, and so we
            # can intercept the Security Check page if it appears.
            meta = {
                'page': self.page,
                'base_link': link.rstrip('/'),
                'dont_redirect': True,
                'handle_httpstatus_list': [301, 302, 303, 307, 308],
            }
            yield scrapy.Request(
                url=self.get_next_page_url(link, self.page),
                callback=self.captcha_or_parse,
                meta=meta,
                headers=self.headers,
                cookies={'18-plus-modal': 'hidden'},
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
        # Detect the challenge either by URL (site's own /turnstile/challenge path)
        # or by content markers. URL check is more resilient — the challenge HTML
        # has been reworked before, and we don't want to silently fall through when
        # markup changes.
        is_challenge = (
            '/turnstile/challenge' in response.url
            or 'turnstileConfig' in response.text
            or 'Security Check' in response.text
        )
        if is_challenge:
            yield from self._solve_captcha(response)
        else:
            yield from self.parse(response)

    def _solve_captcha(self, response):
        m = re.search(r"var\s+turnstileConfig\s*=\s*(\{.*?\});", response.text)
        if not m:
            self.logger.error(
                f"Captcha page detected at {response.url} but turnstileConfig not parseable. "
                f"Response head (first 800 chars): {response.text[:800]!r}"
            )
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
        verify_headers = dict(self.headers)
        verify_headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
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
        redirect_to = result.get('redirectTo') or '/video/gallery'
        if not redirect_to.startswith('http'):
            redirect_to = base + redirect_to

        self.logger.info(f"Verified, re-requesting {redirect_to}")
        yield scrapy.Request(
            url=redirect_to,
            callback=self.parse,
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

    def get_scenes(self, response):
        scenes = response.xpath('//figcaption')
        for scene in scenes:
            link = scene.xpath('./div/span/a/@href').get()
            if re.search(r'video/watch', link) is not None:
                scenedate = scene.xpath('.//span[@class="date"]/text()').get()
                meta = {
                    'title': scene.xpath('./div/span/a/text()').get().strip(),
                    'date': dateparser.parse(scenedate, date_formats=['%b %d, %Y']).strftime('%Y-%m-%d'),
                }
                if "brattysis" in response.url:
                    meta['site'] = "Bratty Sis"
                    meta['parent'] = "Bratty Sis"
                if "cheatingsis" in response.url:
                    meta['site'] = "Cheating Sis"
                    meta['parent'] = "Cheating Sis"
                if "cumswappingsis" in response.url:
                    meta['site'] = "Cum Swapping Sis"
                    meta['parent'] = "Cum Swapping Sis"
                elif "anilos" in response.url:
                    meta['site'] = "Anilos"
                    meta['parent'] = "Anilos"
                elif "deeplush" in response.url:
                    meta['site'] = "Deep Lush"
                    meta['parent'] = "Deep Lush"
                elif "doublepies" in response.url:
                    meta['site'] = "Double Pies"
                    meta['parent'] = "Momlover"
                elif "hotcrazymess" in response.url:
                    meta['site'] = "Hot Crazy Mess"
                    meta['parent'] = "Hot Crazy Mess"
                elif "nfbusty" in response.url:
                    meta['site'] = "NF Busty"
                    meta['parent'] = "NF Busty"
                elif "nubiles.net" in response.url:
                    meta['site'] = "Nubiles"
                    meta['parent'] = "Nubiles"
                elif "thepovgod" in response.url:
                    meta['site'] = "The POV God"
                    meta['parent'] = "The POV God"
                if 'site' not in meta or not meta['site']:
                    meta['site'] = scene.xpath('.//a[@class="site-link"]/text()').get()
                    meta['parent'] = scene.xpath('.//a[@class="site-link"]/text()').get()
                url=self.format_link(response, link)
                if self.check_item(meta, self.days):
                    yield scrapy.Request(url,callback=self.parse_scene, meta=meta)

    # Hosts known to reject /video/gallery/0 — page 1 must be plain /video/gallery.
    # Short-circuit the HEAD probe for these so we don't burn requests (and don't
    # risk triggering the WAF on the ones that answer HEAD with 429).
    _PAGE1_PLAIN_HOSTS = (
        'nubiles.net',
        'doublepies.com',
    )

    # Cache of page-1 URL per host, persisted across runs so we probe each site
    # at most once, ever.
    _PAGE1_CACHE_FILE = os.path.expanduser('~/.tpdb_nubiles_page1_cache.json')
    _page1_cache = None  # populated lazily on first access

    def _load_page1_cache(self):
        cls = type(self)
        if cls._page1_cache is not None:
            return cls._page1_cache
        try:
            with open(cls._PAGE1_CACHE_FILE, 'r') as f:
                cls._page1_cache = json.load(f)
        except (OSError, ValueError):
            cls._page1_cache = {}
        return cls._page1_cache

    def _save_page1_cache(self):
        cls = type(self)
        if cls._page1_cache is None:
            return
        try:
            with open(cls._PAGE1_CACHE_FILE, 'w') as f:
                json.dump(cls._page1_cache, f, indent=2)
        except OSError:
            pass

    def get_next_page_url(self, base, page):
        if page == 1:
            probe_url = self.format_url(base, self.get_selector_map('pagination') % 0)
            plain_url = self.format_url(base, '/video/gallery')
            host = urlparse(base).netloc.lower()

            # Fast-path 1: hardcoded known-plain hosts.
            if any(bad in host for bad in self._PAGE1_PLAIN_HOSTS):
                return plain_url

            # Fast-path 2: persistent cache from a previous run.
            cache = self._load_page1_cache()
            if host in cache:
                return cache[host]

            # Cold path: probe once, then remember the answer forever.
            chosen = plain_url
            try:
                r = requests.head(
                    probe_url,
                    headers={'User-Agent': self.USER_AGENT},
                    allow_redirects=True,
                    timeout=10,
                )
                if r.status_code == 200:
                    chosen = probe_url
            except requests.RequestException:
                pass
            cache[host] = chosen
            self._save_page1_cache()
            return chosen
        page = ((page - 1) * 12)
        return self.format_url(base, self.get_selector_map('pagination') % page)
        

    def get_description(self, response):
        if 'description' not in self.get_selector_map():
            return ''
        descriptionxpath = self.process_xpath(response, self.get_selector_map('description'))
        description = ''
        if descriptionxpath:
            descriptionxpath = descriptionxpath.getall()
            for descrow in descriptionxpath:
                descrow = descrow.replace("\n", "").replace("\r", "").replace("\t", "").strip()
                if descrow:
                    description = description + descrow

        if not description or (description and not description.strip()):
            description = response.xpath('//div[@class="col-12 content-pane-column"]/div//text()[not(contains(., "Show More")) and not(contains(., "Show Less"))]')
            description = description.getall()
            if description:
                description = " ".join(description)
        if description:
            return description.replace('Description:', '').strip()
        return ""

    def get_trailer(self, response, path=None):
        if 'trailer' in self.get_selector_map():
            trailer = self.get_element(response, 'trailer', 're_trailer')
            if type(trailer) is list:
                trailer = trailer[-1]
            if trailer:
                if path:
                    return self.format_url(path, trailer)
                else:
                    return self.format_link(response, trailer)

        return ''
    
    def get_performers(self, response):
        perf_list = response.xpath('//a[@class="content-pane-performer model"]')
        performers = []
        if perf_list:
            for performer in perf_list:
                perf_name = performer.xpath('./text()').get()
                perf_url = performer.xpath('./@href').get()
                perf_id = re.search(r'profile/(\d+)/', perf_url)
                if perf_id:
                    perf_id = perf_id.group(1)

                if " " not in perf_name and perf_id:
                    perf_name = perf_name + " " + perf_id
                performers.append(perf_name.strip())
        return performers