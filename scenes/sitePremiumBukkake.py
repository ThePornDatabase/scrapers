import re
import string
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SitePremiumBukkakeSpider(BaseSceneScraper):
    name = 'PremiumBukkake'
    network = 'Premium Bukkake'
    parent = 'Premium Bukkake'
    site = 'Premium Bukkake'

    start_urls = [
        'https://premiumbukkake.com',
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
        'pagination': '/tour2/updates/page_%s.html'
    }

    def get_scenes(self, response):
        containers = response.xpath('//div[@class="container"]')
        for container in containers:
            slides = container.xpath('.//div[contains(@class,"slide_top")]/..')
            for slide in slides:
                item = SceneItem()

                item['image'] = self.format_link(response, slide.xpath('.//div[@class="slide_player"]/img/@data-src').get())
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
                item['title'] = string.capwords(slide.xpath('.//h2[@class="slide_title"]/text()').get())
                item['description'] = slide.xpath('.//p[@class="slide_text"]/text()').get()
                scenedate = slide.xpath('.//div[@class="slide_info_row"]/span[contains(text(), "Posted")]/text()').get()
                item['date'] = self.parse_date(re.search(r'(\w+ \d{1,2}, \d{4})', scenedate).group(1), date_formats=['%B %d, %Y']).isoformat()
                item['performers'] = slide.xpath('.//a[contains(@href, "/models")]/text()').getall()
                item['tags'] = slide.xpath('.//div[@class="slide_info_row"]//a[contains(@href, "/categories")]/text()').getall()
                item['tags'] = item['tags'] = list(map(lambda x: string.capwords(x.strip()), item['tags']))
                trailer = slide.xpath('.//span[@class="btn_play"]/@onclick').get()
                item['trailer'] = re.search(r'(http.*\.mp4)', trailer).group(1)
                item['site'] = "Premium Bukkake"
                item['parent'] = "Premium Bukkake"
                item['network'] = "Premium Bukkake"
                item['url'] = response.url
                sceneid = re.search(r'content/.*?/(.*)?/', item['image'])
                if sceneid:
                    sceneid = sceneid.group(1)
                else:
                    sceneid = re.search(r'content/(.*)?/', item['image']).group(1)

                item['id'] = sceneid
                yield self.check_item(item, self.days)
