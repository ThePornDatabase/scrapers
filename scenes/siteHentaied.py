import json
import re

import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class siteHentaiedSpider(BaseSceneScraper):
    name = 'Hentaied'
    network = 'Hentaied'
    parent = 'Hentaied'
    site = 'Hentaied'

    start_urls = [
        'https://hentaied.com/',
    ]

    # The JSON-LD VideoObject moved out of div.shortcode-wrapper, which is why the old
    # scoped selectors returned nothing and left title=None for the pipeline.  It also
    # carries the description, date, duration and trailer, so it is read directly.
    selector_map = {
        'title': '//h1//text()',
        'description': '',
        'date': '',
        'image': '//meta[@property="og:image"]/@content',
        'duration': '//div[contains(@class, "durationandtime")]/div/text()[contains(., ":")]',
        'performers': '//div[@class="tagsmodels"]/a/text()|//img[contains(@alt, "model")]/following-sibling::div[contains(@class, "taglist")]/a/text()',
        'tags': '//ul[@class="post-categories"]/li/a/text()',
        'director': '//div[contains(@class, "director") and contains(@class, "tagsmodels")]//a/text()',
        'external_id': r'.*\/(.*?)$',
        'trailer': '',
        'pagination': '/all-videos/page/%s/',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//center[@class="vidcont"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_video_object(self, response):
        """Find the VideoObject entry in the page's JSON-LD @graph."""
        for block in response.xpath('//script[@type="application/ld+json"]/text()').getall():
            try:
                data = json.loads(block)
            except ValueError:
                continue
            graph = data.get('@graph') if isinstance(data, dict) and '@graph' in data else data
            for entry in (graph if isinstance(graph, list) else [graph]):
                if isinstance(entry, dict) and 'VideoObject' in str(entry.get('@type')):
                    return entry
        return {}

    def get_title(self, response):
        title = self.get_video_object(response).get('name')
        if title:
            return self.cleanup_title(title)
        return super().get_title(response)

    def get_description(self, response):
        description = self.get_video_object(response).get('description')
        if description:
            return self.cleanup_description(description)
        return ''

    def get_date(self, response):
        upload = self.get_video_object(response).get('uploadDate')
        if upload:
            upload = re.search(r'(\d{4}-\d{2}-\d{2})', upload)
            if upload:
                return upload.group(1)
        return None

    def get_duration(self, response):
        iso = self.get_video_object(response).get('duration')
        if iso:
            parts = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?$', iso.strip())
            if parts and any(parts.groups()):
                hours, minutes, seconds = (int(x or 0) for x in parts.groups())
                return str(hours * 3600 + minutes * 60 + seconds)
        return super().get_duration(response)

    def get_trailer(self, response):
        return self.get_video_object(response).get('contentUrl') or ''
