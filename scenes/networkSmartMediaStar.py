import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkSmartMediaStarJSONSpider(BaseSceneScraper):
    name = 'SmartMediaStarJSON'
    network = 'Smart Media Star'
    parent = 'Smart Media Star'

    start_urls = [
        'https://engine.realitylovers.com',
        'https://engine.tsvirtuallovers.com'
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/content/videos?max=12&page=%s&pornstar=&category=&perspective=&sort=NEWEST',
        'type': 'Scene',
    }

    def get_next_page_url(self, base, page):
        page = str(int(page) - 1)
        return self.format_url(base, self.get_selector_map('pagination') % page)

    def get_scenes(self, response):
        meta = response.meta
        jsondata = response.json()
        for scene in jsondata['contents']:
            sceneid = scene['id']
            if "tsvirtuallovers" in response.url:
                link = f"https://engine.tsvirtuallovers.com/content/videoDetail?contentId={sceneid}"
            elif "realitylovers" in response.url:
                link = f"https://engine.realitylovers.com/content/videoDetail?contentId={sceneid}"
            yield scrapy.Request(link, callback=self.parse_scene, meta=meta)

    def parse_scene(self, response):
        scene = response.json()
        item = self.init_scene()

        item['title'] = self.cleanup_title(scene['title'])
        if "vr porn video" in item['title'].lower():
            item['title'] = self.cleanup_title(item['title'].lower().replace("vr porn video", "").strip())

        item['description'] = self.cleanup_description(scene['description'])
        item['date'] = scene['releaseDate']

        if "mainImages" in scene and scene['mainImages']:
            image = scene['mainImages'][0]['imgSrcSet']
            image = re.search(r'.*?(http.*?)\s', image).group(1)

        if image:
            item['image'] = image
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
        else:
            item['image'] = ''
            item['image_blob'] = ''

        if "tsvirtuallovers" in response.url:
            item['url'] = f"https://tsvirtuallovers.com/{scene['canonicalUri']}"
            item['site'] = "TS Virtual Lovers"
        elif "realitylovers" in response.url:
            item['url'] = f"https://realitylovers.com/{scene['canonicalUri']}"
            item['site'] = "Reality Lovers"

        item['id'] = scene['contentId']
        item['trailer'] = scene['trailerUrl']
        item['network'] = self.network
        item['parent'] = self.parent

        item['performers'] = []
        if "starring" in scene and scene['starring']:
            for perf in scene['starring']:
                item['performers'].append(perf['name'])

        item['tags'] = []
        if "categories" in scene and scene['categories']:
            for tag in scene['categories']:
                item['tags'].append(tag['name'])

        yield self.check_item(item, self.days)
