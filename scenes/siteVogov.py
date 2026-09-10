import re

import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class VogovSpider(BaseSceneScraper):
    name = 'Vogov'
    network = 'Vogov'
    parent = 'Vogov'
    site = 'Vogov'

    start_urls = [
        'https://vogov.com'
    ]

    # The tour was rebuilt: /latest-videos/N/ is a 404, the listing is
    # /categories/movies_N_p.html, div.video-post cards became a.thumb-video and the
    # scene pages moved from /videos/<slug> to /trailers/<Slug>.html.
    selector_map = {
        'title': '//h1[contains(@class, "video-title")]/text()',
        'description': '//p[contains(@class, "video-description-text")]/text()',
        'performers': '//a[contains(@class, "video-actor-link")]/text()',
        'date': '//span[contains(@class, "video-info-date")]/text()',
        're_date': r'(\w+ \d{1,2}, \d{4})',
        'date_formats': ['%B %d, %Y'],
        'duration': '//span[contains(@class, "video-info-time")]/text()',
        'image': '//meta[@property="og:image"]/@content',
        'tags': '//a[contains(@class, "video-tag-link")]/text()',
        'external_id': r'/trailers/(.+?)\.html',
        'trailer': '',
        'pagination': '/categories/movies_%s_p.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//a[contains(@class, "thumb-video")]/@href').getall()
        for scene in dict.fromkeys(scenes):
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene,
                                     headers=self.headers, cookies=self.cookies)

    def get_duration(self, response):
        # the runtime sits after an inline svg, so the first text node is blank
        duration = ' '.join(response.xpath('//span[contains(@class, "video-info-time")]//text()').getall())
        if duration:
            duration = re.search(r'(\d+)\s*min', duration)
            if duration:
                return str(int(duration.group(1)) * 60)
        return None

    def get_trailer(self, response):
        """The old video_url script block is gone; the preview mp4 is served from
        the teenmegaworld CDN and only appears as a plain source element."""
        trailer = response.xpath('//video//source/@src|//video/@src').re_first(r'(https?://\S+?\.mp4)')
        return trailer.strip() if trailer else ''

    def get_tags(self, response):
        return [x.strip().title() for x in
                response.xpath(self.get_selector_map('tags')).getall() if x.strip()]
