import re
import string
import base64
from requests import get
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteDirtyWrestlingPitSpider(BaseSceneScraper):
    name = 'DirtyWrestlingPit'
    site = 'Dirty Wrestling Pit'
    parent = 'Dirty Wrestling Pit'
    network = 'Sexy Fighting Zone'

    start_url = "https://www.dirtywrestlingpit.com/all-videos.php"

    def get_next_page_url(self, base, page):
        return self.format_url(base, self.get_selector_map('pagination') % page)

    def start_requests(self):
        ip = get('https://api.ipify.org').content.decode('utf8')
        print('My public IP address is: {}'.format(ip))

        meta = {}
        meta['page'] = self.page

        formdata = {}
        formdata['page'] = str(meta['page'])
        yield scrapy.FormRequest(self.start_url, formdata=formdata, callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def parse(self, response, **kwargs):
        scenes = self.get_scenes(response)
        count = 0
        for scene in scenes:
            count += 1
            yield scene

        if count:
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                meta = response.meta
                meta['page'] = meta['page'] + 1
                print('NEXT PAGE: ' + str(meta['page']))
                formdata = {}
                formdata['page'] = str(meta['page'])
                yield scrapy.FormRequest(self.start_url, formdata=formdata, callback=self.parse, meta=meta)

    selector_map = {
        'title': '//div[@class="page-title"]/h1/text()',
        'image': '//div[contains(@class, "videocontent")]//video/@poster',
        'type': 'Scene',
        'external_id': r'',
        'pagination': '',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//p/a/@onclick').getall()
        for scene in scenes:
            sceneid = re.search(r'\((\d+)\)', scene).group(1)
            meta['id'] = sceneid
            scenetext = f"videoID={sceneid}"
            scenetext = base64.b64encode(bytes(scenetext, 'utf-8'))
            scenetext = scenetext.decode('utf-8')
            scene = f"https://www.dirtywrestlingpit.com/previewVideo.php?{scenetext}=_vid"
            if meta['id']:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        tags = []

        categories = response.xpath('//span[contains(text(), "Categories:")]/following-sibling::text()')
        if categories:
            categories = categories.get()
            categories = categories.replace("&nbsp;", "").strip()
            categories = categories.split(",")
            for category in categories:
                tags.append(string.capwords(category.strip()))

        taglist = response.xpath('//span[contains(text(), "Tags:")]/following-sibling::text()')
        if taglist:
            taglist = taglist.get()
            taglist = taglist.replace("&nbsp;", "").strip()
            taglist = taglist.split(",")
            for tag in taglist:
                tags.append(string.capwords(tag.strip()))

        return tags
