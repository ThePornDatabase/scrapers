import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from scrapy.utils.project import get_project_settings


class SiteWestCoastGangbangsSpider(BaseSceneScraper):
    name = 'WestCoastGangbangs'
    network = 'West Coast Gangbangs'
    parent = 'West Coast Gangbangs'
    site = 'West Coast Gangbangs'

    start_url = 'http://www.westcoastgangbangs.com/wcgbhtml/index.html'
    # ~ start_url = 'http://www.westcoastgangbangs.com/wcgbhtml/gangbangarchive.html'

    selector_map = {
        'title': '//div[@align="center"]/p/b/font/text()|//p[@align="center"]/strong/font/text()',
        'description': '//tr[@align="center"]/td/p//span//text()|//tr[@align="center"]/td//div[@align="justify"]/text()',
        'date': '',
        'image': '//tr[@align="center" and @valign="middle"][1]/td[1]//img[contains(@src, ".jp")][1]/@src|//tr[@align="center" and @valign="middle"][1]/td[1]//img[contains(@src, ".pn")][1]/@src|//td[@align="center" and @valign="top"]//p/img[1]/@src|//td[@align="center" and @valign="top"]//td[1]/img[not(contains(@src, ".gif"))][1]/@src',
        'performers': '//b[contains(text(), "Name:")]/../following-sibling::font/text()',
        'tags': '',
        'trailer': '',
        'external_id': r'previews/(.*?)/',
        'pagination': ''
    }

    def start_requests(self):
        settings = get_project_settings()

        meta = {}
        meta['page'] = self.page
        if 'USE_PROXY' in settings.attributes.keys():
            use_proxy = settings.get('USE_PROXY')
        else:
            use_proxy = None

        if use_proxy:
            print(f"Using Settings Defined Proxy: True ({settings.get('PROXY_ADDRESS')})")
        else:
            try:
                if self.proxy_address:
                    meta['proxy'] = self.proxy_address
                    print(f"Using Scraper Defined Proxy: True ({meta['proxy']})")
            except Exception:
                print("Using Proxy: False")

        link = self.start_url
        yield scrapy.Request(url=link,
                             callback=self.get_scenes,
                             meta=meta,
                             headers=self.headers,
                             cookies=self.cookies)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//a[contains(@href, "previews") and contains(@href, ".htm")]/@href').getall()
        for scene in scenes:
            scene = scene.replace("..", "")
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        return ["Gangbang", "FMM+"]

    def get_title(self, response):
        title = super().get_title(response)
        title = title.replace(" 's", "'s").strip()
        return title

    def get_image(self, response):
        if 'image' in self.get_selector_map():
            image = self.get_element(response, 'image', 're_image')
            if isinstance(image, list):
                image = image[0]
            if "../" in image:
                image = re.search(r'.*/(.*)', image).group(1)
            image = re.search(r'(.*/)', response.url).group(1) + image
            return self.format_link(response, image).replace(' ', '%20')
        return ''
