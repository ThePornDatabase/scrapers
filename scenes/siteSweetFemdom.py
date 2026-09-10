import json
import re
import string

import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteSweetFemdomSpider(BaseSceneScraper):
    name = 'SweetFemdom'
    network = 'SweetFemdom'
    parent = 'SweetFemdom'
    site = 'SweetFemdom'

    start_urls = [
        'https://sweetfemdom.com',
    ]

    # The site was rebuilt: /tour/categories/movies/N/latest/ serves the same page
    # whatever N is, and div.item-video, div.videoDetails and li.update_models are
    # all gone.  The listing is /videos?page=N with a.card cards, and each scene
    # page carries a schema.org VideoObject in an @graph block holding the title,
    # synopsis, still, release date and runtime.  Cast is /models/ links and tags
    # are /niche/ links.
    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '//a[contains(@href, "/models/") and string-length(@href) > 8]//text()',
        'tags': '//a[contains(@href, "/niche/")]//text()',
        'trailer': '',
        'external_id': r'/videos/([^/?]+)',
        'pagination': '/videos?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        for card in response.xpath('//a[contains(@class, "card")][.//div[contains(@class, "card-info")]]'):
            link = card.attrib.get('href') or ''
            if not re.search(self.get_selector_map('external_id'), link):
                continue

            meta = dict(response.meta)
            # the card is the only place the preview clip is published
            preview = card.xpath('.//video/@data-src').get()
            if preview:
                meta['trailer'] = preview.strip()

            yield scrapy.Request(url=self.format_link(response, link), callback=self.parse_scene,
                                 meta=meta, headers=self.headers, cookies=self.cookies)

    def get_ld(self, response):
        for block in response.xpath('//script[@type="application/ld+json"]/text()').getall():
            try:
                data = json.loads(block)
            except ValueError:
                continue
            entries = data.get('@graph') if isinstance(data, dict) and '@graph' in data else data
            for entry in (entries if isinstance(entries, list) else [entries]):
                if isinstance(entry, dict) and 'VideoObject' in str(entry.get('@type')):
                    return entry
        return {}

    def get_title(self, response):
        title = self.get_ld(response).get('name') or ''
        if not title:
            title = response.xpath('//meta[@property="og:title"]/@content').get() or ''
            title = re.sub(r'\s*\|\s*Femdom Porn by SweetFemdom\s*$', '', title)
        return self.cleanup_title(title) if title.strip() else ''

    def get_description(self, response):
        return self.cleanup_description(self.get_ld(response).get('description') or '')

    def get_date(self, response):
        published = re.search(r'(\d{4}-\d{2}-\d{2})', self.get_ld(response).get('uploadDate') or '')
        return published.group(1) if published else None

    def get_image(self, response):
        image = (self.get_ld(response).get('thumbnailUrl')
                 or response.xpath('//meta[@property="og:image"]/@content').get() or '')
        image = image.strip()
        return self.format_link(response, image) if image else ''

    def get_duration(self, response):
        runtime = re.search(r'PT(\d+)S', self.get_ld(response).get('duration') or '')
        return str(int(runtime.group(1))) if runtime else None

    def get_trailer(self, response):
        return response.meta.get('trailer', '')

    def get_tags(self, response):
        return [string.capwords(x.strip()) for x in
                response.xpath(self.get_selector_map('tags')).getall() if x.strip()]
