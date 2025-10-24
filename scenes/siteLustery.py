from datetime import datetime
import scrapy
import string
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteLusterySpider(BaseSceneScraper):
    name = 'Lustery'

    start_urls = ['https://lustery.com']

    selector_map = {
        'external_id': r'',
        'pagination': 'https://lustery.com/api/videos?offset=%s&sort=latest',
    }

    def get_next_page_url(self, base, page):
        page = str((int(page) - 1) * 18)
        return self.format_url(base, self.get_selector_map('pagination') % page)

    def get_scenes(self, response):
        meta = response.meta
        jsondata = response.json()
        permalinks = jsondata['currentPagePermalinks']
        for permalink in permalinks:
            meta['id'] = permalink
            link = f"https://lustery.com/api/videos/get-by-permalinks?permalinks%5B%5D={permalink}"
            yield scrapy.Request(link, callback=self.parse_scene, meta=meta)

    def parse_scene(self, response):
        meta = response.meta
        jsondata = response.json()
        if "videos" in jsondata and jsondata['videos']:
            scene = jsondata['videos'][0]
            resources = jsondata['resources']
            item = self.init_scene()

            item['title'] = self.cleanup_title(scene['title'])

            if "poster" in scene and scene['poster']:
                # ~ item['image'] = f"https://static.lustery.com/cdn-cgi/image/format=auto/{scene['poster']['staticPath']}"
                item['image'] = f"https://img.lustery.com/cache/image/resize/width=1600/{scene['poster']['staticPath']}"
                item['image_blob'] = self.get_image_blob_from_link(item['image'])

            item['date'] = datetime.utcfromtimestamp(scene['publishAt']).strftime('%Y-%m-%d')

            item['id'] = meta['id']
            item['url'] = f"https://lustery.com/video-preview/{meta['id']}"
            item['site'] = 'Lustery'
            item['tags'] = scene['tags']
            item['duration'] = scene['duration']
            item['parent'] = 'Lustery'
            item['network'] = 'Lustery'

            for resource in resources:
                if "videoInfo" in resources[resource] and resources[resource]['videoInfo']:
                    item['description'] = resources[resource]['videoInfo']['description']

            if "coupleName" in scene and scene['coupleName']:
                if "&" in scene['coupleName']:
                    coupleName = scene['coupleName'].split("&")
                else:
                    coupleName = [scene['coupleName']]
                for model in coupleName:
                    item['performers'].append(string.capwords(model.strip()))

            yield self.check_item(item, self.days)
