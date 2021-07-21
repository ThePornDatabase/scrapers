import scrapy
import html
import re
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

class networkWowNetworkSpider(BaseSceneScraper):
    name = 'WowNetwork'
    network = 'Wow Girls'

    start_urls = [
        'https://www.wowpornblog.com/',
        'https://www.wowgirlsblog.com/',
        'https://www.ultrafilms.xxx/',
        'https://www.18onlygirlsblog.com/',
    ]

    selector_map = {
        'title': '//meta[@property="og:title"]/@content',
        'description': '',
        'date': '//meta[@itemprop="uploadDate"]/@content',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[@id="video-about"]/div[@id="video-actors"]/a/text()',
        'tags': '//div[@class="tags-list"]/a[@class="label"]/text()',
        'external_id': '/([a-z0-9-]+?)/?$',
        'trailer': '//meta[@property="og:description"]/@content',
        'pagination': '/category/movies/page/%s/?filter=latest'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//main[contains(@class,"site-main")]//div[@class="videos-list"][1]/article[contains(@class,"full-width")]/a/@href').getall()
        for scene in scenes:
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        site = response.xpath(
            '//span[@itemprop="name"]/text()').extract_first()
        return site

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

    def get_trailer(self, response):
        trailer = response.xpath(self.get_selector_map('trailer')).get()
        if trailer:
            trailer = re.search('(http.*\.mp4)', trailer).group(1)
            if trailer:
                return trailer.strip()
        return ''


    def get_description(self, response):
        return ''
        
    def get_site(self, response):
        return match_site(tldextract.extract(response.url).domain)
        
    def get_parent(self, response):
        return match_site(tldextract.extract(response.url).domain)
