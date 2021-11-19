import re
import scrapy
import tldextract
from tpdb.BaseSceneScraper import BaseSceneScraper


def match_site(argument):
    match = {
        'dirty-chubby': 'Dirty-Chubby',
        'dirtycasting': 'Dirty Casting',
        'lustyxxxfamily': 'Lusty Family',
        'pornmuschimovie': 'Porn Muschi Movie',
        'sexgamesprivate': 'Sex Games Private',
        'xxxrealityfuck': 'XXX Reality Fuck',
    }
    return match.get(argument, argument)


class NetworkPornMuschiMovieSpider(BaseSceneScraper):
    name = 'PornMuschiMovie'
    network = 'Porn Muschi Movie'

    start_urls = [
        'https://pornmuschimovie.com',
    ]

    selector_map = {
        'title': '//h1[@class="videoTitle"]/text()',
        'description': '',
        'date': '//div[@class="videoInfo"]',
        're_date': r'(\d{4}/\d{1,2}/\d{1,2})',
        'date_formats': ['%Y/%m/%d'],
        'image': '//div[@class="player"]/img/@src|//div[@class="player"]//video/@poster',
        'performers': '',
        'tags': '//div[@class="videoTags"]/a/text()',
        'external_id': r'video/(\d+)/',
        'trailer': '',
        'pagination': '/updates?p=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="scene"]/div[@class="wrapper"]//a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        image = self.process_xpath(response, self.get_selector_map('image'))
        if image:
            site = tldextract.extract(image.get()).domain
        else:
            site = tldextract.extract(response.url).domain
        return match_site(site)

    def get_parent(self, response):
        image = self.process_xpath(response, self.get_selector_map('image'))
        if image:
            site = tldextract.extract(image.get()).domain
        else:
            site = tldextract.extract(response.url).domain
        return match_site(site)

    def get_tags(self, response):
        image = self.process_xpath(response, self.get_selector_map('image'))
        if image:
            site = tldextract.extract(image.get()).domain
        else:
            site = tldextract.extract(response.url).domain

        tags = super().get_tags(response)
        tags2 = tags.copy()
        for tag in tags2:
            if site.lower() in tag.lower():
                tags.remove(tag)

        return tags
