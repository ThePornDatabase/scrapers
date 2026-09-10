import re
import html
import string
import json
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteBangSpider(BaseSceneScraper):
    name = 'Bang'
    network = 'Bang'
    parent = 'Bang'

    start_urls = [
        'https://www.bang.com',
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '//div[contains(@class, "items-center")]//a[contains(@class, "genres")]/text()|//div[contains(@class, "actions")]/a[contains(@href, "with")]/text()',
        'duration': '',
        'trailer': '',
        'external_id': r'video/(.*?)/',
        'pagination': '',
        'type': 'Scene',
    }

    def get_next_page_url(self, base, page):
        pagination = f"https://www.bang.com/videos?by=date.desc&from=bang%21%20originals&page={page}"
        return pagination

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        scenes = response.xpath('//div[contains(@class,"video_container")]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def parse_scene(self, response):
        item = SceneItem()
        jsondata = response.xpath('//script[contains(@type, "json") and contains(text(), "duration")]/text()')
        if jsondata:
            jsondata = json.loads(jsondata.get(), strict=False)

            title = response.xpath('//meta[@property="og:title"]/@content')
            if title:
                item['title'] = string.capwords(html.unescape(self.cleanup_title(title.get())).replace("&", "and").strip())
            else:
                item['title'] = string.capwords(html.unescape(self.cleanup_title(jsondata['name'])).replace("&", "and").strip())

            published = re.search(r'(\d{4}-\d{2}-\d{2})',
                                  jsondata.get('datePublished') or jsondata.get('uploadDate') or '')
            item['date'] = published.group(1) if published else None
            
            description = response.xpath('//p[contains(@class, "text-card-foreground")]//text()')
            if description:
                description = description.getall()
                description = " ".join(description)
                item['description'] = self.cleanup_description(description.strip())
            else:
                if 'description' in jsondata:
                    item['description'] = html.unescape(jsondata['description'])
                else:
                    item['description'] = ''

            item['image'] = (jsondata.get('thumbnailUrl') or '').strip()
            if "?p=" in item['image']:
                item['image'] = re.search(r'(.*)\?p=', item['image']).group(1)
            item['image_blob'] = self.get_image_blob_from_link(item['image']) if item['image'] else None

            # Older scenes publish @id under /trailer-long/ rather than /video/, which
            # made the original match return None and abort the item; the response URL
            # is the reliable source either way.
            sceneid = re.search(self.get_selector_map('external_id'), response.url)
            if not sceneid:
                sceneid = re.search(r'/(?:video|trailer-long)/(.*?)/', jsondata.get('@id') or '')
            if not sceneid:
                return
            item['id'] = sceneid.group(1)
            item['type'] = 'Scene'
            item['url'] = response.url
            item['duration'] = self.duration_to_seconds(jsondata['duration'])
            # a few scenes ship no actor list at all
            item['performers'] = [person['name'] for person in (jsondata.get('actor') or [])
                                  if isinstance(person, dict) and person.get('name')]

            item['tags'] = self.get_tags(response)
            site = response.xpath('//p[contains(text(), "In the series")]/a/text()')
            if not site:
                site = response.xpath('//p[contains(text(), "Studio:")]/a/text()')
            site = (site.get() or '').strip()
            if not site:
                # neither line is present on some scenes; the JSON-LD studio is the
                # same value the "Studio:" line would have shown
                site = ((jsondata.get('productionCompany') or {}).get('name') or 'bang! originals')
            item['site'] = re.sub('[^a-zA-Z0-9-]', '', site)
            trailer = response.xpath('//video[@data-modal-target="videoImage"]/source[contains(@type, "mp4")]/@src')
            if not trailer:
                trailer = response.xpath('//video[@data-modal-target="videoImage"]/source[contains(@type, "webm")]/@src')
            if trailer:
                item['trailer'] = trailer.get()
            else:
                item['trailer'] = ''
            item['network'] = 'Bang'
            item['parent'] = 'Bang'

            # There was a hardcoded item['date'] > "2026-02-12" floor here, which
            # silently discarded every older scene and made backfilling impossible.
            # The -a days= window is the only date filter that should apply.
            item = self.check_item(item, self.days)
            if item:
                yield item
