import re
import string

import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteMuscleBoyWrestlingSpider(BaseSceneScraper):
    name = 'MuscleBoyWrestling'

    start_urls = [
        'https://muscleboywrestling.com',
    ]

    # Rebuilt on Next.js/Tailwind.  /catalog?alias=catalogs is a 404 -- the index is
    # /catalogs, a single page listing every catalog -- and div.catalog / div.video
    # card are gone.  The rebuild also dropped release dates: there is no date on
    # the catalog pages, the scene pages or the RSC payload, and the old
    # //h1/following-sibling::p[1] line no longer exists, so date is left empty and
    # TPDB falls back to the import date.
    selector_map = {
        'external_id': r'/video/(\w+-\w+)-',
        'pagination': '/catalogs',
        'type': 'Scene',
    }

    def get_next_page_url(self, base, page):
        # one index page; re-requesting it is dropped by the dupefilter
        return self.format_url(base, self.get_selector_map('pagination'))

    def get_scenes(self, response):
        catalogs = response.xpath('//a[contains(@href, "/catalogs/")]/@href').getall()
        for catalog in dict.fromkeys(catalogs):
            yield scrapy.Request(url=self.format_link(response, catalog), callback=self.parse_catalog,
                                 headers=self.headers, cookies=self.cookies)

    def parse_catalog(self, response):
        # the sidebar carries two more h2s ("Our Wrestlers", "Video Catalogs"), so
        # the catalog heading is matched on its own class; its text sits inside an
        # anchor rather than directly under the h2
        cat_title = ' '.join(response.xpath('//h2[contains(@class, "font-impact")]//text()').getall())
        if not cat_title:
            return
        cat_title = string.capwords(cat_title.strip().rstrip(string.punctuation))

        for scene in response.xpath('//div[contains(@class, "shadow-lg")][.//a[contains(@href, "/video/")]]'):
            link = scene.xpath('.//a[contains(@href, "/video/")]/@href').get()
            scene_title = scene.xpath('.//h3/text()').get()
            if not link or not scene_title or not re.search(self.get_selector_map('external_id'), link):
                continue

            meta = {}
            scene_title = string.capwords(scene_title.strip()).replace("Vs", "vs")
            meta['title'] = cat_title + ": " + scene_title
            if " vs " in scene_title.lower():
                meta['performers'] = [x.strip() for x in scene_title.split(" vs ") if x.strip()]
                meta['performers_data'] = self.build_performers_data(meta['performers'])
            meta['description'] = self.cleanup_description(
                scene.xpath('.//div[contains(@class, "text-sm")]/text()').get() or '')

            image = scene.xpath('.//img/@src').get()
            if image:
                meta['image'] = self.format_link(response, image)

            # the card's pills are the quality badge and the runtime
            runtime = ' '.join(scene.xpath('.//p/text()').getall())
            runtime = re.search(r'(\d+)\s*min', runtime)
            if runtime:
                meta['duration'] = str(int(runtime.group(1)) * 60)

            yield scrapy.Request(url=self.format_link(response, link), callback=self.parse_scene,
                                 meta=meta, headers=self.headers, cookies=self.cookies)

    def get_title(self, response):
        return response.meta.get('title', '')

    def get_description(self, response):
        return response.meta.get('description', '')

    def get_image(self, response):
        return response.meta.get('image', '')

    def get_date(self, response):
        """The rebuild publishes no release date anywhere; TPDB falls back to the
        import date when this is empty."""
        return ''

    def get_tags(self, response):
        return ['Gay', 'Wrestling', 'Sports']

    def get_trailer(self, response):
        """Trailer file names do not follow the slug reliably -- some 403 when
        guessed -- so it is read off the scene page."""
        trailer = response.xpath('//video//source/@src').get()
        return self.format_link(response, trailer.strip()) if trailer else ''

    def get_site(self, response):
        return 'Muscle Boy Wrestling'

    def get_parent(self, response):
        return 'Muscle Boy Wrestling'

    def get_network(self, response):
        return 'Muscle Boy Wrestling'

    def get_performers(self, response):
        return response.meta.get('performers', [])

    def get_performers_data(self, response):
        """parse_scene calls this with the response, so the builder below is kept
        under its own name -- a match whose title is not "X vs Y" has no cast."""
        return response.meta.get('performers_data', [])

    def build_performers_data(self, performers):
        performers_data = []
        for performer in performers:
            performer_extra = {}
            performer_extra['name'] = performer
            performer_extra['network'] = "Muscle Boy Wrestling"
            performer_extra['site'] = "Muscle Boy Wrestling"
            performer_extra['extra'] = {}
            performer_extra['extra']['gender'] = "Male"
            performers_data.append(performer_extra)
        return performers_data
