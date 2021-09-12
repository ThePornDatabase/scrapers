import re
import dateparser
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class PornWorldScraper(BaseSceneScraper):
    name = 'PornWorldAlt'
    network = 'ddfnetwork'

    start_urls = [
        'https://www.sandysfantasies.com/',
        'https://cherryjul.com/',
        'https://eveangelofficial.com/',
        'https://sexvideocasting.com/',
        'https://hairytwatter.net/'
    ]

    selector_map = {
        'title': "//h1[@class='videotitle']/text()",
        'description': "//p[@class='vText']/text()",
        'date': "",
        'image': '//div[@class="videoPlayerContainer"]/img/@src | //video/@poster',
        'performers': "",
        'tags': "",
        'external_id': 'videos\\/.*\\/(\\d+)',
        'trailer': '//video/source/@src',
        'pagination': '/videos/%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class,"videoBlock")]')
        for scene in scenes:
            performerlist = scene.xpath('./div/div[@class="featuring"]/a/text()').getall()
            if performerlist:
                performers = [j.strip() for j in performerlist]
            scene = scene.xpath('./div[@class="videoPic"]/a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                if performers:
                    yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta={'performers': performers})
                else:
                    yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_date(self, response):
        search = re.search('Added:\\ (.*?\\d{2,4})\\ {1,3}', response.text)
        return dateparser.parse(search.group(1)).isoformat()

    def get_performers(self, response):
        return ["No Performers Available"]
