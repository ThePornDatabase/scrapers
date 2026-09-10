import re

import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteWeAreHairySpider(BaseSceneScraper):
    name = 'WeAreHairy'
    network = 'We Are Hairy'
    parent = 'We Are Hairy'
    site = 'We Are Hairy'

    start_urls = [
        'https://www.wearehairy.com',
    ]

    # The site was rebuilt on the MMCore platform.  /categories/Movies/pageN.shtml
    # is a 404 now -- the listing is /categories/Movies?page=N -- and the scene
    # pages moved under /models/<model>/<slug>.
    selector_map = {
        'title': '',
        'description': '//span[contains(text(), "Description")]/parent::p/text()',
        'date': '',
        'image': '',
        'performers': '//h6//a[contains(@href, "/models/") and not(@href = "/models")]/@title',
        'tags': '//span[contains(text(), "Tags")]/following-sibling::a/text()',
        'trailer': '//video//source/@src',
        'external_id': r'/models/[^/]+/([^/?]+)',
        'pagination': '/categories/Movies?page=%s'
    }

    def get_scenes(self, response):
        # Title, date, duration and the still are only published on the card; the
        # scene page carries the synopsis, tags and trailer.
        for card in response.xpath('//div[contains(@class, "_results_posts_item")]'):
            link = card.xpath('.//h1/a/@href').get()
            if not link or not re.search(self.get_selector_map('external_id'), link):
                continue

            meta = dict(response.meta)
            meta['title'] = self.cleanup_title(card.xpath('.//h1/a/@title').get() or '')

            scenedate = card.xpath('.//small[2]/text()').get()
            if scenedate:
                meta['date'] = self.parse_date(scenedate.strip(), date_formats=['%b %d, %Y']).strftime('%Y-%m-%d')

            # a few cards ship without the poster attribute; the lazy-loaded
            # thumbnail carries the same file
            image = (card.xpath('.//a/@data-media-poster').get()
                     or card.xpath('.//img[contains(@class, "_image")]/@src').get())
            if image and not image.endswith('no_video_cover.png'):
                meta['image'] = self.format_link(response, image)

            duration = card.xpath('.//small[1]//text()').get()
            if duration:
                duration = re.search(r'(\d+):(\d{2})', duration)
                if duration:
                    meta['duration'] = str(int(duration.group(1)) * 60 + int(duration.group(2)))

            yield scrapy.Request(url=self.format_link(response, link), callback=self.parse_scene,
                                 meta=meta, headers=self.headers, cookies=self.cookies)

    def get_image(self, response):
        """Nothing on the scene page carries the still, so without a card poster
        there is no image -- the base fallback would hand back the site root."""
        return response.meta.get('image', '')
