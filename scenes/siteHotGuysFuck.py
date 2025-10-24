import string
import scrapy
from requests import get
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteHotGuysFuckSpider(BaseSceneScraper):
    name = 'HotGuysFuck'

    start_url = 'https://api.hotguysfuck.com'

    sites = [
        # ~ {"site": "Gayhoopla", "sitenum": "1", "referer": "https://www.gayhoopla.com"},
        # ~ {"site": "Hot Guys Fuck", "sitenum": "2", "referer": "https://www.hotguysfuck.com"},
        # ~ {"site": "Sugar Daddy Porn", "sitenum": "4", "referer": "https://www.sugardaddyporn.com"},
        # ~ {"site": "Bi Guys Fuck", "sitenum": "5", "referer": "https://www.biguysfuck.com"},
        # ~ {"site": "Hot Guys House", "sitenum": "9", "referer": "https://www.hotguyshouse.com"}
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/api/videos?type=&page=%s',
        'type': 'Scene',
    }

    def start_requests(self):
        ip = get('https://api.ipify.org').content.decode('utf8')
        print('My public IP address is: {}'.format(ip))

        meta = {}
        meta['page'] = self.page

        # ~ for site self.sites:
            # ~ meta = {}
            # ~ meta['siteheaders'] = {
                # ~ "origin": "https://www.hotguysfuck.com",
                # ~ "referer": "https://www.hotguysfuck.com/",
                # ~ "site": site['sitenum']
            # ~ }
            # ~ meta['site'] = site['site']

            # ~ yield scrapy.Request(url=self.get_next_page_url(self.start_url, self.page), callback=self.parse, meta=meta, headers=meta['siteheaders'], cookies=self.cookies, dont_filter=True)

    def parse(self, response, **kwargs):
        scenes = self.get_scenes(response)
        count = 0

    def get_scenes(self, response):
        meta = response.meta
        print(response.text)
        if "Unhandled match case" not in response.text:
            jsondata = response.json()
            jsondata = jsondata['videos']['data']
            print()
            print(meta['siteheaders']['site'] + ": ", jsondata[1])
            print()

            # ~ for scene in jsondata:
                # ~ if ("id" in scene and scene['id']) and ("slug" in scene and scene['slug']):
                    # ~ link = f"https://api.hotguysfuck.com/api/video?slug={scene['slug']}"
                    # ~ yield scrapy.Request(link, callback=self.parse_scene, meta=meta, headers=meta['siteheaders'], dont_filter=True)
        else:
            print(f"No site found for #{meta['siteheaders']['site']}")

    def parse_scene(self, response):
        meta = response.meta
        scene = response.json()
        item = SceneItem()
        if "video" in scene and scene["video"]:
            item['title'] = self.cleanup_title(scene['video']['title'])

            item['date'] = scene['video']['dateRelease']

            if item['date'] > '2023-12-18':
                item['id'] = scene['video']['id']
            else:
                item['id'] = scene['video']['slug']

            if "description" in scene['video'] and scene['video']['description']:
                item['description'] = self.cleanup_description(scene['video']['description'])
            else:
                item['description'] = ""

            item['image'] = self.format_link(response, scene['video']['mainPhoto']).replace(" ", "%20")
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['trailer'] = ""

            item['url'] = f"{meta['sitedef']['referer']}/video/{scene['video']['slug']}"

            item['tags'] = []
            if "tags" in scene and scene['tags']:
                for tag in scene['tags']:
                    item['tags'].append(string.capwords(tag['name']))

            item['duration'] = self.duration_to_seconds(scene['video']['duration'])

            item['site'] = meta['sitedef']['site']
            item['parent'] = meta['sitedef']['site']
            item['network'] = "Blurred Media"
            item['performers'] = []
            for model in scene['video']['models']:
                item['performers'].append(model['name'])

            yield self.check_item(item, self.days)
