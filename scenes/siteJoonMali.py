import requests
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteJoonMaliSpider(BaseSceneScraper):
    name = 'JoonMali'
    network = 'Joon Mali'
    parent = 'Joon Mali'
    site = 'Joon Mali'

    start_urls = [
        'https://joonmali.com',
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
        'pagination': 'https://nats.islanddollars.com/tour_api.php/content/sets?cms_set_ids=&data_types=1&content_count=1&count=24&start=%s&cms_area_id=3ee47221-f523-4dd1-97c0-5cf6cf118a60&cms_block_id=104660&orderby=published_desc&content_type=video&status=enabled',
        'type': 'Scene',
    }

    def get_next_page_url(self, base, page):
        page = str((int(page) - 1) * 24)
        return self.get_selector_map('pagination') % page

    async def start(self):
        url = "https://www.joonmali.com/videos"
        yield scrapy.Request(url, callback=self.start_requests2, headers=self.headers, cookies=self.cookies)

    def start_requests2(self, response):
        ip = requests.get('https://api.ipify.org').content.decode('utf8')
        print('My public IP address is: {}'.format(ip))

        meta = {}
        meta['page'] = 1
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Origin': 'https://joonmali.com',
            'Referer': 'https://joonmali.com/',
            'X-Nats-Cms-Area-Id': '3ee47221-f523-4dd1-97c0-5cf6cf118a60',
            'X-Nats-Entity-Decode': '1',
        }

        singleurl = self.settings.get('url')
        if singleurl:
            yield scrapy.Request(singleurl, callback=self.parse_scene, meta=meta, headers=self.headers, cookies=self.cookies)
        else:
            for link in self.start_urls:
                yield scrapy.Request(url=self.get_next_page_url(link, self.page), callback=self.parse, meta=meta, headers=headers, cookies=self.cookies)

    def get_scenes(self, response):
        jsondata = response.json()
        jsondata = jsondata['sets']

        for scene in jsondata:
            item = self.init_scene()
            item['id'] = scene['cms_set_id']
            title = scene['name']
            title = title.replace(" 4k", "").replace(" 4K", "").strip()
            item['title'] = self.cleanup_title(title)
            item['description'] = self.cleanup_description(scene['description'])
            item['performers'] = []
            for performer in scene['data_types']:
                if 'data_type' in performer and performer['data_type'] and performer['data_type'] == 'Models':
                    for perf_row in performer['data_values']:
                        item['performers'].append(perf_row['name'])
            if not item['performers']:
                item['performers'] = ['Joon Mali']

            item['site'] = "Joon Mali"
            item['network'] = "Joon Mali"
            item['parent'] = "Joon Mali"
            item['url'] = "https://joonmali.com/videos/" + item['id']
            item['date'] = scene['added_nice']
            item['duration'] = scene['lengths']['total']
            item['trailer'] = ''
            item['tags'] = []
            for tags in scene['data_types']:
                if 'data_type' in tags and tags['data_type'] and tags['data_type'] == 'Category':
                    for tag in tags['data_values']:
                        item['tags'].append(tag['name'])
            
            base_url = "https://c762d323d1.mjedge.net"
            thumbs = scene['preview_formatted']['thumb']
            t = thumbs[max(thumbs, key=lambda k: int(k.split('-')[0]) * int(k.split('-')[1]))][0]
            image_url = f"{base_url}{t['fileuri']}?{t['signature']}"
            
            item['image'] = image_url
            item['image_blob'] = self.get_image_blob_from_link(item['image'])

            yield self.check_item(item, self.days)
