import re
import string
import unidecode
import html
import json
import scrapy
from deep_translator import GoogleTranslator
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteIbicellaSpider(BaseSceneScraper):
    name = 'Ibicella'
    network = 'Ibicella'
    site = 'Ibicella'

    start_urls = [
        'https://ibicella.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/api/product?slug=ibicellastudio&page=%s&per_page=12',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = json.loads(response.text)
        scenes = scenes['data']
        for scene in scenes:
            meta['id'] = scene['id']
            meta['date'] = re.search(r'(\d{4}-\d{2}-\d{2})', scene['published']).group(1)
            meta['title'] = GoogleTranslator(source='fr', target='en').translate(unidecode.unidecode(self.cleanup_title(scene['title'])))
            meta['duration'] = scene['file_duration']
            meta['trailer'] = scene['file_preview_video']
            meta['image'] = scene['file_preview_image']
            meta['image_blob'] = self.get_image_blob_from_link(meta['image'])
            meta['description'] = GoogleTranslator(source='fr', target='en').translate(unidecode.unidecode(html.unescape(re.sub('<[^<]+?>', '', scene['description'])).replace("\n", " ").strip()))
            if meta['id']:
                # ~ link = f"https://ibicella.com/shop/{scene['perma_name']}"
                link = f"https://ibicella.com/api/product/{scene['perma_name']}?name=1"
                yield scrapy.Request(link, callback=self.parse_scene, meta=meta)

    def parse_scene(self, response):
        meta = response.meta
        scene = json.loads(response.text)
        item = SceneItem()
        item['title'] = meta['title']
        item['date'] = meta['date']
        item['id'] = meta['id']
        item['duration'] = meta['duration']
        item['image'] = meta['image']
        item['image_blob'] = meta['image_blob']
        item['description'] = meta['description']
        item['trailer'] = meta['trailer']
        item['performers'] = ['Icibella']
        taglist = []
        if "categories" in scene:
            for category in scene['categories']:
                taglist.append(category['title_en'])
        if "tags" in scene:
            for tag in scene['tags']:
                taglist.append(tag['title_en'])
        taglist = list(map(lambda x: GoogleTranslator(source='fr', target='en').translate(x), taglist))
        taglist = list(map(lambda x: string.capwords(x.strip(",").strip().lower()), taglist))
        item['tags'] = [i for n, i in enumerate(taglist) if i not in taglist[:n]]
        item['site'] = 'Ibicella'
        item['network'] = 'Ibicella'
        item['url'] = f"https://ibicella.com/shop/{scene['perma_name']}"

        yield self.check_item(item, self.days)
