import warnings
import dateparser
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper

# Ignore dateparser warnings regarding pytz
warnings.filterwarnings(
    "ignore",
    message="The localize method is no longer necessary, as this time zone supports the fold attribute",
)


class CherryPimpsSpider(BaseSceneScraper):
    name = 'CherryPimps'
    network = 'Cherry Pimps'

    start_urls = [
        'https://www.cherrypimps.com',
        'https://www.wildoncam.com',
        'https://www.cherryspot.com',
    ]

    selector_map = {
        'title': '//*[@class="trailer-block_title"]/text() | //h1/text()',
        'description': '//div[@class="info-block"]//p[@class="text"]/text() | '
                       '//div[@class="update-info-block"]//p/text()',
        'image': '//img[contains(@class, "update_thumb")]/@src | '
                 '//img[contains(@class, "update_thumb")]/@src0_1x',
        'performers': '//div[contains(@class, "model-list-item")]'
                      '//a/span/text() | '
                      '//p[contains(text(), "Featuring")]/a/text()',
        'tags': '//ul[@class="tags"]/li/a/text() | '
                '//p[@class="text" and contains(text()'
                ',"Categories")]/a/text()',
        'external_id': 'trailers/(.+)\\.html',
        'trailer': '',
        'pagination': '/categories/movies_%s.html'
    }

    def get_scenes(self, response):
        """ Returns a list of scenes
        @url https://cherrypimps.com/categories/movies.html
        @returns requests 10 50
        """
        if "cherrypimps" in response.url:
            scenexpath = '//div[contains(@class,"item-update") and ' \
                'not(contains(@class,"item-updates"))]'
        if "wildoncam" in response.url or "cherryspot" in response.url:
            scenexpath = '//div[contains(@class,"video-thumb")]'
        scenes = response.xpath(scenexpath)
        for scene in scenes:
            site = scene.xpath(
                './/div[@class="item-sitename"]/a/text() | '
                './p[contains(@class, "text-thumb")]/a/@data-elx_site_name'
            )
            if site:
                site = site.get().strip()
            else:
                site = False
            if "cherrypimps" in response.url:
                urlxpath = './div[@class="item-footer"]/div' \
                    '/div[@class="item-title"]/a/@href'
            else:
                urlxpath = './div[contains(@class, "videothumb")]/a/@href' \
                    '| ./a/@href'
            scene = scene.xpath(urlxpath).get()
            yield scrapy.Request(
                url=scene, callback=self.parse_scene, meta={'site': site})

    def get_date(self, response):
        selector = '//div[@class="info-block_data"]//p[@class="text"]/text() '\
                   '| //div[@class="update-info-row"]/text()'
        if "wildoncam" in response.url or "cherryspot" in response.url:
            date = response.xpath(selector).extract()[0]
        else:
            date = response.xpath(selector).extract()[1]
        date = date.split('|')[0].replace('Added', '').replace(':', '').strip()
        return dateparser.parse(date).isoformat()

    def get_site(self, response):
        return response.css('.series-item-logo::attr(title)').get().strip()

    def get_parent(self, response):
        meta = response.meta
        if meta['site']:
            return meta['site']
        return super().get_parent(response)
