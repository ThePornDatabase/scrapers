import html
import json
import re

import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteRiggsFilmsSpider(BaseSceneScraper):
    name = 'RiggsFilms'
    network = 'Riggs Films'
    parent = 'Riggs Films'
    site = 'Riggs Films'

    start_urls = [
        'https://riggsfilms.com',
    ]

    # The site was rebuilt on a WordPress block theme.  /scenes/page/N/ still
    # answers 200 but renders its cards client-side -- the only rw-card--scene text
    # left in the HTML is inside <style> blocks -- and the scene pages lost the
    # "Starring"/"Duration" lines and the ya:ovs meta tags the old selectors used.
    # Scenes are ordinary WordPress posts in the "Videos" category (id 7), so the
    # listing comes from the REST API, which carries the title, synopsis, release
    # date, still and both taxonomies in one request.  No runtime is published
    # anywhere on the rebuilt site.
    VIDEOS_CATEGORY = 7

    # Categories double as the cast list, so the site's own non-performer
    # categories are filtered out.  "Primal Instincts" is a series, not a person.
    NON_PERFORMER_CATEGORIES = {
        'videos', 'models', 'photosets', 'portfolio', 'blog',
        'uncategorised', 'uncategorized', 'primal instincts',
    }

    selector_map = {
        'external_id': r'riggsfilms\.com/([^/?]+)',
        'pagination': '/wp-json/wp/v2/posts?categories=%d&per_page=20&_embed=1&page=%%s' % VIDEOS_CATEGORY,
        'type': 'Scene',
    }

    def get_scenes(self, response):
        try:
            posts = json.loads(response.text)
        except ValueError:
            return
        if not isinstance(posts, list):
            return

        for post in posts:
            link = (post.get('link') or '').strip()
            if not link:
                continue

            meta = dict(response.meta)
            meta['title'] = self.cleanup_title(
                html.unescape((post.get('title') or {}).get('rendered') or ''))
            meta['id'] = str(post.get('id') or '')

            scenedate = re.search(r'(\d{4}-\d{2}-\d{2})', post.get('date') or '')
            if scenedate:
                meta['date'] = scenedate.group(1)

            excerpt = (post.get('excerpt') or {}).get('rendered') or ''
            meta['description'] = self.cleanup_description(
                re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', html.unescape(excerpt))))

            embedded = post.get('_embedded') or {}
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
                    if term.get('taxonomy') == 'category':
                        if name.lower() not in self.NON_PERFORMER_CATEGORIES:
                            performers.append(name)
                    elif term.get('taxonomy') == 'post_tag':
                        tags.append(name)
            meta['performers'] = list(dict.fromkeys(performers))
            meta['tags'] = list(dict.fromkeys(tags))

            yield scrapy.Request(url=link, callback=self.parse_scene, meta=meta,
                                 headers=self.headers, cookies=self.cookies)

    def get_image(self, response):
        return response.meta.get('image', '')

    def get_duration(self, response):
        return None
