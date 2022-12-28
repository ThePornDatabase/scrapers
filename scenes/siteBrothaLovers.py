import re
import scrapy
from scrapy.utils.project import get_project_settings
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteBrothaLoversSpider(BaseSceneScraper):
    name = 'BrothaLovers'
    network = 'Brotha Lovers'
    parent = 'Brotha Lovers'
    site = 'Brotha Lovers'

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
        'pagination': '',
        'type': 'Scene',
    }

    def start_requests(self):
        settings = get_project_settings()
        meta = {}
        if 'USE_PROXY' in self.settings.attributes.keys():
            use_proxy = self.settings.get('USE_PROXY')
        elif 'USE_PROXY' in settings.attributes.keys():
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

        link = 'https://www.interracialsexx.com/interracialsexx/updates.htm'
        yield scrapy.Request(link, callback=self.get_scenes, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        scenes = response.xpath('//p[@align="center"]/font[contains(text(), "/")]')
        for scene in scenes:
            item = SceneItem()
            scenedate = scene.xpath('./text()')
            if scenedate:
                scenedate = scenedate.get()
                scenedate = re.search(r'(\d+/\d+/\d+)', scenedate)
                if scenedate:
                    scenedate = scenedate.group(1).strip()
                    item['date'] = self.parse_date(scenedate, date_formats=['%m/%d/%Y', '%m/%d/%y']).isoformat()
                    search_query = f'//p[@align="center"]/font[contains(text(), "{scenedate}")]/../following-sibling::div[1]'
                    # ~ search_query = f'//p[@align="center"]/font[contains(text(), "{scenedate}")]/../following-sibling::table[1]'
                    scenemain = response.xpath(search_query)
                    if scenemain:
                        title = scenemain.xpath('./table//td[@colspan="2"]//font[@size="2"]/text()')
                        # ~ title = scenemain.xpath('.//font[@size="2" and contains(text(), "&")]/text()')
                        if title:
                            title = title.get()
                            title = title.replace("&amp;", "&").replace("\r", "").replace("\n", "").replace("\t", "").replace("  ", " ").strip()
                            item['title'] = title

                            if " - " in title:
                                title = re.search(r"(.*) - ", title).group(1)
                            item['performers'] = title.split("&")
                            item['performers'] = list(map(lambda x: x.strip(), item['performers']))

                            image = scenemain.xpath('.//img[@width="200"]/@src')
                            if image:
                                image = image.get()
                                image = self.format_link(response, image.replace("..", ""))
                                item['image'] = image
                                item['image_blob'] = None
                            else:
                                item['image'] = None
                                item['image_blob'] = None

                            item['description'] = None
                            item['trailer'] = None
                            item['tags'] = ['Interracial', 'BBC']
                            item['duration'] = None
                            item['type'] = 'Scene'
                            item['url'] = response.url
                            item['network'] = 'Brotha Lovers'
                            item['parent'] = 'Brotha Lovers'
                            item['site'] = 'Brotha Lovers'

                            sceneid = scenemain.xpath('.//a[contains(@href, ".wmv") or contains(@href, ".mp4") and not(contains(@href, "-HD"))]/@href')
                            if sceneid:
                                sceneid = sceneid.get()
                                if sceneid:
                                    sceneid = re.search(r'.*/(.*)\.', sceneid)
                                    if sceneid:
                                        sceneid = sceneid.group(1)
                                        item['id'] = sceneid.strip()

                                        yield self.check_item(item, self.days)
