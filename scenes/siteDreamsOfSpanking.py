import html
import json
import re

import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteDreamsOfSpankingSpider(BaseSceneScraper):
    name = 'DreamsOfSpanking'
    network = 'Dreams Of Spanking'
    parent = 'Dreams Of Spanking'
    site = 'Dreams Of Spanking'

    # The site was rebuilt on WordPress/Elementor: /scene/recent/N is a 404 and none
    # of the old div.recent_update / div#product markup survives.  Scenes are a
    # WordPress custom post type, so the listing comes from the REST API, which
    # hands over the title, release date, still and the whole taxonomy set in one
    # request.  Only the synopsis is missing from it -- the post body is empty and
    # the text lives in an Elementor widget -- so each scene page is still visited
    # for its og:description.
    start_urls = [
        'https://dreamsofspanking.com',
    ]

    selector_map = {
        'description': '//meta[@property="og:description"]/@content',
        'external_id': r'/scene/([^/?]+)',
        'pagination': '/wp-json/wp/v2/scene?per_page=20&_embed=1&page=%s',
        'type': 'Scene',
    }

    # the taxonomies that are scene tags rather than cast
    TAG_TAXONOMIES = ('genres', 'details', 'atmosphere', 'implements',
                      'orientation', 'media_type', 'stream_type')

    def get_scenes(self, response):
        try:
            scenes = json.loads(response.text)
        except ValueError:
            return
        if not isinstance(scenes, list):
            return

        for scene in scenes:
            link = (scene.get('link') or '').strip()
            if not link or not re.search(self.get_selector_map('external_id'), link):
                continue

            meta = dict(response.meta)
            meta['title'] = self.cleanup_title(
                html.unescape((scene.get('title') or {}).get('rendered') or ''))
            meta['id'] = str(scene.get('id') or '')

            scenedate = re.search(r'(\d{4}-\d{2}-\d{2})', scene.get('date') or '')
            if scenedate:
                meta['date'] = scenedate.group(1)

            embedded = scene.get('_embedded') or {}
            media = (embedded.get('wp:featuredmedia') or [{}])[0]
            image = (media.get('source_url') or '').strip()
            if image:
                meta['image'] = image

            performers, tags = [], []
            for group in embedded.get('wp:term') or []:
                for term in group:
                    name = (term.get('name') or '').strip()
                    if not name:
                        continue
                    if term.get('taxonomy') == 'performers-tag':
                        performers.append(name)
                    elif term.get('taxonomy') in self.TAG_TAXONOMIES:
                        tags.append(name.title())
            meta['performers'] = list(dict.fromkeys(performers))
            meta['tags'] = list(dict.fromkeys(tags))

            yield scrapy.Request(url=link, callback=self.parse_scene, meta=meta,
                                 headers=self.headers, cookies=self.cookies)

    def get_description(self, response):
        description = response.xpath(self.get_selector_map('description')).get() or ''
        return self.cleanup_description(html.unescape(description).strip())

    def get_image(self, response):
        return response.meta.get('image', '')
