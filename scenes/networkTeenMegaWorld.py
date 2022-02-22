import scrapy
from tldextract import tldextract

from tpdb.BaseSceneScraper import BaseSceneScraper


class TeenMegaWorldSpider(BaseSceneScraper):
    name = 'TeenMegaWorld'
    network = 'teenmegaworld'

    custom_settings = {'CONCURRENT_REQUESTS': '1'}

    start_urls = [
        'https://teenmegaworld.net',
        'http://rawcouples.com/',
        'http://anal-angels.com',
        'http://anal-beauty.com',
        'http://beauty4k.com',
        'http://beauty-angels.com',
        'http://creampie-angels.com',
        'http://dirty-coach.com',
        'http://dirty-doctor.com',
        'http://firstbgg.com',
        'http://fuckstudies.com',
        'http://gag-n-gape.com',
        'http://lollyhardcore.com',
        'http://noboring.com',
        'http://nubilegirlshd.com',
        'http://old-n-young.com',
        'http://soloteengirls.net',
        'http://teensexmania.com',
        'http://trickymasseur.com',
        'http://x-angels.com',
        'http://teensexmovs.com',
    ]

    selector_map = {
        'title': "//div[contains(@class, 'title-line')]//h1/text()",
        'description': "//p[contains(@class, 'description')]/text() | //div[contains(@class, 'text')]/text() | //meta[@property='og:description']/@content",
        'date': "//div[contains(@class, 'date')]//time/text()",
        'image': '//deo-video/@poster | //video/@poster | //meta[@property="og:image"]/@content',
        'performers': "//div[contains(@class, 'site')]//a[contains(@href, 'models')]/text()",
        'tags': "//ul[contains(@class, 'tag-list')]//a/text()",
        'external_id': 'trailers\\/(.+)\\.html',
        'trailer': '//source/@src',
        'pagination': '/categories/movies_%s_d.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath(
            "//a[contains(@class, 'title')]/@href").getall()
        for scene in scenes:
            yield scrapy.Request(url=scene, callback=self.parse_scene)

    def get_site(self, response):
        site = response.xpath(
            '//div[contains(@class, "site")]//a[starts-with(@href, "/search")]/text()').extract_first()
        return tldextract.extract(site).domain
