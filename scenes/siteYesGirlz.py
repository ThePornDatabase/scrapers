import re
import html
import json
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteYesGirlzSpider(BaseSceneScraper):
    name = 'YesGirlz'
    network = 'YesGirlz'
    parent = 'YesGirlz'
    site = 'YesGirlz'

    start_urls = [
        'https://yesgirlz.com/wp-json/wp/v2/scene?per_page=10&page=1',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': 'https://yesgirlz.com/wp-json/wp/v2/scene?per_page=10&page=%s',
    }

    def get_scenes(self, response):
        meta = response.meta
        jsondata = json.loads(response.text)
        for scene in jsondata:
            item = SceneItem()

            item['id'] = scene['id']
            item['title'] = self.cleanup_title(scene['title']['rendered'])
            item['description'] = ''
            item['date'] = scene['date']
            item['url'] = scene['link']
            performers = re.sub(r'<[^<]+?>', '', scene['excerpt']['rendered']).strip().replace(" & ", ", ").replace("Bella Rose Brooklyn Rose", "Bella Rose, Brooklyn Rose")
            performers = html.unescape(performers)
            item['performers'] = performers.split(", ")
            item['tags'] = []
            item['trailer'] = ''
            item['site'] = "YesGirlz"
            item['parent'] = "YesGirlz"
            item['network'] = "YesGirlz"
            item['type'] = 'Scene'
            meta['item'] = item

            yield scrapy.Request(item['url'], callback=self.get_image, headers=self.headers, cookies=self.cookies, meta=meta)

    def get_image(self, response):
        item = response.meta['item']
        image = response.xpath('//video/@data-poster').get()
        item['image'] = self.format_link(response, image)
        item['image_blob'] = self.get_image_blob_from_link(item['image'])
        trailer = response.xpath('//div[contains(@class,"h5vp_player")]/@data-settings').getall()
        trailer1 = trailer[0].replace("\\", "")
        item['trailer'] = re.search(r'(http.*?\.mp4)', trailer1).group(1)
        if "preview" not in item['trailer'].lower():
            item['trailer'] = ''
        # ~ if len(trailer) > 1:
            # ~ trailer2 = trailer[1].replace("\\", "")
            # ~ if re.search(r'(http.*?\.mp4)', trailer2):
                # ~ item['back'] = re.search(r'(http.*?\.mp4)', trailer2).group(1)
            # ~ if re.search(r'(http.*?\.m4v)', trailer2):
                # ~ item['back'] = re.search(r'(http.*?\.m4v)', trailer2).group(1)
            # ~ else:
                # ~ print(trailer2)

        yield item
