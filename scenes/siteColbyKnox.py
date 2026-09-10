import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteColbyKnoxSpider(BaseSceneScraper):
    name = 'ColbyKnox'
    network = 'Colby Knox'
    parent = 'Colby Knox'
    site = 'Colby Knox'

    start_urls = [
        'https://www.colbyknox.com',
    ]

    # The site was rebuilt: the video-block-wrapper cards became Bootstrap columns
    # holding an a.card--video, the itemprop meta tags are gone, and the scene page
    # no longer links the cast at all.  The still and runtime only exist on the
    # listing card now, so get_scenes passes them through meta.
    selector_map = {
        'title': '//h1/text()',
        'description': '//h2[contains(text(), "Description")]/following-sibling::p/text()',
        'date': '',
        're_date': r'(\d{4}-\d{2}-\d{2})',
        'image': '',
        'performers': '',
        'tags': '//a[contains(@href, "/category/")]/text()',
        'duration': '',
        'trailer': '//video/@src|//video/source/@src',
        'external_id': r'.*/(.*?)$',
        'pagination': '/videos?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        for scene in response.xpath('//a[contains(@class, "card--video")]'):
            link = scene.xpath('./@href').get()
            if not link or not re.search(self.get_selector_map('external_id'), link):
                continue

            duration = scene.xpath('.//i[contains(@class, "icon-clock")]/following-sibling::span/text()').get()
            if duration and ':' in duration:
                meta['duration'] = self.duration_to_seconds(duration.strip())

            image = scene.xpath('.//img/@src').get()
            if image and image.strip():
                meta['image'] = self.format_link(response, image.strip())
                meta['image_blob'] = self.get_image_blob_from_link(meta['image'])

            yield scrapy.Request(url=self.format_link(response, link), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        """The category links are the only tagging left; keep the Gay marker the old
        scraper hard-coded, since the whole site is gay content."""
        tags = [x.strip() for x in response.xpath(self.get_selector_map('tags')).getall() if x and x.strip()]
        return ['Gay'] + [t for t in dict.fromkeys(tags) if t.lower() != 'gay']

    def get_date(self, response):
        """The still's filename carries the shoot date, e.g. .../20260903162726_..."""
        image = response.meta.get('image') or ''
        date = re.search(r'images/(\d{8})', image)
        if date:
            date = date.group(1)
            date = self.parse_date(date, date_formats=['%Y%m%d']).strftime('%Y-%m-%d')
            return date
        return None
