import re
import chompjs
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteCumCountdownSpider(BaseSceneScraper):
    name = 'CumCountdown'
    network = 'Cum Countdown'
    parent = 'Cum Countdown'
    site = 'Cum Countdown'

    start_urls = [
        'https://www.cumcountdown.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/main.html?%s',
        'type': 'Scene',
    }

    def start_requests(self):
        meta = {}
        meta['page'] = self.page
        for link in self.start_urls:
            meta['link'] = link
            link = f"{link}/js/clips.js"
            print(link)
            yield scrapy.Request(link, callback=self.get_scenes, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        meta = response.meta
        clipslist = response.text
        clipslist = re.findall(r'(ClipDatabase.*?\]);', clipslist)
        for clip in clipslist:
            item = SceneItem()
            sceneid = re.search(r'Database\[(\d+)\]', clip).group(1)
            clip = re.search(r'=\s+?(\[.*?\])', clip).group(1)
            clip = chompjs.parse_js_object(clip)

            if clip[2]:
                if clip[1]:
                    item['title'] = clip[1]
                else:
                    item['title'] = f"#{sceneid}"
                item['description'] = clip[4]
                item['date'] = self.parse_date(clip[2], date_formats=['%m/%d/%y']).strftime('%Y-%m-%d')
                item['performers'] = []
                item['tags'] = []
                item['image'] = f"{meta['link']}/images/gallery/{clip[0]}/Pics/{clip[0]}1.jpg"
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
                item['url'] = f"{meta['link']}/main.html"
                item['site'] = re.search(r'//(.*?)\.com', meta['link'].replace("www.", "")).group(1)
                item['parent'] = re.search(r'//(.*?)\.com', meta['link'].replace("www.", "")).group(1)
                item['network'] = 'Reality Studio'
                item['trailer'] = ''
                item['id'] = sceneid
                item['type'] = 'Scene'
                yield self.check_item(item, self.days)
