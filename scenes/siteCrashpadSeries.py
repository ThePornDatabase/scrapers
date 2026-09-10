import re
from requests import get
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteCrashpadSeriesSpider(BaseSceneScraper):
    name = 'CrashpadSeries'
    network = 'CrashpadSeries'
    parent = 'CrashpadSeries'
    site = 'CrashpadSeries'

    start_url = 'https://crashpadseries.com/queer-porn/episodes-all/'

    # The site was rebuilt on a Bootstrap 5 theme: the episode title moved from an h2
    # to the h1, ep-description is now a span rather than a div, the release date sits
    # in the byline span next to the director instead of its own h4, and the tag icons
    # became text buttons.  The cast is no longer published as markup at all -- see
    # get_performers below.
    selector_map = {
        'title': '//h1[contains(@class, "text-uppercase")]/text()',
        'description': '//span[contains(@class, "ep-description")]//p[not(contains(text(), "following the results of the presidential election"))]/text()',
        'date': '//span[contains(@class, "text-body-secondary")]//text()',
        're_date': r'(\w+ \d+\w{1,2}?, \d{4})',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '',
        'tags': '//div[contains(@class, "film-tags-box")]/a/text()',
        'director': '//a[contains(@href, "/director/")]/text()',
        'duration': '',
        'trailer': '',
        'external_id': r'episode-(\d+)-',
        'pagination': '',
        'type': 'Scene',
    }

    async def start(self):
        ip = get('https://api.ipify.org').content.decode('utf8')
        print('My public IP address is: {}'.format(ip))

        yield scrapy.Request(self.start_url, callback=self.get_scenes, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        # a.epiLink became a.film-link, and the thumbnail is a plain src now that the
        # listing no longer lazy-loads.
        for scene in response.xpath('//a[contains(@class, "film-link")][contains(@href, "/episode/")]'):
            link = scene.xpath('./@href').get()
            if not link or not re.search(self.get_selector_map('external_id'), link):
                continue
            image = scene.xpath('.//img/@src').get()
            if image and image.strip():
                # get_image_blob_from_link needs an absolute URL or it logs a
                # "missing protocol" error for every card
                meta['image'] = self.format_link(response, image.strip())
                meta['image_blob'] = self.get_image_blob_from_link(meta['image'])
            yield scrapy.Request(url=self.format_link(response, link), callback=self.parse_scene, meta=meta)

    def get_date(self, response):
        """Pull "Release Date: September 4th, 2026" out of the byline.

        The byline is several text nodes (director link, icons, the date), so the
        base implementation takes the first one and parse_date returns None on it.
        """
        for text in response.xpath(self.get_selector_map('date')).getall():
            scenedate = re.search(self.get_selector_map('re_date'), text)
            if scenedate:
                scenedate = self.parse_date(scenedate.group(1))
                if scenedate:
                    return scenedate.strftime('%Y-%m-%d')
        return None

    def get_performers(self, response):
        """Recover the cast from the title, the only place the site still names it.

        Episodes are titled "Episode 449: Goddess Euphoria and Vitalis". Only that
        exact shape is parsed, and only parts that look like names are kept, so the
        specials and compilations yield nothing rather than nonsense.
        """
        title = response.xpath(self.get_selector_map('title')).get() or ''
        cast = re.match(r'\s*Episode\s+\d+\s*:\s*(.+)$', title.strip())
        if not cast:
            return []
        performers = []
        for part in re.split(r'\s+and\s+|\s*&\s*|\s*,\s*', cast.group(1)):
            part = part.strip(' .')
            if 2 <= len(part) <= 40 and not re.search(r'\d', part):
                performers.append(part)
        return performers

    def get_image(self, response):
        """The old bunny.net iframe thumbnail is gone; use the listing card's still,
        then og:image, and return '' rather than letting the base resolve the domain."""
        image = response.meta.get('image') or response.xpath(self.get_selector_map('image')).get() or ''
        image = image.strip()
        if not image:
            return ''
        return self.format_link(response, image)
