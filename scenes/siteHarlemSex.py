import re
import json
import html
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
true = True
false = False


class SiteHarlemSexSpider(BaseSceneScraper):
    name = 'HarlemSex'
    site = 'Harlem Sex'
    parent = 'Harlem Sex'
    network = 'Harlem Sex'

    start_urls = [
        'https://www.harlemsex.com'
    ]

    cookies = []

    selector_map = {
        'title': '//h1/text()',
        'description': '//h2/text()',
        'date': '//script[contains(text(), "datePublished")]/text()',
        're_date': r'datePublished.*?(\d{4}-\d{2}-\d{2})',
        'image': '//comment()[contains(., "TRAILER")]/following-sibling::div//img/@src',
        'performers': '',
        'tags': '//comment()[contains(., "TAGS")]/following-sibling::div//a/h3/text()',
        'trailer': '//comment()[contains(., "TRAILER")]/following-sibling::div//source/@src',
        'type': 'Scene',
        'external_id': r'.*/(\d+)-',
        'pagination': '/en/videos?page=%s',
    }

    def get_next_page_url(self, base, page):
        if int(page) == 1:
            return "https://www.harlemsex.com/en/videos?"
        page = str(int(page) - 1)
        return self.format_url(base, self.get_selector_map('pagination') % page)

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        # The gallery was rebuilt: div.video-gallery is gone and each card is now a
        # bare anchor to /en/videos/detail/<id>-<slug>, repeated several times per
        # card (thumbnail, title and preview all link to it), hence the dedupe.
        scenes = response.xpath('//a[contains(@href, "/videos/detail/")]/@href').getall()
        for scene in dict.fromkeys(scenes):
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_ld(self, response):
        """The scene page publishes a full schema.org VideoObject.

        It carries the title, description, still, release date and cast, all of
        which the rebuilt markup no longer exposes as addressable elements.
        """
        for block in response.xpath('//script[@type="application/ld+json"]/text()').getall():
            try:
                data = json.loads(block)
            except ValueError:
                continue
            for entry in (data if isinstance(data, list) else [data]):
                if isinstance(entry, dict) and 'VideoObject' in str(entry.get('@type')):
                    return entry
        return {}

    def get_title(self, response):
        title = self.get_ld(response).get('name')
        return self.cleanup_title(title) if title else super().get_title(response)

    def get_description(self, response):
        ld = self.get_ld(response)
        text = ld.get('text') or ld.get('description') or ''
        if not text:
            return super().get_description(response)
        # the long-form "text" field embeds escaped anchor markup
        text = re.sub(r'<[^>]+>', ' ', html.unescape(text))
        return self.cleanup_description(re.sub(r'\s+', ' ', text))

    def get_date(self, response):
        published = self.get_ld(response).get('datePublished') or self.get_ld(response).get('uploadDate')
        if published:
            published = re.search(r'(\d{4}-\d{2}-\d{2})', published)
            if published:
                return published.group(1)
        return None

    def get_image(self, response):
        image = self.get_ld(response).get('thumbnailUrl') or ''
        image = image.strip()
        if not image:
            return ''
        return self.format_link(response, image)

    def get_performers(self, response):
        actors = self.get_ld(response).get('actor') or []
        if isinstance(actors, dict):
            actors = [actors]
        return [a.get('name').strip() for a in actors
                if isinstance(a, dict) and a.get('name') and a['name'].strip()]

    def get_trailer(self, response):
        trailer = self.get_ld(response).get('contentUrl') or ''
        return trailer.strip()
