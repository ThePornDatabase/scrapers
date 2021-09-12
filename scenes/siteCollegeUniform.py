import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteCollegeUniformSpider(BaseSceneScraper):
    name = 'CollegeUniform'
    network = 'College Uniform'

    start_urls = [
        'https://college-uniform.com',
    ]

    selector_map = {
        'title': '//span[@class="update_title"]/text()',
        'description': '//span[contains(@class,"description")]/text()',
        'date': '//span[@class="update_date"]/text()',
        'date_formats': ['%m/%d/%Y'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//span[@class="tour_update_models"]/a/text()',
        'tags': '//comment()[contains(., "Tags")]',
        'external_id': r'.*\/(.*?).html',
        'trailer': '',
        'pagination': '/categories/updates_%s_p.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="update_details" and .//div[@class="update_counts" and contains(text(), "video")]]/a[1]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_id(self, response):
        return super().get_id(response).lower().strip()

    def get_tags(self, response):
        if self.get_selector_map('tags'):
            tags = self.process_xpath(response, self.get_selector_map('tags'))
            if tags:
                tags = tags.getall()
                tags = "".join(tags)
                tags = re.findall(r'<a href.*\">(.*?)<\/a', tags)
                for tag in tags:
                    if re.search(r'\d{3}', tag):
                        tags.remove(tag)
                return list(map(lambda x: x.strip().title(), tags))

        return []

    def get_site(self, response):
        return "College Uniform"

    def get_parent(self, response):
        return "College Uniform"
