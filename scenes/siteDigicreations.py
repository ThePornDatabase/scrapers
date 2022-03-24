import re
import string
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteDigicreationsSpider(BaseSceneScraper):
    name = 'Digicreations'
    network = 'Digicreations'

    start_urls = [
        'https://digicreationsxxx.com',
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'external_id': r'',
        'trailer': '',
        'pagination': '/index.php/model-page%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@itemprop="articleBody"]/div/em')
        for scene in scenes:
            item = SceneItem()

            item['title'] = string.capwords(scene.xpath('./text()').get())
            image = scene.xpath('./following-sibling::a/img/@src').get()
            item['image'] = self.format_link(response, image)
            item['image_blob'] = None
            item['description'] = ''
            item['trailer'] = ''
            item['tags'] = []
            item['performers'] = []
            item['date'] = self.parse_date('today').isoformat()
            item['id'] = re.search(r'rokgallery/.*?/(.*).jpg', item['image'])
            if not item['id']:
                item['id'] = re.search(r'rokgallery/.*?/(.*).png', item['image'])
            item['id'] = item['id'].group(1)
            item['network'] = 'Digicreations'
            item['parent'] = 'Digicreations'
            item['site'] = 'Digicreations'
            item['url'] = response.url
            yield item

    def get_next_page_url(self, base, page):
        if int(page) == 1:
            return "https://digicreationsxxx.com/index.php/browse-movies"
        return self.format_url(base, self.get_selector_map('pagination') % page)
