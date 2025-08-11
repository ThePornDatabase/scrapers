import re
import requests
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkARXBucksNonAPISpider(BaseSceneScraper):
    name = 'ARXBucksNonAPI'

    cookies = [{"name": "localConsent", "value": "true"}]

    start_urls = [
        "www.analvault.com",
        "cuckhunter.com",
        "honeytrans.com",
        "japanlust.com",
        "joibabes.com",
        "lesworship.com",
        "nudeyogaporn.com",
        "povmasters.com",
        # "randypass.com", # Network site, not single site
        "transdaylight.com",
        "transmidnight.com",
        "transroommates.com"
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//span[contains(text(), "Description:")]/following-sibling::span[1]//text()',
        'date': '//h1/following-sibling::div[1]//span[contains(text(), "|")]/following-sibling::span[contains(text(), ",") and contains(text(), "20")]/text()',
        'date_formats': ['%b %d, %Y'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//span[contains(text(), "Models:")]/following-sibling::div/a//text()',
        'tags': '//span[contains(text(), "Categories:")]/following-sibling::div/a//text()',
        'external_id': r'scenes/(\d+)/',
        'pagination': '/scenes?page=%s',
        'type': 'Scene',
    }

    def start_requests(self):
        ip = requests.get('https://api.ipify.org').content.decode('utf8')
        print('My public IP address is: {}'.format(ip))

        meta = {}
        meta['page'] = self.page

        singleurl = self.settings.get('url')
        if singleurl:
            yield scrapy.Request(singleurl, callback=self.parse_scene, meta=meta, headers=self.headers, cookies=self.cookies)
        else:
            for link in self.start_urls:
                link = "https://" + link
                meta['site'] = re.search(r'(\w+)\.com', link).group(1)
                meta['parent'] = meta['site']
                meta['network'] = 'ARXBucks'
                yield scrapy.Request(url=self.get_next_page_url(link, self.page), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//h2/ancestor::a[contains(@href, "/scenes/")]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    # ~ def get_date(self, response):
        # ~ scenedate = response.xpath('//h1/following-sibling::div[1]//span[contains(text(), "|")]/following-sibling::span[contains(text(), ",") and contains(text(), "20")]').get()
        # ~ print(scenedate)
