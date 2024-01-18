import re
import string
from slugify import slugify
import unicodedata
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteHouseOfGordSpider(BaseSceneScraper):
    name = 'HouseOfGord'
    network = 'House Of Gord'
    parent = 'House Of Gord'
    site = 'House Of Gord'

    start_urls = [
        'https://www.houseofgord.com',
    ]

    cookies = {'legal_accepted2': 'yes'}

    selector_map = {
        'external_id': r'',
        'pagination': '/?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class, "relative my-")]/div[1]')
        for scene in scenes:
            item = SceneItem()
            item['title'] = self.cleanup_title(scene.xpath('./../a/text()').get())
            item['url'] = self.format_link(response, scene.xpath('./a[1]/@href').get())
            description = scene.xpath('./a/p/text()').get()
            if description:
                item['description'] = self.cleanup_description(description)
            else:
                item['description'] = ''
            scenedate = scene.xpath('.//div[contains(text(), "added") and contains(text(), "Video")]/text()|.//div[contains(text(), "added") and contains(text(), "Photo")]/text()').get()
            if scenedate:
                scenedate = scenedate.replace("\r", "").replace("\n", "").replace("\t", "")
                scenedate = re.search(r'(\d{1,2} \w{3,4} \d{4})', scenedate).group(1)
                item['date'] = self.parse_date(scenedate, date_formats=['%d %b %Y']).strftime('%Y-%m-%d')
            else:
                item['date'] = ''

            item['performers'] = []
            performers = scene.xpath('./following-sibling::div[contains(@class, "text-sm")]//text()').getall()
            performers = " ".join(performers)
            performers = " ".join(performers.replace("\n", "").replace("\r", "").replace("\t", "").split()).replace("Featuring: ", "")
            if "Keywords:" in performers:
                performers = re.search(r'(.*?)Keywords:', performers).group(1)
            if " - " in performers:
                performers = re.search(r'(.*?) - ', performers).group(1)
            item['performers'] = list(map(lambda x: x.strip(), performers.split(",")))

            item['tags'] = []
            tags = scene.xpath('./following-sibling::div[contains(@class, "text-sm")]/text()[contains(., "Featuring")][1]/following-sibling::a/text()').getall()
            for tag in tags:
                res = any(ele.isupper() for ele in tag)
                if not res:
                    tag = tag.replace("&nbsp;", " ")
                    item['tags'].append(string.capwords(tag))

            image = scene.xpath('./following-sibling::table[1]//tr/td[contains(@style, "53")][1]/a/img/@src|./following-sibling::table[1]//tr/td[1]/a/img/@src').get()
            if image:
                item['image'] = image
                item['image_blob'] = self.get_image_blob_from_link(image)
                item['id'] = re.search(r'previews/(\d+)/', item['image']).group(1)
            else:
                item['image'] = ''
                item['image_blob'] = ''
                item['id'] = slugify(re.sub('[^a-z0-9- ]', '', item['title'].lower().strip()))

            item['duration'] = None
            item['trailer'] = ''
            item['site'] = 'House Of Gord'
            item['parent'] = 'House Of Gord'
            item['network'] = 'House Of Gord'

            yield self.check_item(item, self.days)
