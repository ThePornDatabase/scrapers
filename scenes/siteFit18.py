import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteFit18Spider(BaseSceneScraper):
    name = 'Fit18'
    network = 'Fit 18'
    parent = 'Fit 18'
    site = 'Fit 18'

    # The old fit18.team18media.app GraphQL API no longer resolves.  The site is now a
    # server-rendered Next.js app, but every listing is capped at 12 entries and the
    # rest is loaded client-side, so the crawl also walks the model pages to reach
    # what it can (about 27 scenes).  The previous scraper only asked for the newest
    # 15, so this is no worse in practice.
    start_urls = [
        'https://fit18.com/videos',
    ]

    selector_map = {
        'title': '//h1[contains(@class, "video-title-component")]/text()',
        'description': '//div[contains(@class, "video-description-component")]/p//text()',
        # Neither the listing nor the scene page publishes a release date or duration
        'date': '',
        'image': '//picture//img[contains(@src, "videothumb")]/@src | (//picture//img/@src)[1]',
        'performers': '//div[contains(@class, "video-models-component")]//a/text()',
        'tags': '//div[contains(@class, "video-tags-component")]/a/text()',
        'external_id': r'/video/(.*?)/?$',
        'trailer': '',
        'pagination': '',
        'type': 'Scene',
    }

    async def start(self):
        meta = {}
        meta['page'] = self.page
        for url in (self.start_urls[0], 'https://fit18.com/models'):
            yield scrapy.Request(url, callback=self.parse, meta=meta,
                                 headers=self.headers, cookies=self.cookies)

    def parse(self, response, **kwargs):
        yield from self.get_scenes(response)

        # Model pages carry that model's scenes, which reach a little further than
        # the 12 the /videos listing renders.
        for model in response.xpath('//a[starts-with(@href, "/model/")]/@href').getall():
            yield scrapy.Request(url=self.format_link(response, model),
                                 callback=self.parse_models, meta=response.meta,
                                 headers=self.headers)

    def parse_models(self, response):
        yield from self.get_scenes(response)

    def get_scenes(self, response):
        for link in response.xpath('//a[starts-with(@href, "/video/")]/@href').getall():
            yield scrapy.Request(url=self.format_link(response, link),
                                 callback=self.parse_scene, meta=response.meta,
                                 headers=self.headers)

    def get_image(self, response):
        """Return '' rather than the site root when no thumbnail is present.

        The base implementation runs format_link() on an empty match, which resolves
        to the domain and yields an 'image' of https://fit18.com.
        """
        image = response.xpath(self.get_selector_map('image')).get() or ''
        image = image.strip()
        if not image:
            return ''
        return self.format_link(response, image)
