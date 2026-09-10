import re
import html
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteKinkAcademySpider(BaseSceneScraper):
    name = 'KinkAcademy'
    network = 'Kink Academy'
    parent = 'Kink Academy'
    site = 'Kink Academy'

    start_url = 'https://www.kinkacademy.com'

    # /category/experts/page/N/ 404s now, as do the commented skill-level paths.  The
    # surviving listing is /videos/, and its own "page 2..95" links 404 as well, so
    # the site is effectively serving a single page of 24 -- get_next_page_url
    # therefore returns /videos/ for page one and nothing after it.
    paginations = [
        '/videos/',
    ]

    selector_map = {
        'title': '//meta[@name="twitter:title"]/@content',
        # figure.featured-image is gone; og:description carries the synopsis
        'description': '//meta[@property="og:description"]/@content',
        'date': '//meta[@property="article:published_time"]/@content',
        're_date': r'(\d{4}-\d{2}-\d{2})',
        'image': '//figure[@class="featured-image"]/img/@src',
        'performers': '',
        # p.entry-meta is gone.  The scene page carries many articles (its own plus
        # related), so their class lists cannot be told apart there -- the tags come
        # from the listing card instead, via meta.  See get_scenes.
        'tags': '',
        'duration': '',
        'trailer': '',
        'external_id': r'.*/(.*?)/',
        'pagination': '',
        'type': 'Scene',
    }

    def get_next_page_url(self, base, page, pagination):
        if '%s' not in pagination:
            return self.format_url(base, pagination) if int(page) == 1 else None
        return self.format_url(base, pagination % page)

    async def start(self):
        meta = {}
        meta['page'] = self.page

        for pagination in self.paginations:
            link = 'https://www.kinkacademy.com'
            meta['pagination'] = pagination
            yield scrapy.Request(url=self.get_next_page_url(link, self.page, pagination), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def parse(self, response, **kwargs):
        scenes = self.get_scenes(response)
        count = 0
        for scene in scenes:
            count += 1
            yield scene

        if count:
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                meta = self.copy_meta(response)
                meta['page'] = meta['page'] + 1
                nextpage = self.get_next_page_url(response.url, meta['page'], meta['pagination'])
                if nextpage:
                    print('NEXT PAGE: ' + str(meta['page']))
                    yield scrapy.Request(url=nextpage, callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        for article in response.xpath('//article[contains(@class, "format-video")]'):
            figure = article.xpath('./header/figure')
            if not figure:
                continue
            meta['orig_image'] = figure.xpath('.//img/@src').get()

            # WordPress writes this scene's own taxonomy onto the article element as
            # category-<slug> and tag-<slug> classes; the housekeeping ones are dropped
            classes = (article.attrib.get('class') or '').split()
            skip = {'video', 'members-only', 'free'}
            tags = []
            for cls in classes:
                for prefix in ('category-', 'tag-'):
                    if cls.startswith(prefix):
                        slug = cls[len(prefix):]
                        if slug in skip or re.fullmatch(r'\d+', slug):
                            continue
                        name = string.capwords(re.sub(r'\d+$', '', slug).replace('-', ' ').strip())
                        if name and name not in tags:
                            tags.append(name)
            meta['tags'] = tags

            scene = figure.xpath('./a/@href').get()
            if scene and re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_performers(self, response):
        performerlist = response.xpath('//span[@class="post-instructors"]/span[@class="terms"]/a/text()')
        if performerlist:
            performerlist = performerlist.getall()
        performers = []
        for perf in performerlist:
            performers.append(string.capwords(html.unescape(perf)))
        return performers

    def get_image(self, response):
        image = super().get_image(response)
        if not image or image in response.url:
            image = response.meta['orig_image']
        return image
