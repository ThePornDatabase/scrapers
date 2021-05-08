import re

import dateparser
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


class PrivateSpider(BaseSceneScraper):
    name = 'PuffyNetwork'
    network = "Puffy Network"

    start_urls = [
        'https://www.puffynetwork.com/'
        ## 'https://www.eurobabefacials.com'
        ## 'https://www.simplyanal.com'
        ## 'https://www.weliketosuck.com'
        ## 'https://www.wetandpissy.com'
        ## 'https://www.wetandpuffy.com'

    ]

    selector_map = {
        'title': '//h2[@class="title"]/span/text()',
        'description': '//div[@class="show_more"]/text()[1]',
        'date': '//dl/dt[contains(text(),"Released on:")]/span/text()',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//dl/dd/a/text()',
        'tags': '//p[@class="tags"]/a/text()',
        'external_id': 'videos\/(.*)',
        'trailer': '//div[@id="videoplayer"]//video/source/@src',
        'pagination': '/videos/page-%s/?&sort=recent'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//a[@class="image-wrapper"]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        site = response.xpath('//h2[@class="title"]//div[contains(text(),"Site:")]/a/text()').get()
        site = match_site(site)
        if site:
            return site.strip()
        else:
            return "Puffy Network"

    def get_id(self, response):
        search = re.search(self.get_selector_map(
            'external_id'), response.url, re.IGNORECASE)
        search = search.group(1)
        if "/" in search:
            search = search.replace("/","").strip()
        return search
