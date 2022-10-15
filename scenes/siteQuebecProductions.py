import re
import string
import scrapy
from googletrans import Translator
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteQuebecProductionsSpider(BaseSceneScraper):
    name = 'QuebecProductions'
    site = 'Quebec Productions'
    parent = 'Quebec Productions'
    network = 'GammaEnterprises'
    start_urls = [
        'https://www.quebecproductions.com']

    selector_map = {
        'title': '//h1[@class="title"]/text()',
        'description': '//div[contains(@class,"sceneDesc")]//text()',
        'date': '//div[@class="updatedDate"]/b/following-sibling::text()',
        'date_formats': ['%Y-%m-%d'],
        'image': '//div[contains(@class, "Giraffe_ScenePlayer")]/script[contains(text(), "gammacdn.com")]/text()',
        're_image': 'picPreview.*?(http.*?\\.jpg).*',
        'performers': '//div[@class="pornstarNameBox"]/a//text()',
        'tags': '//div[contains(@class,"sceneColCategories")]/a/text()',
        'external_id': '.*/(\\d+)',
        'trailer': '//script[contains(text(), ".mp4")]/text()',
        're_trailer': '.*url\\":\\"(.*?\\.mp4).*',
        'pagination': '/en/scenes/updates/%s/Category/0/Pornstar/0'}

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class,"tlcItem")]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=(self.format_link(response, scene)), callback=(self.parse_scene))

    def get_title(self, response):
        translator = Translator()
        title = super().get_title(response).lower()
        if title:
            if title == 'salope de bureau':
                title = 'Office Slut'
            elif title == 'voleuses cochonnes':
                title = 'Dirty Thieves'
            else:
                title = translator.translate((title.lower()), src='fr', dest='en')
                title = string.capwords(title.text)
        return title

    def get_description(self, response):
        translator = Translator()
        description = response.xpath('//div[contains(@class,"sceneDesc")]//text()')
        if description:
            description = list(map(lambda x: x.strip(), description.getall()))
            description = ' '.join(description)
            description = translator.translate((description.strip()), src='fr', dest='en')
            description = description.text.strip()
            return description
        return ''

    def get_tags(self, response):
        translator = Translator()
        tags = super().get_tags(response)
        if tags:
            tags2 = []
            for tag in tags:
                tag = translator.translate(tag, src='fr', dest='en')
                tag = tag.text
                tag = tag.lower().replace('cat', 'pussy')
                tag = tag.lower().replace('buttocks', 'ass')
                tag = tag.lower().replace('hearing', 'audition')
                tag = tag.lower().replace('congregation', 'Group Sex')
                tag = tag.lower().replace('smoking pipe', 'blowjob')
                tag = tag.lower().replace('trip to three', 'threesome')
                tag = tag.lower().replace('québécois', '')
                tag = tag.lower().replace('francophone', '')
                tag = tag.lower().replace('stuff', '')
                if tag:
                    tags2.append(tag.title().strip())
                tags = tags2

            return tags

    def get_trailer(self, response):
        trailer = super().get_trailer(response)
        return trailer.replace('\\', '')

    def get_image(self, response):
        image = super().get_image(response)
        return image.replace('\\', '')
