import re
import scrapy
import tldextract

from tpdb.BaseSceneScraper import BaseSceneScraper


def match_site(argument):
    match = {
        'brutalpov': "Brutal POV",
    }
    return match.get(argument, argument)


class FetishNetworkAltSpider(BaseSceneScraper):
    name = 'FetishNetworkAlt'
    network = "Fetish Network"
    parent = "Fetish Network"

    start_urls = [
        'http://www.brutalpov.com/'
    ]

    selector_map = {
        'title': '//div[contains(@class,"video-title")]/h1/text()',
        'description': '//div[contains(@class,"scene-desc")]/text()',
        'date': '//div[contains(@class,"date-views")]/span[1]/text()',
        'image': '//video[@id="videoplayer"]/@poster',
        'performers': '//div[@class="content-label" and contains(text(),"Starring:")]/following-sibling::div/text()',
        'tags': '//div[@class="content-label" and contains(text(),"Categories:")]/following-sibling::div/text()',
        'external_id': '(.*)',
        'trailer': '//div[@id="videoplayer"]//source/@src',
        'pagination': '/videos/page-%s/?&sort=recent'
    }

    def get_scenes(self, response):
        if "brutalpov" in response.url:
            scenes_list = response.xpath('//div[@class="date-img-wrapper"]/a/@href').getall()
            scenes = ["http://www.brutalpov.com/t2/" + listitem for listitem in scenes_list]
        else:
            scenes = response.xpath('//a[@class="image-wrapper"]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        site = response.xpath('//div[contains(@class,"bigtext-section")]/h3/span[contains(text(),"Videos")]/text()').get()
        if site:
            if "Videos" in site:
                site = re.search('(.*) Videos', site).group(1)
                if site:
                    site = site.strip()

        if not site:
            site = tldextract.extract(response.url).domain
        if site:
            site = match_site(site)

        return site

    def get_tags(self, response):
        if self.get_selector_map('tags'):
            tags = self.process_xpath(
                response, self.get_selector_map('tags')).getall()
            if tags:
                return list(map(lambda x: x.strip().title(), tags))
        return []

    def get_next_page_url(self, base, page):
        if "brutalpov" in base:
            pagination = '/t2/show.php?a=2205_%s&nats=typein.4.106.275.0.0.0.0.0'
        else:
            pagination = '/t2/show.php?a=2074_%s'

        return self.format_url(base, pagination % page)

    def get_id(self, response):
        search = re.search(r'\/(\d+)\/', response.url, re.IGNORECASE).group(1)
        return search

    def get_image(self, response):
        image = self.process_xpath(response, self.get_selector_map('image')).get()
        if not image:
            image = response.xpath('//video[contains(@id,"my-video")]/@poster').get()

        if image:
            image = "http://www.fetishnetwork.com/t2/" + image
            return self.format_link(response, image)
        return ''
