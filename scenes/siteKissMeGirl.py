import re
import string
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteKissMeGirlSpider(BaseSceneScraper):
    name = 'KissMeGirl'
    site = 'Kiss Me Girl'
    parent = 'Kiss Me Girl'
    network = 'Kiss Me Girl'

    start_urls = [
        'https://www.kissmegirl.com',
    ]

    selector_map = {
        'title': './/td[contains(.//b, "SCENE")]/following-sibling::td[1]//font/text()',
        'description': './/td[contains(.//b, "Desc:")]//b/following-sibling::p/font/text()',
        'performers': './/b[contains(text(), "Stars:")]/following-sibling::text()',
        'duration': './div[contains(@class, "rtitle")]/h3[1]/strong/text()',
        'external_id': r'',
        'pagination': '/vodpage%s.html',
        'type': 'Scene',
    }

    def get_next_page_url(self, base, page):
        if int(page) == 1:
            return "https://www.kissmegirl.com/vod.html"
        else:
            return self.format_url(base, self.get_selector_map('pagination') % page)

    def get_scenes(self, response):
        scenes = response.xpath('//table[contains(.//b, "SCENE")]')
        for scene in scenes:
            item = self.init_scene()

            item['title'] = self.get_title(scene)
            if " - " in item['title']:
                item['title'] = re.search(r' - (.*)', item['title']).group(1)
            item['description'] = self.get_description(scene).replace("\n", " ").replace("\r", "").replace("\t", "")
            item['image'] = scene.xpath('.//img[contains(@src, "small")]/@src').get()
            if item['image']:
                item['image'] = "https://www.kissmegirl.com/" + item['image']
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['performers'] = self.get_performers(scene)
            item['performers_data'] = self.get_performers_data(scene)
            item['tags'] = ['Lesbian', 'Kissing']
            item['duration'] = self.get_duration(scene)
            item['trailer'] = scene.xpath('.//td[contains(.//b, "Desc:")]//a[contains(@href, "trailer")]/@href').get()
            if item['trailer']:
                item['trailer'] = "https://www.kissmegirl.com/" + item['trailer']
            item['site'] = "Kiss Me Girl"
            item['parent'] = "Kiss Me Girl"
            item['network'] = "Kiss Me Girl"
            item['type'] = "Scene"
            sceneid = item['image']
            sceneid = re.search(r'.*/(.*?)\.', sceneid).group(1)
            sceneid = sceneid.replace("small", "")
            item['id'] = sceneid
            item['url'] = f"https://www.kissmegirl.com/video/{sceneid}"

            yield item

    def get_performers(self, scene):
        performers = scene.xpath('.//b[contains(text(), "Stars:")]/following-sibling::text()')
        if performers:
            performers = performers.get()
            if "," in performers:
                performers = performers.split(",")
                return list(map(lambda x: string.capwords(x.strip()), performers))
            else:
                return [string.capwords(performers.strip())]
        return []

    def get_performers_data(self, response):
        performers = self.get_performers(response)
        performers_data = []
        if len(performers):
            for performer in performers:
                perf = {}
                perf['name'] = performer
                perf['extra'] = {}
                perf['extra']['gender'] = "Female"
                perf['network'] = "Kiss Me Girl"
                perf['site'] = "Kiss Me Girl"
                performers_data.append(perf)
        return performers_data
