from datetime import datetime
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
        'spy26': "SPY26",
        'unrealporn': "Unreal Porn",
        'xvirtual': "XVirtual",
    }
    return match.get(argument, argument)

class siteUnrealPornSpider(BaseSceneScraper):
    name = 'UnrealPorn'
    network = 'Czech Casting'

    start_urls = [
        'https://creativeporn.com',
        'https://dirtysarah.com',
        'https://extremestreets.com',
        'https://horrorporn.com',
        'https://movieporn.com',
        'https://perversefamily.com',
        'https://spy26.com',
        'https://unrealporn.com',
        'https://xvirtual.com',
    ]

    selector_map = {
        'title': '//div[@class="title"]/h2[@class="nice-title"]/text()',
        'description': "//div[@class='desc-text']//p/text()",
        'image': "//meta[@property='og:image']/@content",
        're_image': '(.*)\?',
        'tags': '//ul[@class="tags"]/li/a/text()',
        'external_id': '/tour\\/preview\\/(.+)/',
        'trailer': '',
        'pagination': '/tour/page-%s/'
    }

    def get_scenes(self, response):
        scenes = response.xpath(
            '//div[contains(@class, "episode-list")]//div[contains(@class,"episode__preview")]//a[contains(@class,"title")]/@href').getall()
        for scene in scenes:
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_performers(self, response):
        return ['Unknown Czech Performer']

    def get_date(self, response):
        return datetime.now().isoformat()

    def get_description(self, response):
        description = self.process_xpath(response, self.get_selector_map('description')).getall()
        if description:
            description = " ".join(description)
            return html.unescape(description.strip())
        return ''
 
    def get_parent(self, response):
        return match_site(tldextract.extract(response.url).domain)
               
    def get_site(self, response):
        return match_site(tldextract.extract(response.url).domain)

