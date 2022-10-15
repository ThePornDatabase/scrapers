import re
import html
import json
import requests
import unidecode
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteSugarbabesTVSpider(BaseSceneScraper):
    name = 'SugarbabesTV'
    network = "Sugarbabes TV"
    parent = "Sugarbabes TV"
    site = "Sugarbabes TV"

    custom_settings = {'CONCURRENT_REQUESTS': '1',
                       'AUTOTHROTTLE_ENABLED': 'True',
                       'AUTOTHROTTLE_DEBUG': 'False',
                       'DOWNLOAD_DELAY': '2',
                       'CONCURRENT_REQUESTS_PER_DOMAIN': '1',
                       }

    start_urls = [
        'https://sugarbabes.tv',
    ]

    headers = {
        'age_gate': '18',
        'wpml_browser_redirect_test': '0',
    }

    selector_map = {
        'performers': '//h2[@class="h4 title-cat"]/following-sibling::div[contains(@class,"post-metadata")]//div[@class="channel-content"]/h4/a/text()',
        'external_id': r'',
        'pagination': '/index.php/wp-json/wp/v2/posts?page=%s&per_page=10&lang=en'
    }

    def get_scenes(self, response):
        reqheaders = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}
        meta = response.meta
        jsondata = json.loads(response.text)
        for scene in jsondata:
            meta['id'] = scene['id']
            scenelink = scene['link']
            meta['date'] = scene['date']
            meta['title'] = unidecode.unidecode(html.unescape(re.sub('<[^<]+?>', '', scene['title']['rendered'])).replace("\n", " ").strip())
            if "og_image" in scene['yoast_head_json']:
                meta['image'] = scene['yoast_head_json']['og_image'][0]['url']
            meta['description'] = scene['content']['rendered']
            if meta['description']:
                meta['description'] = unidecode.unidecode(html.unescape(re.sub('<[^<]+?>', '', meta['description'])).replace("\n", " ").strip())
                if 'vc_raw_html' in meta['description']:
                    meta['description'] = ''
            tags = []
            link = f"https://sugarbabes.tv/wp-json/wp/v2/categories?post={meta['id']}&lang=en"
            req = requests.get(link, headers=reqheaders, timeout=10)
            if req and len(req.text) > 5:
                taglist = []
                taglist = json.loads(req.text)
                for tag in taglist:
                    tags.append(tag['name'])
            if "European" not in tags:
                tags.append("European")
            meta['tags'] = tags
            meta['trailer'] = ''
            if "lang=en" not in scenelink:
                scenelink = scenelink + "?lang=en"
            processpointer = True
            for tag in tags:
                if "DVD" in tag:
                    processpointer = False
            if processpointer:
                yield scrapy.Request(scenelink, callback=self.parse_scene, meta=meta)
