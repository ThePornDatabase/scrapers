import string
import html
import scrapy
import tldextract
from tpdb.BaseSceneScraper import BaseSceneScraper


def match_site(argument):
    match = {
        'creativeporn': "Creative Porn",
        'dirtysarah': "Dirty Sarah",
        'extremestreets': "Extreme Streets",
        'horrorporn': "Horror Porn",
        'movieporn': "Movie Porn",
        'perversefamily': "Perverse Family",
        'perversefamilylive': "Perverse Family Live",
        'spy26': "SPY26",
        'unrealporn': "Unreal Porn",
        'xvirtual': "XVirtual",
    }
    return match.get(argument, argument)


class siteUnrealPornSpider(BaseSceneScraper):
    name = 'UnrealPornNewformat'
    network = 'Czech Casting'

    start_urls = [
        'https://creativeporn.com',
        'https://dirtysarah.com',
        'https://extremestreets.com',
        'https://horrorporn.com',
        'https://movieporn.com',
        'https://perversefamily.com',
        'https://perversefamilylive.com',
        'https://spy26.com',
        'https://unrealporn.com',
        'https://xvirtual.com',
    ]

    selector_map = {
        'title': '//div[contains(@class, "badge")]/span[contains(@class, "text-uppercase")]/../following-sibling::span[1]/text()',
        'date': '//script[contains(text(), "thumbnailUrl")]/text()',
        're_date': r'[\'\"]uploadDate[\'\"]\: [\'\"](.*?)[\'\"]',
        'description': '//div[contains(@class, "detail-description")]/p/text()',
        'image': '//meta[@property="og:image"]/@content',
        'duration': '//script[contains(text(), "thumbnailUrl")]/text()',
        're_duration': r'[\'\"]duration[\'\"]\: [\'\"](.*?)[\'\"]',
        'tags': '//div[contains(@class,"show-more-ultimate")]/ul/li/a/span/text()',
        'performers': '//span[contains(text(), "Featuring")]/following-sibling::a/text()',

        'external_id': '.*/(.*?)/',
        'trailer': '',
        'pagination': '/pages/page-%s/'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class, "gap--100")]/a/@href').getall()
        for scene in scenes:
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_parent(self, response):
        return match_site(tldextract.extract(response.url).domain)

    def get_site(self, response):
        return match_site(tldextract.extract(response.url).domain)

    def get_image_blob(self, response):
        image = response.xpath('//meta[@property="og:image"]/@content').get()
        return self.get_image_blob_from_link(image)
