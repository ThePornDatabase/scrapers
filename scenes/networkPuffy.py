import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


def match_site(argument):
    match = {
        'Eurobabefacials': "Euro Babe Facials",
        'Simplyanal': "Simply Anal",
        'Weliketosuck': "We Like to Suck",
        'Wetandpissy': "Wet and Pissy",
        'Wetandpuffy': "Wet and Puffy",
    }
    return match.get(argument, "Puffy Network")


class PuffySpider(BaseSceneScraper):
    name = 'PuffyNetwork'
    network = "Puffy Network"

    start_urls = [
        'https://www.puffynetwork.com/'
        # 'https://www.eurobabefacials.com'
        # 'https://www.simplyanal.com'
        # 'https://www.weliketosuck.com'
        # 'https://www.wetandpissy.com'
        # 'https://www.wetandpuffy.com'
    ]

    selector_map = {
        'title': "//h2[@class='title']/span/text()",
        'description': "//section[@class='downloads']//div[@class='show_more']/text()",
        'date': "//section[contains(@class, 'downloads2')]/dl[1]/dt[2]/span/text()",
        'image': "//div[@id='videoplayer']//video/@poster",
        'performers': "//section[contains(@class, 'downloads2')]/dl[1]/dd[1]//a/text()",
        'tags': "//p[@class='tags']/a[contains(@href,'tag')]/text()",
        'external_id': 'videos/(.+)/?$',
        'trailer': '//div[@id="videoplayer"]//source/@src',
        'pagination': '/videos/page-%s/?&sort=recent'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//a[@class="image-wrapper"]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        site = response.xpath(
            '//h2[@class="title"]//div[contains(text(),"Site:")]/a/text()').get()
        site = match_site(site)
        if site:
            return site.strip()
        return "Puffy Network"

    def get_tags(self, response):
        if self.get_selector_map('tags'):
            tags = self.process_xpath(
                response, self.get_selector_map('tags')).getall()
            if tags:
                return list(map(lambda x: x.strip().title(), tags))
        return []

    def get_image(self, response):
        image = self.process_xpath(response, self.get_selector_map('image')).get()
        if not image:
            image = response.xpath('//meta[@property="og:image"]/@content').get()
        if not image:
            image = response.xpath('//video[1]/@poster').get()

        if image:
            return self.format_link(response, image)
        return ''
