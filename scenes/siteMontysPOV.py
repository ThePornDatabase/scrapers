import re
from datetime import datetime
import dateparser

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class MontysPOVSpider(BaseSceneScraper):
    name = 'MontysPov'
    network = "Montys POV"
    parent = "Montys POV"

    start_urls = [
        'http://www.montyspov.com/',
    ]

    selector_map = {
        # Everything is coming off of the index page for this one
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'external_id': '',
        'trailer': '',
        'pagination': ''
    }

    def get_scenes(self, response):

        sceneresponses = response.xpath('//div[@class="item"]')

        items = []

        for sceneresponse in sceneresponses:
            item = SceneItem()
            item['network'] = 'Montys POV'
            item['parent'] = 'Montys POV'
            item['site'] = 'Montys POV'
            item['trailer'] = ''

            # Date
            date = sceneresponse.xpath(
                './div[@class="meta"]/div[contains(@class,"vidData")]/span[contains(text(),"-")]/text()').get()
            if not date:
                date = datetime.now()
            item['date'] = dateparser.parse(
                date.strip(), date_formats=['%d-%m-%Y']).isoformat()

            # Performer
            performer = sceneresponse.xpath(
                './div[@class="meta"]/div/a[contains(@class,vidLinkName)]/text()').getall()
            if not performer:
                performer = []
            item['performers'] = list(map(lambda x: x.strip(), performer))

            # Tags
            tags = sceneresponse.xpath(
                './div[@class="meta"]/div/div[@class="subListCats"]/a/text()').getall()
            if not tags:
                tags = []
            item['tags'] = list(map(lambda x: x.strip(), tags))

            # Title
            title = sceneresponse.xpath(
                './div[@class="meta"]/div/span[@class="underName"]/text()').get()
            if not title:
                title = performer[0]
            item['title'] = title.strip()

            # Description
            description = sceneresponse.xpath(
                './div[@class="meta"]/div[@class="descriptionBox"]/text()').get()
            if not description:
                description = ''
            item['description'] = description.strip()

            # Image
            image = sceneresponse.xpath('./a/img/@src').get()
            if not image:
                image = None
            item['image'] = image.replace(" ", "%20").strip()

            item['image_blob'] = None

            # URL
            url = sceneresponse.xpath('./a/img/@src').get()
            url = re.search('(.*)\\.(?:jpg|png|gif)', url).group(1)
            item['url'] = url.replace(" ", "%20").strip()

            # ID
            item['id'] = re.search('\\/scene\\/(\\d+)', item['url']).group(1)

            # ~ print(f"Date: {item['date']}")
            # ~ print(f"Perf: {item['performers']}")
            # ~ print(f"Tags: {item['tags']}")
            # ~ print(f"Title: {item['title']}")
            # ~ print(f"Image: {item['image']}")
            # ~ print(f"Desc: {item['description']}")
            # ~ print(f"URL: {item['url']}")
            # ~ print(f"ID: {item['id']}")
            # ~ print("\n\n")

            items.append(item)

        if self.debug:
            print(items)
            return items
        return items

    def get_next_page_url(self, base, page):
        selector = '/public/most-recent/%s/'
        return self.format_url(base, selector % page)
