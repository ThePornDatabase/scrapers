import json

import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SitePowershotzSpider(BaseSceneScraper):
    name = 'Powershotz'
    site = 'Powershotz'
    parent = 'Powershotz'
    network = 'Powershotz'

    # The site was rebuilt from Next.js onto a Vite SPA, so /_next/data/<buildId>
    # is gone and there is no buildId on the page to find.  The catalogue now
    # comes from a streamed NDJSON endpoint, and the cast is a second lookup per
    # clip.  Both are refused without the browser CORS headers below.
    #
    # The feed carries no release date in any form, so dates are left empty for
    # TPDB to fall back on the import date.  It is returned in title order rather
    # than newest-first, so a full pass needs -a limit_pages=all.
    start_urls = [
        'https://powershotz.com',
    ]

    catalogue_url = 'https://data.powershotz.com/php/stream/gvop.php'
    cast_url = 'https://data.powershotz.com/php/gsd_p.php'
    image_url = 'https://powershotz.com/imageProcessor.php?path=/c4sImages/%s'
    per_page = 60

    api_headers = {
        'Origin': 'https://powershotz.com',
        'Referer': 'https://powershotz.com/',
        'Content-Type': 'application/json',
        'Accept': '*/*',
        'Sec-Fetch-Site': 'same-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
    }

    selector_map = {
        'external_id': r'',
        'pagination': '',
        'type': 'Scene',
    }

    async def start(self):
        yield scrapy.Request(url=self.catalogue_url, method='POST', body=json.dumps({"st": "clip"}),
                             headers={**self.headers, **self.api_headers}, callback=self.parse,
                             meta={'page': self.page}, dont_filter=True)

    def parse(self, response, **kwargs):
        clips = []
        for line in response.text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                clips.append(json.loads(line))
            except ValueError:
                continue

        if not clips:
            print("*** Powershotz returned no clips")
            return

        start = (int(response.meta['page']) - 1) * self.per_page
        end = start + (self.per_page * self.limit_pages)
        for clip in clips[start:end]:
            if not clip.get('id') or not clip.get('title'):
                continue
            yield scrapy.Request(url=self.cast_url, method='POST',
                                 body=json.dumps({"i": clip['id'], "p": "clip"}),
                                 headers={**self.headers, **self.api_headers},
                                 callback=self.parse_scene, meta={'clip': clip},
                                 dont_filter=True)

    def parse_scene(self, response):
        clip = response.meta['clip']
        item = SceneItem()

        item['title'] = self.cleanup_title(clip['title'])
        item['description'] = self.cleanup_description(clip.get('description') or '')
        item['id'] = str(clip['id'])
        item['url'] = "https://powershotz.com/%s" % (clip.get('pz_code') or clip['id'])
        item['date'] = ""

        item['image'] = (self.image_url % clip['image']) if clip.get('image') else ''
        item['image_blob'] = self.get_image_blob_from_link(item['image']) if item['image'] else ''

        try:
            cast = response.json()
        except ValueError:
            cast = []
        item['performers'] = [model['model_name'].strip() for model in cast
                              if isinstance(model, dict) and (model.get('model_name') or '').strip()]

        item['tags'] = self.get_tags(clip)

        item['duration'] = None
        if str(clip.get('length') or '').isdigit():
            item['duration'] = str(int(clip['length']) * 60)

        item['trailer'] = ""
        item['site'] = self.site
        item['parent'] = self.parent
        item['network'] = self.network
        item['type'] = "Scene"

        yield self.check_item(item, self.days)

    def get_tags(self, clip):
        # The feed's tag string mixes real categories with the clip title and the
        # cast's names, so only the leading all-caps categories are kept.
        tags = ['Bondage', 'BDSM', 'Roleplay']
        for tag in (clip.get('tags') or '').split(","):
            tag = tag.strip()
            if tag and tag.isupper() and tag.title() not in tags:
                tags.append(tag.title())
        return tags
