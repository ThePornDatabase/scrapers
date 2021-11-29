import re
from datetime import date, timedelta
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteLegsJapanSpider(BaseSceneScraper):
    name = 'UraLesbian'
    network = 'Digital J Media'
    parent = 'Ura Lesbian'

    start_urls = [
        'https://www.uralesbian.com'
    ]

    selector_map = {
        'title': '',
        'description': '',
        'performers': '',
        'date': '',
        'image': '',
        'tags': '',
        'trailer': '',
        'external_id': '',
        'pagination': '/en/samples?page=%s'
    }

    def start_requests(self):

        url = "https://www.uralesbian.com/getdata.php?l=0&c=10"
        yield scrapy.Request(url, callback=self.get_scenes,
                             meta={'page': 1},
                             headers=self.headers,
                             cookies=self.cookies)

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="content-obj"]')
        for scene in scenes:
            content_type = scene.xpath('.//div[@class="content-date-type"]/div[contains(text(),"photo") or contains(text(),"video")]/text()').get()
            if content_type:
                if "video" in content_type.lower().strip():
                    item = SceneItem()

                    title = scene.xpath('./div[@class="content-info"]/a/div/text()').get()
                    if title:
                        item['title'] = self.cleanup_title(title)
                    else:
                        item['title'] = ''

                    description = scene.xpath('./div[@class="content-info"]/a/div/text()').get()
                    if description:
                        item['description'] = self.cleanup_description(description)
                    else:
                        item['description'] = ''

                    performers = scene.xpath('.//a[contains(@href,"/model/")]/text()').getall()
                    if performers:
                        item['performers'] = list(map(lambda x: x.strip(), performers))
                    else:
                        item['performers'] = []

                    tags = scene.xpath('.//div/div[@class="content-tags"]/a/div/text()').getall()
                    if tags:
                        item['tags'] = list(map(lambda x: x.strip(), tags))
                    else:
                        item['tags'] = []

                    scenedate = scene.xpath('.//div[contains(@class,"content-date")]/div[1][not(contains(text(),"photo")) and not(contains(text(),"video"))]/text()').get()
                    if scenedate:
                        item['date'] = self.parse_date(scenedate, date_formats=['%m/%d/%Y']).isoformat()
                    else:
                        item['date'] = self.parse_date('today').isoformat()

                    image = scene.xpath('./div[contains(@class,"content-img")]/@style').get()
                    if image:
                        image = re.search('(https:.*.jpg)', image).group(1)
                        if image:
                            item['image'] = image.strip()
                    else:
                        item['image'] = None

                    item['image_blob'] = None

                    if item['image']:
                        extern_id = re.search(r'\.com/.*?/(.*?)/', item['image']).group(1)
                        if extern_id:
                            item['id'] = extern_id.strip()
                            item['trailer'] = "https://cdn.uralesbian.com/content/" + extern_id.strip() + "/hover.mp4"

                    item['site'] = "Ura Lesbian"
                    item['parent'] = "Ura Lesbian"
                    item['network'] = "Digital J Media"

                    item['url'] = "https://www.uralesbian.com/en/updates/" + item['id']

                    days = int(self.days)
                    if days > 27375:
                        filterdate = "0000-00-00"
                    else:
                        filterdate = date.today() - timedelta(days)
                        filterdate = filterdate.strftime('%Y-%m-%d')

                    if self.debug:
                        if not item['date'] > filterdate:
                            item['filtered'] = "Scene filtered due to date restraint"
                        print(item)
                    else:
                        if filterdate:
                            if item['date'] > filterdate:
                                yield item
                        else:
                            yield item
