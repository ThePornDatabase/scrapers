import re
import requests
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
true = True
false = False


class SiteLustCinemaSpider(BaseSceneScraper):
    name = 'LustCinema'
    network = 'LustCinema'
    parent = 'LustCinema'
    site = 'LustCinema'

    start_urls = [
        'https://next-prod-api.lustcinema.com',
    ]

    cookies = [{"name": "age_restriction", "value": true}]

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
        'pagination': '/api/series?page=%s&sortBy=default&direction=desc',
        'type': 'Scene',
    }

    def start_requests(self):
        link = "https://lustcinema.com/series"
        yield scrapy.Request(link, callback=self.start_requests_2, headers=self.headers, cookies=self.cookies)

    def start_requests_2(self, response):
        meta = {}
        responsetext = response.text
        responsetext = responsetext.replace("\n", "").replace("\r", "").replace("\t", "").strip()
        token = re.search(r'Bearer.*?access_token=[\'\"](.*?)[\'\"]', responsetext)
        if token:
            meta['token'] = token.group(1)

            ip = requests.get('https://api.ipify.org').content.decode('utf8')
            print('My public IP address is: {}'.format(ip))

            meta['page'] = self.page

            for link in self.start_urls:
                meta['headers'] = {"Authorization": f"Bearer {meta['token']}"}
                yield scrapy.Request(url=self.get_next_page_url(link, self.page), callback=self.parse, meta=meta, headers=meta['headers'], cookies=self.cookies)
        else:
            print("No token found.  Aborting")

    def parse(self, response, **kwargs):
        scenes = self.get_series(response)
        count = 0
        for scene in scenes:
            count += 1
            yield scene

        if count:
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                meta = response.meta
                meta['page'] = meta['page'] + 1
                print('NEXT PAGE: ' + str(meta['page']))
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page']), callback=self.parse, headers=meta['headers'], meta=meta)

    def get_series(self, response):
        meta = response.meta
        seriesjson = response.json()
        seriesjson = seriesjson['data']
        for series in seriesjson:
            meta['series'] = series['title']
            meta['slug'] = series['slug']
            if 'poster_picture' in series and series['poster_picture']:
                meta['series_cover'] = series['poster_picture']
                if meta['series_cover'] and "?" in meta['series_cover']:
                    meta['series_cover'] = re.search(r'(.*?)\?', meta['series_cover']).group(1)
                meta['series_cover_blob'] = self.get_image_blob_from_link(meta['series_cover'])
            seriesurl = f"https://next-prod-api.lustcinema.com/api/series/slug/{meta['slug']}"
            yield scrapy.Request(seriesurl, callback=self.get_scenes, headers=meta['headers'], meta=meta)

    def get_scenes(self, response):
        meta = response.meta
        scenejson = response.json()
        scenejson = scenejson['data']
        for scene in scenejson['episodes']:
            item = self.init_scene()
            item['id'] = scene['movie']['id']
            item['title'] = scene['movie']['title']
            if "title" in scenejson and scenejson['title']:
                titletext = f"{scenejson['title']}:   "
            else:
                titletext = ""
            item['description'] = f"{titletext}Season: {scene['season']}  Episode: {scene['episode']}\n" + re.sub(r'<[^<]+?>', '', self.cleanup_description(scenejson['synopsis']))
            item['date'] = re.search(r'(\d{4}-\d{2}-\d{2})', scene['created_at']).group(1)
            item['duration'] = self.duration_to_seconds(scene['movie']['length'])
            item['image'] = scene['movie']['cover_title_picture']
            if item['image'] and "?" in item['image']:
                item['image'] = re.search(r'(.*?)\?', item['image']).group(1)
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            if meta['series_cover']:
                item['back'] = meta['series_cover']
                item['back_blob'] = meta['series_cover_blob']
            item['tags'] = []
            for tag in scene['movie']['tags']:
                item['tags'].append(tag['title'])

            item['url'] = f"https://lustcinema.com/movies/{scene['movie']['slug']}"
            if "director" in scene['movie'] and scene['movie']['director']:
                director = scene['movie']['director']['name'] + " " + scene['movie']['director']['last_name']
                item['director'] = director.replace("Director", "").strip()

            item['site'] = "Lust Cinema"
            item['parent'] = "Lust Cinema"
            item['network'] = "Lust Cinema"

            yield self.check_item(item, self.days)

    def get_image_from_link(self, image):
        if image:
            # ~ header_list = response.request.headers.to_unicode_dict()
            # ~ headers = {'Authorization': header_list['Authorization']}
            req = requests.get(image, verify=False)

            # ~ req = Http.get(image, headers=response.headers, cookies=self.cookies, verify=False)
            if req and req.ok:
                return req.content
        return None
