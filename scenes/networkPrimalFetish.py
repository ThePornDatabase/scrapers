import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkPrimalFetishSpider(BaseSceneScraper):
    name = 'PrimalFetish'
    network = 'Primal Fetish Network'
    parent = 'Primal Fetish Network'

    start_urls = [
        'https://primalfetishnetwork.com',
    ]

    selector_map = {
        'title': '//h1[@class="video__movieTitle"]/text()',
        'description': '//span[contains(@class, "update_description")]//text()',
        'date': '//h1/following-sibling::div[1]/div[@class="video__data" and contains(text(), "Date")]/text()[1]',
        're_date': r'(\d{2}.*? \w{3} \d{4})',
        'date_formats': ['%d %b %Y'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//span[@class="video__listTitle" and contains(text(), "Models:")]/following-sibling::div[1]/a/span/text()',
        'tags': '//div[contains(@class, "--tags")]/a/text()',
        'external_id': r'.*/(.*?)\.htm',
        'pagination': '/videos/page%s.html'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "videoElement")]')
        for scene in scenes:
            meta['trailer'] = scene.xpath('./@data-video').get()
            scene = scene.xpath('./a[1]/@href').get()
            meta['id'] = re.search(r'-(\d+)\.htm', scene).group(1)
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_title(self, response):
        title = super().get_title(response)
        if " - Primal Fetish" in title:
            title = re.search(r'(.*) - Primal Fetish', title).group(1)
        return title

    def get_tags(self, response):
        tags = super().get_tags(response)
        tags2 = []
        for tag in tags:
            if "primal" not in tag.lower() and tag.strip()[0] != "." and tag.strip()[:-1] != ".":
                tags2.append(string.capwords(tag.strip()))
        return tags2

    def get_site(self, response):
        site = response.xpath('//span[contains(text(), "Studios:")]/following-sibling::a[1]/text()')
        if site:
            site = site.get()
            if "primal" not in site.lower():
                site = "Primals " + site
            return site
        else:
            return "Primal Fetish"
