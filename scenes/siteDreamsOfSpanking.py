import re
import html
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteDreamsOfSpankingSpider(BaseSceneScraper):
    name = 'DreamsOfSpanking'
    network = 'Dreams Of Spanking'

    start_urls = [
        'https://dreamsofspanking.com',
    ]

    selector_map = {
        'title': '//div[@id="product"]/h3/text()',
        'description': '//div[@class="long-description"]/p/text()',
        'date': '//div[@class="date"]/text()',
        're_date': r'Created\s+(\d{1,2}\s[a-zA-Z]{3}\s\d{4}).*',
        'date_formats': ['%d %b %Y'],
        'image': '//video/@poster|//img[@class="preview"]/@src',
        'performers': '//div[@class="performers"][1]/p/a/text()',
        'tags': '//p[@class="tags"]/a/text()',
        'external_id': r'item\/(.*)$',
        'trailer': '//div[@class="poster"]/video/source/@src',
        'pagination': '/scene/recent/%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="recent_update"]/h3/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        return "Dreams Of Spanking"

    def get_parent(self, response):
        return "Dreams Of Spanking"

    def get_description(self, response):
        description = self.process_xpath(response, self.get_selector_map('description'))
        if description:
            description = list(map(lambda x: x.strip(), description.getall()))
            description = " ".join(description)
            return html.unescape(description.strip())
        return ''

    def get_tags(self, response):
        tags = super().get_tags(response)
        for idx in range(len(tags)):
            tags[idx] = tags[idx].replace("|", "").replace("Solo-F", "Solo")

        if "DominanceSubmission" in tags:
            tags.remove('DominanceSubmission')
            tags.append('Domination')
            tags.append('Submission')

        performers = super().get_performers(response)
        tags = list(map(lambda x: x.strip().lower(), tags))
        for performer in performers:
            if performer.lower() in tags:
                tags.remove(performer.lower())

        tags = list(map(lambda x: x.strip().title(), tags))

        return tags
