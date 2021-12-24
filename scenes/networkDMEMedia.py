import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


def match_site(argument):
    match = {
        'adultdoorway': "Adult Doorway",
        'amateurthroats': "Amateur Throats",
        'analrecruiters': "Anal Recruiters",
        'bustyamateurboobs': "Busty Amateur Boobs",
        'clubamberrayne': "Club Amber Rayne",
        'facialabuse': "Facial Abuse",
        'hardcoredoorway': "Hardcore Doorway",
        'herfirstporn': "Her First Porn",
        'hugerubberdicks': "Huge Rubber Dicks",
        'joethepervert': "Joe the Pervert",
        'latinaabuse': "Latina Abuse",
        'lesbianslovesex': "Lesbians Love Sex",
        'monstercockmadness': "Monster Cock Madness",
        'nastylittlefacials': "Nasty Little Facials",
        'pinkkittygirls': "Pink Kitty Girls",
        'sexysuckjobs': "Sexy Suck Jobs",
        'spermsuckers': "Sperm Suckers",
        'thehandjobsite': "The Handjob Site",
        'thepantyhosesite': "The Pantyhose Site",
    }
    return match.get(argument, argument)


class NetworkDMEMediaSpider(BaseSceneScraper):
    name = 'DMEMedia'
    network = 'DME Media'

    start_urls = [
        'https://tour5m.adultdoorway.com',
        'https://tour5m.amateurthroats.com',
        'https://tour5m.analrecruiters.com',
        'https://tour5m.bustyamateurboobs.com',
        'https://tour5m.clubamberrayne.com',
        'https://tour5m.facialabuse.com',
        'https://tour5m.hardcoredoorway.com',
        'https://tour5m.herfirstporn.com',
        'https://tour5m.hugerubberdicks.com',
        'https://tour5m.joethepervert.com',
        'https://tour5m.latinaabuse.com',
        'https://tour5m.lesbianslovesex.com',
        'https://tour5m.monstercockmadness.com',
        'https://tour5m.nastylittlefacials.com',
        'https://tour5m.pinkkittygirls.com',
        'https://tour5m.sexysuckjobs.com',
        'https://tour5m.spermsuckers.com',
        'https://tour5m.thehandjobsite.com',
        'https://tour5m.thepantyhosesite.com',
    ]

    selector_map = {
        'title': '//span[@class="update_title"]/text()|//h1[@class="update_title"]/text()',
        'description': '//span[contains(@class, "latest_update_description")]//text()',
        'date': '//span[contains(@class,"update_date")]/text()',
        'image': '//script[contains(text(), "poster=")]/text()',
        'image_blob': True,
        're_image': r'poster=\"(.*?)\".*',
        'performers': '',
        'tags': '//span[@class="update_tags"]/a/text()',
        'external_id': r'.*/(.*?).html',
        'trailer': '',
        'pagination': '/tour/categories/movies_%s_d.html'
    }

    def start_requests(self):
        for link in self.start_urls:
            yield scrapy.Request(link,
                                 callback=self.start_requests2,
                                 headers=self.headers,
                                 cookies=self.cookies)

    def start_requests2(self, response):
        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, self.page),
                                 callback=self.parse,
                                 meta={'page': self.page},
                                 headers=self.headers,
                                 cookies=self.cookies)

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="updateItem"]/a/@href').getall()
        for scene in scenes:
            scene = "/tour/" + scene
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        return match_site(super().get_site(response))

    def get_parent(self, response):
        return match_site(super().get_site(response))

    def get_tags(self, response):
        tags = super().get_tags(response)
        site = self.get_site(response)
        if site in tags:
            tags.remove(site)
        if "Ss - Movies" in tags:
            tags.remove("Ss - Movies")
        if "Ss - Photos" in tags:
            tags.remove("Ss - Photos")
        return tags
