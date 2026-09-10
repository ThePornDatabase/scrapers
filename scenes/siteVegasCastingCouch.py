import json
import re
import string

import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteVegasCastingCouchSpider(BaseSceneScraper):
    name = 'VegasCastingCouch'
    network = 'VegasCastingCouch'
    parent = 'VegasCastingCouch'
    site = 'VegasCastingCouch'

    # The site was rebuilt on Next.js and the API moved off the www host onto
    # api.vegascastingcouch.com, where /api/v1/videos and /api/v1/performers are
    # both 404s.  The listing endpoint is /user/assets/videos/search, and it now
    # embeds the cast in each record, so the separate performer lookup that the old
    # start() made is no longer needed.
    start_urls = [
        'https://api.vegascastingcouch.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/user/assets/videos/search?limit=16&offset=%s',
        'type': 'Scene',
    }

    def get_next_page_url(self, base, page):
        offset = str((int(page) - 1) * 16)
        return self.format_url(base, self.get_selector_map('pagination') % offset)

    def get_scenes(self, response):
        payload = json.loads(response.text)
        for scene in (payload.get('data') or {}).get('data') or []:
            item = SceneItem()

            item['id'] = scene['_id']
            item['title'] = self.cleanup_title(scene.get('title') or '')
            item['description'] = self.cleanup_description(scene.get('description') or '')

            scenedate = re.search(r'(\d{4}-\d{2}-\d{2})', scene.get('createdAt') or '')
            item['date'] = scenedate.group(1) if scenedate else None

            image = ((scene.get('thumbnail') or {}).get('url') or '').replace(" ", "%20")
            item['image'] = image
            item['image_blob'] = self.get_image_blob_from_link(image) if image else None

            item['trailer'] = ((scene.get('teaser') or {}).get('url') or '').replace(" ", "%20")

            duration = (scene.get('video') or {}).get('duration')
            item['duration'] = str(int(duration)) if duration else None

            # tags arrive as snake_case slugs
            item['tags'] = [string.capwords(x.replace('_', ' ').strip())
                            for x in (scene.get('tags') or []) if x and x.strip()]

            performers = []
            for performer in scene.get('performers') or []:
                name = (performer.get('name') or '').strip()
                if not name:
                    continue
                # a couple of records pack a duo into one name
                performers.extend([x.strip() for x in name.split('&')] if '&' in name else [name])
            item['performers'] = list(dict.fromkeys(performers))

            item['site'] = "Vegas Casting Couch"
            item['parent'] = "Vegas Casting Couch"
            item['network'] = "Vegas Casting Couch"
            item['type'] = 'Scene'
            item['url'] = f"https://www.vegascastingcouch.com/movies/{scene.get('slug') or ''}"

            item = self.check_item(item, self.days)
            if item:
                yield item
