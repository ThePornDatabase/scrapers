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
        'ghettogaggers': "Ghetto Gaggers",
        'ebonycumdumps': "Ebony Cum Dumps"
    }
    return match.get(argument, argument)


class NetworkDMEMediaV2Spider(BaseSceneScraper):
    name = 'DMEMediaV2'
    network = 'DME Media'

    start_urls = [
        'https://tour5m.amateurthroats.com',
        'https://tour5m.analrecruiters.com',
        'https://tour5m.bustyamateurboobs.com',
        'https://tour5m.clubamberrayne.com',
        'https://tour5m.facialabuse.com',
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
        'https://tour5m.ghettogaggers.com',
        'https://tour5m.ebonycumdumps.com'
    ]

    selector_map = {
        'title': '//h1[@class="highlight"]/text()',
        'description': '//div[contains(@class, "update-info-block")]/text()',
        'date': '//div[contains(@class, "update-info-row")]/strong/following-sibling::text()',
        're_date': r'(\w+ \d{1,2}, \d{4})',
        'date_formats': ['%B %d, %Y'],
        'duration': '//div[contains(@class, "update-info-row")]/strong/following-sibling::text()',
        're_duration': r'((?:\d{1,2}\:)?\d{2}\:\d{2})',
        'image': '//img[contains(@class, "update_thumb")]/@src0_3x|//img[contains(@class, "update_thumb")]/@src0_4x|//img[contains(@class, "update_thumb")]/@src0_2x|//img[contains(@class, "update_thumb")]/@src0_1x',
        'performers': '',
        'tags': '//ul[@class="tags"]/li/a/text()',
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
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "videothumb")]|//div[contains(@class,"item-thumb")]')
        for scene in scenes:
            image2 = scene.xpath('.//img/@src')
            if image2:
                meta['image2'] = image2.get()
            scene = scene.xpath('.//a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene) and "404-error" not in response.url:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_site(self, response):
        return match_site(super().get_site(response))

    def get_parent(self, response):
        return match_site(super().get_site(response))

    def get_tags(self, response):
        tags = super().get_tags(response)
        site = self.get_site(response)
        if site in tags:
            tags.remove(site)
        tags2 = []
        for tag in tags:
            if "movie" not in tag.lower() and "photos" not in tag.lower():
                tags2.append(tag)

        return tags2

    def get_image(self, response):
        image = super().get_image(response)
        if ".jpg" not in image:
            if "ghettogaggers" in response.url or "ebonycumdumps" in response.url:
                image = response.xpath('//img[contains(@src, "full.jpg")]/@src')
                if image:
                    image = image.get()
                if "jpg" not in image:
                    image = response.xpath('//script[contains(text(), "poster")]/text()')
                    if image:
                        image = re.search(r'poster=\"(http.*?)\"', image.get()).group(1)
        if not image:
            image = response.meta['image2']
        return image

    def get_image_blob(self, response):
        meta = response.meta
        if 'image_blob' not in self.get_selector_map():
            image = self.get_image(response)
            image_blob = self.get_image_blob_from_link(image)
            if image_blob:
                return image_blob
            image = meta['image2']
            image_blob = self.get_image_blob_from_link(image)
            if image_blob:
                return image_blob

        return None
