import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteDorcelPagesSpider(BaseSceneScraper):
    name = 'DorcelPages'

    start_url = "https://dorcelnetwork.com/"
    sites = [
        'africa-xxx',
        'girls-at-work',
        'contact',
        'luxure',
        'xxx-vintage',
        'thr3e',
    ]

    headers = {
        'Accept-Language': 'en-US,en',
        'x-requested-with': 'XMLHttpRequest',
        'referer': 'https://dorcelnetwork.com/',
    }

    custom_settings = {'CONCURRENT_REQUESTS': '1',
                       'AUTOTHROTTLE_ENABLED': 'True',
                       'AUTOTHROTTLE_DEBUG': 'False',
                       'DOWNLOAD_DELAY': '2',
                       'CONCURRENT_REQUESTS_PER_DOMAIN': '1',

                       'ITEM_PIPELINES': {
                           'tpdb.pipelines.TpdbApiScenePipeline': 400,
                       },
                       'DOWNLOADER_MIDDLEWARES': {
                           'tpdb.middlewares.TpdbSceneDownloaderMiddleware': 543,
                       }
                       }

    selector_map = {
        'title': '//h1[contains(@class, "title")]/text()',
        'date': '//div[contains(@class, "right")]/span[contains(@class, "publish_date")]/text()',
        'image': '//div[contains(@class, "player_container")]//picture/img/@data-src',
        'performers': '//div[@class="actress"]/a/text()',
        'tags': '',
        'trailer': '',
        'external_id': r'/videos/(\d+)/',
        'pagination': '/24api/v1/sites/103/freetour/videos?is_mobile=false&take=12&page=%s'
    }

    def get_next_page_url(self, site, page):
        url = f"https://dorcelnetwork.com/collection/{site}/more?lang=en&page={str(page)}"
        return url

    def start_requests(self):
        for site in self.sites:
            meta = {}
            meta['orig_site'] = site
            meta['parent'] = "Dorcel"
            meta['network'] = "Dorcel"
            meta['page'] = self.page
            url = self.get_next_page_url(meta['orig_site'], self.page)
            yield scrapy.Request(url, method='POST', callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

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
                url = self.get_next_page_url(meta['orig_site'], meta['page'])
                yield scrapy.Request(url, method='POST', callback=self.parse, meta=meta, headers=self.headers)

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class, "scene thumbnail")]/a[1]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=response.meta)

    def get_site(self, response):
        site = response.meta['orig_site']
        if "contact" in site.lower() or "vintage" in site.lower() or "africa" in site.lower():
            site = "Dorcel: " + site
        return string.capwords(site)

    def get_duration(self, response):
        duration = response.xpath('//div[contains(@class, "right")]/span[contains(@class, "duration")]/text()')
        if duration:
            duration = duration.get()
            hours = re.search(r'(\d+)h', duration)
            if hours:
                hours = int(hours.group(1)) * 3600
            else:
                hours = 0

            minutes = re.search(r'(\d+)m', duration)
            if minutes:
                minutes = int(minutes.group(1)) * 60
            else:
                minutes = 0

            seconds = re.search(r'm(\d+)', duration)
            if seconds:
                seconds = int(seconds.group(1))
            else:
                seconds = 0

            duration = hours + minutes + seconds
            return str(duration)
        return None

    def get_description(self, response):
        desc = response.xpath('//div[contains(@class, "description")]/div')
        if desc:
            if len(desc) > 1:
                desc = desc.xpath('./span[contains(@class, "full")]/p//text()')
            else:
                desc = desc.xpath('./p//text()')
            if desc:
                return desc.get()
        return ""

    def get_image(self, response):
        images = response.xpath('//div[contains(@class, "player_container")]//source/@data-srcset').getall()
        if images:
            image_list = []
            for image in images:
                match = re.search(r'.*(http.*?)\s2x.*', image)
                if not match:
                    match = re.search(r'.*(http.*?)\s1x.*', image)
                if match:
                    image_list.append(match.group(1))

            def extract_area(url):
                dim_match = re.search(r'_(\d{3,4})_(\d{3,4})_', url)
                if dim_match:
                    width, height = map(int, dim_match.groups())
                    return width * height
                return 0

            if image_list:
                largest_image = max(image_list, key=extract_area)
                return largest_image

