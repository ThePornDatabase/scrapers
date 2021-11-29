import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class PrivateSpider(BaseSceneScraper):
    name = 'Private'
    network = "Private"

    start_urls = [
        'https://www.private.com',
        'https://www.privateblack.com',
        # 'https://www.analintroductions.com'
        # 'https://www.blacksonsluts.com'
        # 'https://www.iconfessfiles.com'
        # 'https://www.missionasspossible.com'
        # 'https://www.privatecastings.com'
        # 'https://www.privatefetish.com'
        # 'https://www.privatemilfs.com'
        # 'https://www.privatestars.com'
        # 'https://www.russianfakeagent.com'
        # 'https://www.russianteenass.com'
        # 'https://www.tightandteen.com'
        # 'https://www.trannytemptation.com'
    ]

    selector_map = {
        'title': '//meta[@itemprop="name"]/@content',
        'description': '//meta[@itemprop="description"]/@content',
        'date': '//meta[@itemprop="uploadDate"]/@content',
        'image': '//meta[@itemprop="thumbnailUrl"]/@content',
        'performers': '//ul[@class="scene-models-list"]/li/a[@data-track="PORNSTAR_NAME"]/text()',
        'tags': '//ul[@class="scene-tags"]/li/a/text()',
        'external_id': '\\/(\\d+)$',
        'trailer': '',
        'pagination': '/scenes/%s/'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="scene"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        site = response.xpath('//span[@class="title-site"]/text()').get()
        if site:
            return site.strip()
        elif "privateblack" in response.url:
            return "Private Black"
        return "Private"

    def get_parent(self, response):
        site = response.xpath('//span[@class="title-site"]/text()').get()
        if site:
            return site.strip()
        elif "privateblack" in response.url:
            return "Private Black"
        return "Private"
