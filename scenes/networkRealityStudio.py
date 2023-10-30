import re
import chompjs
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class NetworkRealityStudioSpider(BaseSceneScraper):
    name = 'RealityStudio'
    network = 'Reality Studio'

    start_urls = [
        'https://www.femaleworship.com',
        'https://www.goddesskitra.com',
        'https://menareslaves.com',
        'https://www.subbygirls.com',
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
        clipslist = clipslist.replace('\n', '').replace('\r', '')
        clipslist = re.search(r'ClipDatabase\s+?=\s+?(\[.*\])', clipslist).group(1)
        clipslist = chompjs.parse_js_object(clipslist)
        counter = 0
        for clip in clipslist:
            item = SceneItem()
            if clip[2]:
                if clip[1]:
                    item['title'] = f"#{str(counter)} - {clip[1]}"
                else:
                    item['title'] = f"#{str(counter)}"
                item['description'] = ''
                item['date'] = self.parse_date(clip[2], date_formats=['%m/%d/%y']).strftime('%Y-%m-%d')
                item['performers'] = list(map(lambda x: x.strip(), clip[4].split(",")))
                item['tags'] = list(map(lambda x: x.strip(), clip[5].split(",")))
                item['image'] = f"{meta['link']}/images/gallery/{clip[0]}/Pics/{clip[0]}1.jpg"
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
                item['url'] = f"{meta['link']}/main.html"
                item['site'] = re.search(r'//(.*?)\.com', meta['link'].replace("www.", "")).group(1)
                item['parent'] = re.search(r'//(.*?)\.com', meta['link'].replace("www.", "")).group(1)
                item['network'] = 'Reality Studio'
                item['trailer'] = ''
                item['id'] = str(counter)
                item['type'] = 'Scene'
                yield self.check_item(item, self.days)
            counter = counter + 1
