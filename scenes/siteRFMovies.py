import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteRFMoviesSpider(BaseSceneScraper):
    name = 'RFMovies'
    network = 'RF Movies'
    parent = 'RF Movies'
    site = 'RF Movies'

    start_urls = [
        'https://api.fundorado.com',
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'duration': '',
        'trailer': '',
        'external_id': r'',
        'pagination': '/api/videos/browse/labels/695?page=%s&sg=false&sort=release&video_type=scene&lang=en&site_id=7&ts=null&genre=0',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        jsondata = response.json()
        jsondata = jsondata['videos']['data']
        for scene in jsondata:
            if scene['preview']:
                if "url" in scene['preview']:
                    meta['trailer'] = scene['preview']['url']
            sceneid = scene['id']
            if sceneid:
                link = f"https://api.fundorado.com/api/videodetail/{sceneid}?s=7"
                yield scrapy.Request(link, callback=self.parse_scene, meta=meta)

    def parse_scene(self, response):
        meta = response.meta
        jsondata = response.json()
        jsondata = jsondata['video']
        if jsondata:
            item = self.init_scene()
            item['site'] = "RF Movies"
            item['parent'] = "RF Movies"
            item['network'] = "RF Movies"
            item['title'] = self.cleanup_title(jsondata['title']['en'])
            item['description'] = self.cleanup_text(jsondata['description']['en'])
            item['performers'] = []
            if jsondata['actors']:
                for actor in jsondata['actors']:
                    item['performers'].append(actor['name'])
            item['date'] = self.parse_date(jsondata['publication_date']).isoformat()
            item['id'] = jsondata['id']
            item['image'] = jsondata['artwork']['large']
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            if jsondata['genres']:
                for genre in jsondata['genres']:
                    if genre['title']['en']:
                        item['tags'].append(genre['title']['en'])
            if "trailer" in meta:
                item['trailer'] = meta['trailer']
            else:
                item['trailer'] = None
            item['url'] = f"https://rfmovies.com/video/{item['id']}/{jsondata['slug']}"
            if jsondata['meta']:
                if "duration" in jsondata['meta']:
                    item['duration'] = self.duration_to_seconds(jsondata['meta']['duration'])
            item['type'] = 'Scene'

            # ~ print(item)
            yield self.check_item(item, self.days)
