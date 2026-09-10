import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteKinkyMistressesSpider(BaseSceneScraper):
    name = 'KinkyMistresses'
    network = 'Kinky Mistresses'
    parent = 'Kinky Mistresses'
    site = 'Kinky Mistresses'

    start_urls = [
        'https://www.kinkymistresses.com',
    ]

    # The site moved onto the shopmaker platform: the listing is /collections
    # (paginated /collections/page/N) and scenes are /collections/<slug>, so the
    # numeric -(\d{5,20})- id no longer appears in a URL anywhere.  The old
    # videodetails / videowrapper markup is gone with it.
    selector_map = {
        'title': '//h1[@class="h2"]/text()|//h1/text()',
        'description': '//div[@class="custom_text"]/p/text()',
        'date': '',
        'image': '//meta[@name="twitter:image"]/@content',
        'performers': '//a[contains(@href, "/models/")]/text()',
        'tags': '//div[@class="tags"]/a/text()',
        'external_id': r'/collections/(.+?)/?$',
        'trailer': '//meta[@name="twitter:player:stream"]/@content',
        'pagination': '/collections/page/%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class, "card")]//a[contains(@href, "/collections/")]/@href').getall()
        for scene in dict.fromkeys(scenes):
            if '/collections/page' in scene:
                continue
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def scene_meta(self, response):
        """The release date and runtime sit in the shopmaker meta line."""
        return [x.strip() for x in response.xpath('//span[contains(@class, "fa5-text")]/text()').getall() if x.strip()]

    def get_date(self, response):
        for entry in self.scene_meta(response):
            scenedate = re.match(r'^(\d{4}-\d{2}-\d{2})$', entry)
            if scenedate:
                return scenedate.group(1)
        return None

    def get_duration(self, response):
        for entry in self.scene_meta(response):
            runtime = re.match(r'^(\d{1,2}:\d{2}(?::\d{2})?)\s*minutes?$', entry)
            if runtime:
                return self.duration_to_seconds(runtime.group(1))
        return ''

    def get_title(self, response):
        title = super().get_title(response)
        title = title.replace("`", "'")
        return self.cleanup_title(title)

    def get_trailer(self, response):
        trailer = super().get_trailer(response)
        trailer = trailer.replace("mp4_720", "mp4_360")
        return trailer
