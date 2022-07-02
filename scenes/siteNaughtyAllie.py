import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteNaughtyAllieSpider(BaseSceneScraper):
    name = 'NaughtyAllie'
    network = 'Naughty Allie'
    parent = 'Naughty Allie'
    site = 'Naughty Allie'

    start_urls = [
        'http://www.naughtyallie.com',
    ]

    selector_map = {
        'title': '//h2/text()',
        'description': '//p[contains(@class,"story")]//text()',
        'date': '',
        'image': '//div[@class="hidden faceimage"]/text()',
        'performers': '',
        'tags': '//div[contains(@class, "keywords")]/span/following-sibling::text()',
        'trailer': '',
        'external_id': r'/(v\d+)/',
        'pagination': '/freeguestarea/show.php?a=94_%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//h1[@id="epi-h1"]/a/@href').getall()
        for scene in scenes:
            scene = "/freeguestarea/" + scene
            if "?lid=" in scene:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_description(self, response):
        description = super().get_description(response)
        description = description.replace("TO READ THIS ENTIRE STORY CLICK HERE TO ACCESS MY MEMBERS AREA", "")
        description = description.replace(".....", "")
        return description

    def get_image(self, response):
        if 'image' in self.get_selector_map():
            image = self.get_element(response, 'image', 're_image')
            if isinstance(image, list):
                image = image[0]
            if image:
                image = "/freeguestarea/" + image
            return self.format_link(response, image).replace(' ', '%20')
        return ''

    def get_tags(self, response):
        tags = []
        taglist = response.xpath(self.get_selector_map('tags'))
        if taglist:
            taglist = taglist.get()
            tagtemp = taglist.split(",")
            tagtemp = list(map(lambda x: x.strip(), tagtemp))
            for tag in tagtemp:
                res = bool(re.match(r'\w*[A-Z]\w*', tag))
                if not res and "xxx" not in tag.lower():
                    tags.append(string.capwords(tag))
        return tags
