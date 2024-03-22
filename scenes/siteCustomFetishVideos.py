import re
import unidecode
import html
import json
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteCustomFetishVideosSpider(BaseSceneScraper):
    name = 'CustomFetishVideos'
    site = 'Custom Fetish Videos'
    parent = 'Anatomik Media'
    network = 'Gamma Enterprises'

    start_urls = [
        'https://customfetishvideos.com',
    ]

    selector_map = {
        'date': '//script[contains(text(), "datePublished")]/text()',
        're_date': r'datePublished.*?(\d{4}-\d{2}-\d{2})',
        'performers': '//span[contains(text(), "Models:")]/a/text()|//span[contains(text(), "Model:")]/a/text()',
        'tags': '//span[contains(text(), "Fetish:")]/a/text()',
        'trailer': '//div[contains(@class, "video_slide")]/video/source/@src',
        'external_id': r'',
        'pagination': '',
        'type': 'Scene',
    }

    def get_next_page_url(self, base, page):
        link = f"https://customfetishvideos.com/wp-json/wc/store/v1/products?orderby=date&order=desc&catalog_visibility=catalog&per_page=18&page={page}&_locale=user"
        return link

    def get_scenes(self, response):
        meta = response.meta
        jsondata = json.loads(response.text)

        for scene in jsondata:
            meta['id'] = scene['id']
            meta['title'] = scene['name']
            if "description" in scene:
                meta['description'] = unidecode.unidecode(html.unescape(re.sub(r'<[^<]+?>', '', scene['description'])))
            else:
                meta['description'] = unidecode.unidecode(html.unescape(re.sub(r'<[^<]+?>', '', scene['short_description'])))
            meta['image'] = scene['images'][0]['src']
            meta['image_blob'] = self.get_image_blob_from_link(meta['image'])
            link = scene['permalink']
            yield scrapy.Request(link, callback=self.parse_scene, meta=meta)
