from datetime import datetime

import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class CzechAvSpider(BaseSceneScraper):
    name = 'CzechAv'
    network = 'Czech Casting'

    start_urls = [
        'https://czechwifeswap.com',
        'https://czechstreets.com',
        'https://czechfantasy.com',
        'https://czechtantra.com',
        'https://czechpawnshop.com',
        'https://czechmegaswingers.com',
        'https://czechamateurs.com',
        'https://czechcouples.com',
        'https://czechmassage.com',
        'https://czechharem.com',
        'https://czechtoilets.com',
        'https://czechbitch.com',
        'https://czechgangbang.com',
        'https://czechhomeorgy.com',
        'https://czechorgasm.com',
        'https://czechtaxi.com',
        'https://czechparties.com',
        'https://czechlesbians.com',
        'https://czechsauna.com',
        'https://czechestrogenolit.com',
        'https://czechtwins.com',
        'https://czechcabins.com',
        'https://czechsnooper.com',
        'https://czechdungeon.com',
        'https://czechgardenparty.com',
        'https://czechsolarium.com',
        'https://czechsupermodels.com',
        'https://czechexperiment.com',
        'https://czechpool.com',
        'https://czechgame.com',
        'https://czechfirstvideo.com',
        'https://czechbangbus.com',
        'https://czechspy.com',
        'https://czechsharking.com',
    ]

    selector_map = {
        'title': "//h2[@class='nice-title']/text()",
        'description': "//div[contains(@class, 'description')]/text() | //div[@class='desc-text']//p/text()",
        'image': "//meta[@property='og:image']/@content",
        'tags': "",
        'external_id': '/tour\\/preview\\/(.+)/',
        'trailer': '',
        'pagination': '/tour/videos/page-%s/'
    }

    def get_scenes(self, response):
        scenes = response.xpath(
            '//div[contains(@class, "episode-list")]//div[contains(@class,"episode__preview")]//a/@href').getall()
        for scene in scenes:
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_performers(self, response):
        return ['Unknown Czech Performer']

    def get_date(self, response):
        return datetime.now().isoformat()
