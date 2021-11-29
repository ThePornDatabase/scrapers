import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


def match_site(argument):
    match = {
        'filthygapers': 'Filthy Gapers',
        'gynoexclusive': 'Gyno Exclusive',
        'ihuntmycunt': 'I Hunt My Cunt',
        'maturegapers': 'Mature Gapers',
        'maturegynoexam': 'Mature Gyno Exam',
        'maturegynospy': 'Mature Gyno Spy',
        'nastypublicsex': 'Nasty Public Sex',
        'oldsfuckdolls': 'Olds Fuck Dolls',
    }
    return match.get(argument, argument)


class NetworkDollsHubSpider(BaseSceneScraper):
    name = 'DollsHub'
    network = 'DollsHub'

    start_urls = [
        'https://www.filthygapers.com',
        'https://www.gynoexclusive.com',
        'https://www.ihuntmycunt.com',
        'https://maturegapers.com',
        'https://www.maturegynoexam.com',
        'https://www.maturegynospy.com',
        'https://www.nastypublicsex.com',
        'https://www.oldsfuckdolls.com',
    ]

    selector_map = {
        'title': '//div[contains(@class, "scence-title-name")]/h2/text()',
        'description': '//h4[contains(text(), "Description")]/following-sibling::p/text()',
        'date': '',
        'image': '//video/@data-poster',
        'performers': '//text()[contains(., "Featuring")]/following-sibling::span/a/text()',
        'tags': '',
        'external_id': r'name=(.*)',
        'trailer': '//video/source/@src',
        'pagination': '/scenes?page=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="black-box2"]//a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_id(self, response):
        extern_id = super().get_id(response)
        extern_id = extern_id.replace("%20", " ")
        extern_id = re.sub(r'[^A-Za-z0-9 ]+', '', extern_id.lower())
        extern_id = extern_id.replace(" ", "-")
        return extern_id

    def get_tags(self, response):
        if "gyno" in response.url:
            return ['Doctor/Nurse', 'Doctors Office / Hospital', 'Medical Fetish', 'European']
        if "gaper" in response.url:
            return ['Gaping', 'European']
        if "ihunt" in response.url:
            return ['Masturbation', 'European']
        if "oldsfuck" in response.url:
            return ['Older / Younger', 'European']
        if "nastypublic" in response.url:
            return ['Public Sex', 'Outdoors', 'European']
        return []

    def get_performers(self, response):
        performers = super().get_performers(response)
        if "Freaky Doctor" in performers:
            performers.remove("Freaky Doctor")
        return performers

    def get_site(self, response):
        return match_site(super().get_site(response))

    def get_parent(self, response):
        return match_site(super().get_parent(response))
