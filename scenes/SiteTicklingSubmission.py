import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteTicklingSubmissionSpider(BaseSceneScraper):
    name = 'TicklingSubmission'
    site = 'Tickling Submission'
    parent = 'Tickling Submission'
    network = 'Tickling Submission'

    start_urls = [
        'http://www.tickling-submission.com'
    ]

    selector_map = {
        'title': '//h1[contains(@class, "title")]/text()',
        'description': '//div[contains(@id,"content-body")]/div[1]/p/text()',
        'date': '//span[contains(text(), "Datum") or contains(text(), "Date")]/following-sibling::text()',
        'date_formats': ['%b %d %Y'],
        'image': '//div[@id="mediaspace"]/span//img/@src',
        'performers': '//div[@class="field-items"]//a[contains(@href, "performers")]/text()',
        'tags': '//div[@class="field-items"]//a[contains(@href, "category")]/text()',
        'trailer': '',
        'type': 'Scene',
        'external_id': r'.*/(.*?)/',
        'pagination': '/updates/?page=%s',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "field-image-profile")]/span/a[not(contains(@href, "freeclip"))]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_duration(self, response):
        duration = response.xpath('//div[@class="field-items"]//div[contains(text(), "Time:")]/following-sibling::text()')
        if duration:
            duration = duration.get()
            duration = duration.strip()
            duration = re.search(r'(\d{1,2}:\d{2}(?::\d{2})?)', duration)
            if duration:
                return self.duration_to_seconds(duration.group(1))
        return None

    def get_performers(self, response):
        performers = super().get_performers(response)
        description = super().get_description(response)
        if "Tickler" in performers:
            performers.remove("Tickler")
            performers.append("Mr. Tickler")
        if "Mr. Tickler" not in performers and "Mr. Tickler" in description:
            performers.append("Mr. Tickler")
        return performers
