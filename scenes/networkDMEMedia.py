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

    # Deprecated, use DMEMediaV2 instead
    start_urls = [
        # ~ 'https://tour5m.amateurthroats.com',
        # ~ 'https://tour5m.analrecruiters.com',
        # ~ 'https://tour5m.herfirstporn.com',
        # ~ 'https://tour5m.hugerubberdicks.com',
        # 'https://tour5m.latinaabuse.com',
        # 'https://tour5m.lesbianslovesex.com',
        # ~ 'https://tour5m.monstercockmadness.com',
        # ~ 'https://tour5m.sexysuckjobs.com',
        # ~ 'https://tour5m.spermsuckers.com',
        # ~ # 'https://tour5m.adultdoorway.com', Just listing FacialAbuse scenes
        # 'https://tour5m.bustyamateurboobs.com',  # Moved to V2
        # 'https://tour5m.clubamberrayne.com', # Moved to V2
        # 'https://tour5m.facialabuse.com', # Moved to V2
        # ~ # 'https://tour5m.hardcoredoorway.com', Just listing from others
        # 'https://tour5m.joethepervert.com', # Moved to V2
        # 'https://tour5m.nastylittlefacials.com', # Moved to V2
        # 'https://tour5m.pinkkittygirls.com', # Moved to V2
        # 'https://tour5m.thehandjobsite.com', # Moved to V2
        # 'https://tour5m.thepantyhosesite.com', # Moved to V2
    ]

    selector_map = {
        'title': '//span[@class="update_title"]/text()|//h1[@class="update_title"]/text()',
        'description': '//span[contains(@class, "latest_update_description")]//text()',
        'date': '//span[contains(@class,"update_date")]/text()',
        'image1': '//script[contains(text(), "poster=")]/text()',
        'image2': '//div[@id="fakeplayer"]//img/@src',
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
        scenes = response.xpath('//div[@class="updateItem"]/a')
        for scene in scenes:
            imageholder = scene.xpath('./img/@src')
            if imageholder:
                imageholder = imageholder.get()
            else:
                imageholder = None
            scene = "/tour/" + scene.xpath('./@href').get()
            if re.search(self.get_selector_map('external_id'), scene) and "404-error" not in response.url:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta={'imageholder': imageholder})

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

    def get_image(self, response):
        image = response.xpath(self.get_selector_map('image2'))
        if image:
            return image.get()
        else:
            image = response.xpath(self.get_selector_map('image1'))
            if image:
                image = re.search(self.get_selector_map('re_image'), image.get())
                if image:
                    return image.group(1)
        if response.meta['imageholder']:
            return response.meta['imageholder']
        else:
            return ''
