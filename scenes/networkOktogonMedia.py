import scrapy
import re
import requests
import json
from tpdb.BaseSceneScraper import BaseSceneScraper
true = True
false = False


def match_site(argument):
    match = {
        'loveherboobs': "Love Her Boobs",
        'loveherfeet': "Love Her Feet",
        'shelovesblack': "She Loves Black",
    }
    return match.get(argument, argument)


class OktogonMediaSpider(BaseSceneScraper):
    name = 'OktogonMedia'
    network = 'Oktogon Media'

    start_urls = [
        'https://www.shelovesblack.com',
        'https://www.loveherboobs.com',
        'https://www.loveherbutt.com',
        'https://www.loveherfeet.com',
        'https://www.loveherfilms.com',
    ]

    paginations = [
        '/tour/categories/interviews/%s/latest/',
        '/tour/categories/movies/%s/latest/',
    ]

    selector_map = {
        'title': '//h1[contains(@class, "title")]/text()',
        'description': '//h2[contains(text(), "Story")]/following-sibling::p[1]/text()',
        'performers': '//h2[contains(text(), "Featuring")]/following-sibling::ul[1]/li/a/p[contains(@class, "modelName")]/text()',
        'date': '//p[contains(@class, "dateText")]/text()',
        'date_formats': ['%m/%d/%Y', '%B %d, %Y'],
        'image': '//div[contains(@class, "HeroInteractive")]/a[contains(@aria-label, "Watch")]/@href',
        're_image': r'imgUrl=(http.*)',
        'tags': '//h2[contains(text(), "Tags")]/following-sibling::ul[1]/li/a/p/text()',
        'trailer': '',
        'external_id': r'trailers/(.*)\.html',
        'pagination': '/%s/latest/'
    }

    async def start(self):
        meta = {}
        singleurl = self.settings.get('url')
        if singleurl:
            meta['date'] = ""
            yield scrapy.Request(singleurl, callback=self.parse_scene, meta=meta, headers=self.headers, cookies=self.cookies)
        else:
            for url in self.start_urls:
                for pagination in self.paginations:
                    meta = {'page': self.page, 'pagination': pagination}
                    yield scrapy.Request(url=self.get_next_page_url(url, self.page, pagination), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def parse(self, response, **kwargs):
        meta = self.copy_meta(response)
        if response.status == 200:
            scenes = self.get_scenes(response)
            count = 0
            for scene in scenes:
                count += 1
                yield scene

        if 'page' in response.meta and response.meta['page'] < self.limit_pages:
            meta['page'] = meta['page'] + 1
            print('NEXT PAGE: ' + str(meta['page']))
            yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page'], meta['pagination']), callback=self.parse, meta=meta)

    def get_next_page_url(self, url, page, pagination):
        url = self.format_url(url, pagination % page)
        print(url)
        return url

    def get_scenes(self, response):
        scenes = response.xpath('//script[contains(text(), "mutations") and not(contains(text(), "upcomingContent"))]/text()')
        if scenes:
            scenes = scenes.get()
            scenes = re.search(r'(\{.*\})', scenes).group(1)
            scenes = scenes.replace('\\\"', '"')
            scenes = scenes.replace('\\\" ', '\\\"').replace(' \\\"', '\\\"')
            scenes = scenes.encode('utf-8').decode('unicode_escape')
            jsondata = json.loads(scenes)
        for scene in jsondata['state']['queries'][0]['state']['data']['items']:
            item = self.init_scene()

            if "slug" in scene and scene['slug']:
                item['id'] = scene['slug']

                item['title'] = self.cleanup_title(scene['title'])

                if "releaseDateVideo" in scene and scene['releaseDateVideo']:
                    scenedate = scene['releaseDateVideo']
                    scenedate = re.search(r'(\d{4}-\d{2}-\d{2})', scenedate)
                    if scenedate:
                        item['date'] = scenedate.group(1)

                if not item['date']:
                    if "trailer" in scene and scene['trailer']:
                        if "createdAt" in scene['trailer'] and scene['trailer']['createdAt']:
                            scenedate = scene['trailer']['createdAt']
                            scenedate = re.search(r'(\d{4}-\d{2}-\d{2})', scenedate)
                            if scenedate:
                                item['date'] = scenedate.group(1)

                if self.check_item(item, self.days):

                    scene_url = f"https://api.loveherboobs.com/v1/content-sets/{item['id']}?isPhoto=false"

                    if "loveherboobs" in response.url:
                        xsite = "677d3f422e587cf94d1a9e5b"
                    if "loveherbutt" in response.url:
                        xsite = "677d3f422e587cf94d1a9e5e"
                    if "shelovesblack" in response.url:
                        xsite = "677d3f422e587cf94d1a9e5c"
                    if "loveherfeet" in response.url:
                        xsite = "677d3f422e587cf94d1a9e5a"
                    if "loveherfilms" in response.url:
                        xsite = "677d3f422e587cf94d1a9e5d"
                    
                    process_scene = True
                    if "loveherfilms" in response.url:
                        if "trailer" in scene and scene['trailer']:
                            if "baseName" in scene['trailer'] and scene['trailer']['baseName']:
                                trailer_base = scene['trailer']['baseName']
                                trailer_prefix = re.search(r'^([a-z]+)_', trailer_base.lower())
                                if trailer_prefix:
                                    trailer_prefix = trailer_prefix.group(1)
                                    if trailer_prefix in ['slb', 'lhf', 'lhb']:
                                        process_scene = False
                                else:
                                    pass

                    if process_scene:
                        req_headers = {'x-site-id': xsite}
                        req = requests.get(scene_url, headers=req_headers)
                        if req and req.ok:
                            scene_secondary = req.content
                            if scene_secondary:
                                scene_secondary = json.loads(scene_secondary)
                                if "description" in scene_secondary and scene_secondary['description']:
                                    item['description'] = self.cleanup_description(scene_secondary['description'])

                        if "models" in scene and scene['models']:
                            for model in scene['models']:
                                item['performers'].append(model['modelName'])

                        if "categories" in scene and scene['categories']:
                            for tag in scene['categories']:
                                item['tags'].append(tag['title'])
                            if "behind-the-scenes" in item['id'].lower():
                                item['tags'].append("Behind The Scenes")
                                item['tags'].append("BTS")

                        if "trailer" in scene and scene['trailer']:
                            if "sources" in scene['trailer'] and len(scene['trailer']['sources']):
                                trailer = scene['trailer']['sources'][0]['path']
                                if trailer:
                                    item['trailer'] = trailer

                        if "thumb" in scene and scene['thumb']:
                            image = scene['thumb']['previewImage']
                            if image:
                                if "-1x" in image:
                                    image = image.replace("-1x", "-4x")
                                item['image'] = image
                                item['image_blob'] = self.get_image_blob_from_link(item['image'])

                        item['site'] = self.get_site(response)
                        item['parent'] = self.get_site(response)
                        item['network'] = self.get_site(response)

                        item['url'] = f"https://www.{item['site']}.com/tour/trailers/{item['id']}.html"

                        yield item
