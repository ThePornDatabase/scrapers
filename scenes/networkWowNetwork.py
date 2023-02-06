import string
import scrapy
import tldextract
from tpdb.BaseSceneScraper import BaseSceneScraper


def match_site(argument):
    match = {
        '18onlygirlsblog': "All Fine Girls",
        'ultrafilms': "Ultra Films",
        'wowgirlsblog': "Wow Girls",
        'wowpornblog': "Wow Porn",
    }
    return match.get(argument, argument)


class NetworkWowNetworkSpider(BaseSceneScraper):
    name = 'WowNetwork'
    network = 'Wow Girls'

    custom_scraper_settings = {
        'USER_AGENT':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.62',
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 5,
        'CONCURRENT_REQUESTS': 1,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'CONCURRENT_REQUESTS_PER_IP': 1,
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 522, 524, 408, 429, 403, 302],
    }

    start_urls = [
        'https://www.wowpornblog.com/',
        'https://www.wowgirlsblog.com/',
        'https://www.ultrafilms.xxx/',
        'https://www.18onlygirlsblog.com/',
    ]

    selector_map = {
        'title': '//h1[@class="entry-title"]/text()',
        'description': '',
        'date': '//meta[@itemprop="uploadDate"]/@content',
        'image': '//meta[@property="og:image"]/@content|//meta[@itemprop="thumbnailUrl"]/@content',
        'performers': '//div[@id="video-about"]/div[@id="video-actors"]/a/text()',
        'tags': '//div[@class="tags-list"]/a[@class="label"]/text()',
        'external_id': '/([a-z0-9-]+?)/?$',
        'trailer': '//video/source/@src',
        'pagination': '/category/movies/page/%s/?filter=latest'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//main[contains(@class,"site-main")]//div[@class="videos-list"][1]/article[contains(@class,"full-width")]/a/@href').getall()
        for scene in scenes:
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_tags(self, response):
        performers = response.xpath(self.get_selector_map('performers')).getall()

        if self.get_selector_map('tags'):
            tags = self.process_xpath(
                response, self.get_selector_map('tags')).getall()
            tags = list(map(lambda x: x.replace(' Movies', '').strip().lower(), tags))
            if performers:
                for performer in performers:
                    if performer.lower() in tags:
                        tags.remove(performer.lower())
            if tags:
                tags2 = tags.copy()
                for tag in tags2:
                    matches = ['1080p', '4k / uhd', '60 frames', 'hd', 'sd', 'movies', '6k']
                    if any(x in tag.lower() for x in matches):
                        tags.remove(tag)
            if tags:
                tags = list(map(lambda x: x.strip().title(), tags))
                return tags
        return []

    def get_description(self, response):
        return ''

    def get_site(self, response):
        return match_site(tldextract.extract(response.url).domain)

    def get_parent(self, response):
        return match_site(tldextract.extract(response.url).domain)

    def get_title(self, response):
        #  This is split out due to it sometimes grabbing the incorrect result if both are present.
        #  The og:title entry can have unwanted text
        title = super().get_title(response)
        if not title:
            title = response.xpath('//meta[@property="og:title"]/@content')
        if title:
            return string.capwords(title.strip())
        return None
