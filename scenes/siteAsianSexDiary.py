import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteAsianSexDiarySpider(BaseSceneScraper):
    name = 'AsianSexDiary'
    network = 'Asian Sex Diary'
    parent = 'Asian Sex Diary'
    site = 'Asian Sex Diary'

    start_urls = [
        'https://asiansexdiary.com',
    ]

    selector_map = {
        'title': '//div[contains(@class, "cntn-wrp") and contains(@class, "artl-cnt")]//h2/text()',
        'description': '//div[@class="cntr"]/div[contains(@class, "artl-cnt")]//p|a/text()',
        'date': '//i[@class="fa fa-calendar-o"]/following-sibling::text()',
        're_date': r'(\w+ \d{1,2}, \d{4})',
        'date_formats': ['%b %d, %Y'],
        'image': '//div[@id="myOverlay"]/amp-img/@src',
        'performers': '//div[@class="update-info"]//a[contains(@href, "/model/")]/text()',
        'tags': '//div[@class="amp-category"]/span/a/text()',
        'external_id': r'.*/(.*?)/$',
        'trailer': '//div[contains(@class, "video-player")]/amp-video/@src',
        'pagination': '/category/conquests/page/%s/',
        'duration': '//div[contains(@class, "update-info")]//i[contains(@class,"fa-video-camera")]/ancestor::div/text()',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//article/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_description(self, response):
        description = super().get_description(response)
        description = re.sub('<[^<]+?>', '', description).strip()
        return description

    def get_duration(self, response):
        if 'duration' in self.get_selector_map():
            # Seems to return an array
            duration = self.get_element(response, 'duration', 're_duration')[0]
            if duration:
                if ":" in duration or re.search(r'(\d{1,2})M(\d{1,2})S', duration):
                    duration = self.duration_to_seconds(duration)
                return duration
        return ''
