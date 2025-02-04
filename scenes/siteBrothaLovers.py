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

    start_urls = ['https://www.interracialsexx.com/']

    selector_map = {
        'external_id': r'',
        'pagination': '',
        'type': 'Scene',
    }

    pages = [
        'https://www.interracialsexx.com/interracialsexx/updates.htm',
        'https://www.interracialsexx.com/interracialsexx/updates2023pt2.htm',
        'https://www.interracialsexx.com/interracialsexx/updates2023pt1.htm',
        'https://www.interracialsexx.com/interracialsexx/updates2022pt2.htm',
        'https://www.interracialsexx.com/interracialsexx/updates2022pt1.htm',
        'https://www.interracialsexx.com/interracialsexx/updates2021pt2.htm',
        'https://www.interracialsexx.com/interracialsexx/updates2021pt1.htm',
        'https://www.interracialsexx.com/interracialsexx/updates2020pt2.htm',
        'https://www.interracialsexx.com/interracialsexx/updates2020pt1.htm',
        'https://www.interracialsexx.com/interracialsexx/updates2019pt2.htm',
        'https://www.interracialsexx.com/interracialsexx/updates2019pt1.htm',
        'https://www.interracialsexx.com/interracialsexx/updates2018pt2.htm',
        'https://www.interracialsexx.com/interracialsexx/updates2018pt1.htm',
    ]

    def get_next_page_url(self, base, page):
        links = self.pages
        page = int(page) - 1
        if page < len(links):
            url = links[page]
            print(url)
            return url
        else:
            return "https://www.google.com"
        # ~ return self.format_url(base, self.get_selector_map('pagination') % page)

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
                    item['date'] = self.parse_date(scenedate, date_formats=['%m/%d/%Y', '%m/%d/%y']).strftime('%Y-%m-%d')
                    search_query = f'//p[@align="center"]/font[contains(text(), "{scenedate}")]/../following-sibling::div[1]'
                    # ~ search_query = f'//p[@align="center"]/font[contains(text(), "{scenedate}")]/../following-sibling::table[1]'
                    scenemain = response.xpath(search_query)
                    if scenemain:
                        title = scenemain.xpath('./table//td[@colspan="2"]/p/font/text()[not(contains(.,"Pics")) and not(contains(.,"Movie"))]')
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
                                item['image_blob'] = self.get_image_blob_from_link(item['image'])
                            else:
                                item['image'] = None
                                item['image_blob'] = None

                            item['description'] = ""
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
