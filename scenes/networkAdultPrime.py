import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper

# ~ The following sites are included in this scraper:
# ~ -------------------------------------------------
# ~ "4K CFNM",
# ~ "Adultprime Originals",
# ~ "BBvideo",
# ~ "Beauty and the Senior",
# ~ "Bondagettes",
# ~ "Brasil Bimbos",
# ~ "Club Bang Boys",
# ~ "Club Castings",
# ~ "Club SweetHearts",
# ~ "Color Climax",
# ~ "Cuckoldest",
# ~ "DaringSex HD",
# ~ "Digital Desire",
# ~ "Elegant Raw",
# ~ "Evil Playgrounds",
# ~ "Family Screw",
# ~ "Fan Fuckers",
# ~ "Fetish Prime",
# ~ "Fixxxion",
# ~ "Grandmams",
# ~ "GrandparentsX",
# ~ "Group Banged",
# ~ "Groupsex Games",
# ~ "Hollandsche Passie",
# ~ "Jim Slip",
# ~ "Lara's Playground",
# ~ "Lets Go Bi",
# ~ "Manko88",
# ~ "Mature Van",
# ~ "My Milfz",
# ~ "Peep Leak",
# ~ "Plumperd",
# ~ "Pornstar Classics",
# ~ "Pornstars Live",
# ~ "Redlight Sex Trips",
# ~ "Retro Raw",
# ~ "Shadowslaves",
# ~ "Sinful Raw",
# ~ "Sinful Soft",
# ~ "Sinful XXX",
# ~ "Southern Sins",
# ~ "Submissed",
# ~ "Summer Sinners",
# ~ "Sweethearts Classics",
# ~ "SWhores",
# ~ "Teenrs",
# ~ "The Pain Files",
# ~ "Uk-Flashers",
# ~ "Vintage Classic Porn",
# ~ "VR Teenrs",
# ~ "Young Busty",


class NetworkAdultPrimeSpider(BaseSceneScraper):
    name = 'AdultPrime'
    network = 'Adult Prime'

    start_urls = [
        'https://adultprime.com',
    ]

    selector_map = {
        'title': '//span[@class="active-crumb"]/text()',
        # ~ 'description': '//p[contains(@class,"ap-limited-description-text")]/text()',  # Blocked due to public scenes having generic site descriptions
        'description': '',
        'date': '//div[contains(@class, "player-wrapper")]//span[@class="description-releasedate"]/text()',
        'date_formats': ['%d.%m.%Y','%d-%m-%Y'],
        'image': '//div[contains(@class,"update-video-wrapper")]/a/div/@style|//video/@poster',
        're_image': r'(http.*\.jpg)',
        'performers': '//p[contains(@class,"update-info-line")]/b[contains(text(), "Performer")]/following-sibling::a/text()',
        'tags': '//b[contains(text(), "Niches")]/following-sibling::text()',
        'external_id': r'.*/(\d+)',
        'trailer': '',
        'pagination': '/studios/videos?q=&website=&niche=&year=&type=&sort=&page=%s#focused'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="row portal-grid"]//div[@class="overlay-wrapper"]/div[1]/a/@href').getall()
        for scene in scenes:
            sceneid = re.search(r'Id=(\d+)', scene)
            if sceneid:
                sceneid = sceneid.group(1)
                scene = "https://adultprime.com/studios/video/" + sceneid
                yield scrapy.Request(scene, callback=self.parse_scene)

    def get_site(self, response):
        site = response.xpath('//b[contains(text(), "Studio")]/a[1]/text()')
        if site:
            site = site.get()
        else:
            site = "AdultPrime"
        return site.strip()

    def get_parent(self, response):
        site = response.xpath('//b[contains(text(), "Studio")]/a[1]/text()')
        if site:
            site = site.get()
        else:
            site = "AdultPrime"
        return site.strip()

    def get_tags(self, response):
        tags = response.xpath('//b[contains(text(), "Niches")]/following-sibling::text()')
        if tags:
            tags = tags.get()
            tags = tags.split(",")
            tags = list(map(lambda x: x.strip(), tags))
            if "" in tags:
                tags.remove("")
        return tags

    def get_image(self, response):
        image = super().get_image(response)
        if image and len(image) < 10:
            image = ""
        return image
