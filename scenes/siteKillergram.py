import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


def match_site(argument):
    match = {
        'anal rehab': 'Anal Rehab',
        'get shafted': 'Baby Loves the Shaft',
        'bitch funkers': 'Bitch Funkers',
        'booty packers': 'Booty Back Packers',
        'brown sugar': 'Brown Sugar Rush',
        'burlesque xxx': 'Burlesque XXX',
        'college babes': 'College Babes Exposed',
        'cream my cunt': 'Cream My Cunt',
        'office antics': 'Cum Into My Office',
        'cum party sluts': 'Cum Party Sluts',
        'fetish sex clinic': 'Fetish Sex Clinic',
        'girly riders': 'Girly Riders',
        'gloryhole girls': 'Gloryhole Gaggers',
        'chain smokers': 'Hardcore Chain Smokers',
        'lets get slippy': 'Lets Get Slippy',
        'nylon cum sluts': 'Nylon Cum Sluts',
        'dogging missions': 'On a Dogging Mission',
        'pornostatic': 'Pornostatic',
        'rock chicks': 'Rock Chicks',
        'ru 4 hire': 'RU 4 Hire',
        'club babes': 'Sexy Club Babes',
        'space hoppers': 'Space Hoppers and Lolly Poppers',
        'tattooed sluts': 'Tattooed Fuck Sluts',
        'the handy man': 'The Handy Man',
        'the lady pimp': 'The Lady Pimp',
        'kinky couples': 'UK Reality Swingers',
        'porn stars utd': 'UK Soccer Babes',
        'street walkers': 'UK Street Walkers',
        'hard-fi sex': 'Urban Perversions',
        'voyeur cams': 'Voyeur Cam Sluts',
        'wife sluts': 'Wife Slut Adventures',
        'wishes cum true': 'Wishes Cum True',
        'killergram%20cuts': 'Killergram Cuts',
        'killergram platinum': 'Killergram Platinum',
    }
    return match.get(argument, argument)


class SiteKillergramSpider(BaseSceneScraper):
    name = 'Killergram'
    network = 'Killergram'
    parent = 'Killergram'

    start_urls = [
        'https://killergram.com',
    ]

    selector_map = {
        'description': '//table[contains(@class, "episodetext")]/tr[5]/td/text()',
        'date': '//table[contains(@class, "episodetext")]//span[contains(text(), "ublished")]/following-sibling::text()',
        'date_formats': ['%d %B %Y'],
        'image': '//table//td/img[contains(@name, "episode_001")]/@src',
        'performers': '//table[contains(@class, "episodetext")]//a[contains(@href, "model")]/text()',
        'tags': '',
        'trailer': '',
        'external_id': r'id=(\d+)',
        'pagination': '/home.asp?page=home&p=%s'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//comment()[contains(., "latest")]/following-sibling::div[contains(@id, "episodes")]//a[contains(@href, "id=")]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_title(self, response):
        title = response.xpath('//table//td/img[contains(@name, "episode_001")]/@src')
        if title:
            title = title.get()
            model = re.search(r'models/(.*?)/', title).group(1)
            title = re.search(r'models/.*?/(.*?)/', title).group(1)
            title = title.replace(model, "").replace("_", " ").replace("-", " ").strip()
            return self.cleanup_title(title)
        return ''

    def get_duration(self, response):
        duration = response.xpath('//table[contains(@class, "episodetext")]//span[contains(text(), "uration")]/following-sibling::text()')
        if duration:
            duration = re.search(r'(\d+) min', duration.get()).group(1)
            duration = str(int(duration) * 60)
            return duration
        return None

    def get_description(self, response):
        description = response.xpath(self.get_selector_map('description'))
        if description:
            description = " ".join(description.getall())
            return description.strip()
        return ''

    def get_site(self, response):
        site = response.xpath('//img[@id="episode_showcase"]/../@href')
        if site:
            site = site.get()
            site = re.search(r'site=(.*?)\&', site)
            if site:
                return self.cleanup_title(site.group(1))
        return "Killergram"
