# Historical scraper only.  No new scenes, pulling from Archive.org
import re
import csv
import json
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem
import scrapy


class Spider(BaseSceneScraper):
    name = 'MomPovJSON'
    network = 'MomPov'
    parent = 'MomPov'
    site = 'MomPov'

    # ~ custom_settings = {'DOWNLOADER_MIDDLEWARES': {'scrapy_wayback_machine.WaybackMachineMiddleware': 5}}

    start_urls = [
        'https://www.mompov.com',
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'trailer': '',
        'external_id': r'',
        'pagination': '/tour/page/%s/'
    }

    def start_requests(self):
        f = open('test.json')
        csv_f = csv.reader(f)

        count = 0
        for row in csv_f:
            count = count + 1
            row = list(map(lambda x: x.replace('"', "").strip(), row))
            url = f"https://web.archive.org/web/{row[1]}id_/{row[2]}"
            yield scrapy.Request(url, callback=self.parse_data, meta = {'row': row})
            # ~ if count > 10:
                # ~ break
            # ~ print(row[1])
            # ~ print(row[2])


    def parse_data(self, response):
        print(F"Using Wayback URL: {response.url}")
        item = SceneItem()
        scenes = response.xpath('//div[@id="inner_content"]')
        for scene in scenes:

            item['title'] = self.cleanup_title(scene.xpath('.//a[@class="title"]/text()|//meta[@property="og:title"]/@content').get())
            description = scene.xpath('.//div[contains(@class,"entry_content")]/p//text()').getall()
            description = " ".join(description).strip().replace("  ", " ")
            item['description'] = description
            item['description'] = item['description'].replace("\\n-", "").replace("\\n", "").replace("  ", " ")
            scenemonth = scene.xpath('.//span[@class="month"]/text()').get()
            sceneday = scene.xpath('.//span[@class="day"]/text()').get()
            sceneyear = scene.xpath('.//span[@class="year"]/text()').get()
            if scenemonth and sceneday and sceneyear:
                item['date'] = self.parse_date(f'{sceneyear}-{scenemonth}-{sceneday}').isoformat()
            else:
                item['date'] = self.parse_date('today').isoformat()
            imagepath = re.search(r'(.*id_/)', response.url).group(1)
            imagepath = imagepath.replace("id_", "im_")
            imagelink = scene.xpath('./div/a/img/@src')
            if not imagelink:
                imagelink = scene.xpath('.//div[@class="entry_content"]/p/img/@src')

            if imagelink:
                image = imagepath + imagelink.get()
                item['image_blob'] = self.get_image_blob_from_link(image)
                if re.search(r'src=(.*?\.jpg)', image):
                    item['image'] = re.search(r'src=(.*?\.jpg)', image).group(1)
                else:
                    item['image'] = image
            else:
                item['image'] = ''
                item['image_blob'] = ''
            item['performers'] = []
            item['tags'] = ['Amateur']
            item['trailer'] = ''
            item['url'] = scene.xpath('./div/a/@href|.//div[@class="title_holder"]/h1/a/@href').get()
            try:
                item['id'] = re.search(r'.*/(.*?)/', item['url']).group(1)
            except Exception:
                print(f"Item URL: {item['url']}")
                print(f"Scene Xpath: {scene.xpath('.//*').getall()}")
                print(f"Item Loaded: {item}")
                item['id'] = None
            item['network'] = "MomPov"
            item['parent'] = "MomPov"
            item['site'] = "MomPov"
            if item['id']:
                yield item

    def format_url(self, base, path):
        return 'https://www.mompov.com' + path

    def get_next_page_url(self, base, page):
        if page == 1:
            return base + "/tour"
        pageurl = self.format_url(base, self.get_selector_map('pagination') % page)
        return pageurl
