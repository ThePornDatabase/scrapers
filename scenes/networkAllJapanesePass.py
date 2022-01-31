import re
import string
import scrapy
import tldextract

from tpdb.BaseSceneScraper import BaseSceneScraper


def match_site(argument):
    match = {
        '18tokyo': 'Japanese Teens',
        'analnippon': 'Anal Nippon',
        'bigtitstokyo': 'Big Tits Tokyo',
        'bukkakenow': 'Bukkake Now',
        'japaneseflashers': 'Japanese Flashers',
        'japanesematures': 'Japanese Matures',
        'japaneseslurp': 'Japanese Slurp',
        'jcosplay': 'Japanese Cosplay',
        'jpmilfs': 'JP Milfs',
        'jpnurse': 'JP Nurse',
        'jpshavers': 'Shaved Pussy',
        'jpteacher': 'Japanese Teacher',
        'jschoolgirls': 'Japanese School Girls',
        'myracequeens': 'My Race Queens',
        'ocreampies': 'O Creampies',
        'officesexjp': 'Japanese Office Sex',
        'outdoorjp': 'Outdoor JP',
        'povjp': 'POVJP',
        'tokyobang': 'Tokyo Bang',
        'wierdjapan': 'Weird Japan',
    }
    return match.get(argument, '')


class NetworkAllJapanesePassSpider(BaseSceneScraper):
    name = 'AllJapanesePass'
    network = "All Japanese Pass"
    parent = "All Japanese Pass"

    start_urls = [
        'https://18tokyo.com',
        'https://analnippon.com',
        'https://bigtitstokyo.com',
        'https://bukkakenow.com',
        'https://japaneseflashers.com',
        'https://japanesematures.com',
        'https://japaneseslurp.com',
        'https://jcosplay.com',
        'https://jpmilfs.com',
        'https://jpnurse.com',
        'https://jpshavers.com',
        'https://jpteacher.com',
        'https://jschoolgirls.com',
        'https://myracequeens.com',
        'https://ocreampies.com',
        'https://officesexjp.com',
        'https://outdoorjp.com',
        'https://povjp.com',
        'https://tokyobang.com',
        # ~ #'https://wierdjapan.com',  #Requires Membership
    ]

    selector_map = {
        'title': '//span[@class="b-breadcrumb-text"]/text()',
        'description': '//p[@itemprop="description"]/text()',
        'date': '//div[contains(text(),"Added")]/following-sibling::div[1]/text()',
        'date_formats': ['%d %b %Y'],
        'image': '//div[@class="b-player-body"]/div/img/@src',
        'image_blob': True,
        'performers': '//p[@itemprop="actor"]/a/span/text()',
        'tags': '//p[@class="b-video-info__text"]/a[contains(@href,"/category/") or contains(@href,"/tag/")]/text()',
        'external_id': r'.*\/(.*?)$',
        'trailer': '',
        'pagination': '/videos/newest/%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//a[contains(@class,"b-videos-item-link")]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_title(self, response):
        title = response.xpath(self.get_selector_map('title')).get()
        if title:
            title = string.capwords(title)
            return title.strip()

        return None

    def get_site(self, response):
        parsed_uri = tldextract.extract(response.url)
        domain = parsed_uri.domain
        site = match_site(domain)
        if not site:
            site = tldextract.extract(response.url).domain

        return site

    def get_tags(self, response):
        if self.get_selector_map('tags'):
            tags = self.process_xpath(response, self.get_selector_map('tags'))
            if tags:
                return list(map(lambda x: x.strip().title(), tags.getall()))

        return []

    def get_performers(self, response):
        performers = self.process_xpath(response, self.get_selector_map('performers')).getall()
        if performers:
            if "Japanese AV Model" in performers:
                performers.remove("Japanese AV Model")
            if "Unknown Model" in performers:
                performers.remove("Unknown Model")
            if "Amateur" in performers:
                performers.remove("Amateur")
            return list(map(lambda x: x.strip(), performers))

        return []

    def get_image(self, response):
        image = self.process_xpath(response, self.get_selector_map('image'))
        if image:
            image = self.get_from_regex(image.get(), 're_image')
            if image:
                image = image.replace(" ", "%20")
                return self.format_link(response, image)

        return None
