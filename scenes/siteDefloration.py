import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteDeflorationSpider(BaseSceneScraper):
    name = 'Defloration'
    network = 'Defloration'
    parent = 'Defloration'
    site = 'Defloration'

    start_urls = [
        # ~ 'https://www.defloration.com',
        'file:///scrapy/scrapyProduction/tpdb/defloration.html',
    ]

    selector_map = {
        'title': '//h1[@class="entry-title"]/text()',
        'description': '//div[@class="entry-content"]/article//text()',
        'date': '//div[@class="entry-meta-top"]/text()',
        're_date': r'(\w+ \d{1,2}, \d{4})',
        'image': '//div[@class="entry-content"]/article//img/@src',
        'image_blob': True,
        'performers': '//h1[@class="entry-title"]/text()',
        'tags': '',
        'external_id': r'.*/(.*?)/',
        'trailer': '',
        'pagination': '/freetour.php?page=%s'
    }

    def start_requests(self):

        for link in self.start_urls:
            yield scrapy.Request(url=link,
                                 callback=self.parse,
                                 headers=self.headers,
                                 cookies=self.cookies)

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="textblock1"]/p/strong/../..')
        for scene in scenes:
            item = SceneItem()
            mylist = scene.xpath('.//*').getall()
            mylist = "".join(mylist)
            if "goland" in mylist.lower():
                print(mylist)
            title = scene.xpath('./p/strong/text()')
            if title:
                item['title'] = title.get().strip()
            else:
                item['title'] = None

            item['date'] = self.parse_date('today').isoformat()

            item['performers'] = self.parse_performer(item['title'])
            item['tags'] = ['Hymen', 'Defloration', 'Virgin']

            image = scene.xpath('.//img/@src')
            if image:
                item['image'] = "https://www.defloration.com/" + image.get().strip()
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
                # ~ item['image_blob'] = None
                item['id'] = re.search(r'.*/(.*?)\.jpg', item['image']).group(1)
            else:
                image = scene.xpath('./following-sibling::div//img/@src')
                if image:
                    item['image'] = "https://www.defloration.com/" + image.get().strip()
                    item['image_blob'] = self.get_image_blob_from_link(item['image'])
                    # ~ item['image_blob'] = None
                    item['id'] = re.search(r'.*/(.*?)\.jpg', item['image']).group(1)
                else:
                    item['image'] = None
                    item['image_blob'] = None
                    item['id'] = None

            description = scene.xpath('./p[2]//text()')
            if description:
                description = description.getall()
                item['description'] = " ".join(description).replace("\n", "").replace("\r", "").replace("\t", "").replace("  ", "").strip()
            else:
                item['description'] = None

            item['trailer'] = None
            item['url'] = "https://www.defloration.com/freetour.php"
            item['network'] = 'Defloration'
            item['parent'] = 'Defloration'
            item['site'] = 'Defloration'

            if "goland" in item['title'].lower():
                print(item)
            yield item

    def parse_performer(self, title):
        performer = ''
        if title:
            if re.search(r'(\w+ \w+)\.', title):
                performer = re.search(r'(\w+ \w+)\.', title).group(1)
            else:
                if len(re.findall(r'\w+', title)) == 2:
                    performer = title.strip()
        if performer:
            return [string.capwords(performer)]
        return[]
