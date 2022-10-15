import re
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteThaiSwingerSpider(BaseSceneScraper):
    name = 'ThaiSwinger'
    network = 'Thai Swinger'
    parent = 'Thai Swinger'
    site = 'Thai Swinger'

    start_urls = [
        'https://www.thaiswinger.com',
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
        'pagination': '/index.php?start=%s'
    }

    def get_next_page_url(self, base, page):
        page = str(32 * (int(page) - 1))
        return self.format_url(base, self.get_selector_map('pagination') % page)

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="col-sm-6 mb-4"]')
        for scene in scenes:
            item = SceneItem()

            item['title'] = self.cleanup_title(scene.xpath('.//h2/a/text()').get())
            item['description'] = scene.xpath('.//p[@class="videoStory"]/text()').get().strip()
            scenedate = scene.xpath('.//span[@class="videoDate"]/text()')
            if scenedate:
                item['date'] = self.parse_date(scenedate.get(), date_formats=['%B %d, %Y']).isoformat()
            else:
                item['date'] = self.parse_date('today').isoformat()

            item['performers'] = []
            item['tags'] = scene.xpath('.//span[@class="videoSection"]/a/text()').getall()
            image = scene.xpath('.//comment()')
            if image:
                image = image.get()
                item['image'] = self.format_link(response, re.search(r'src=\"(.*\.jpg)', image).group(1))
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
                item['id'] = re.search(r'.*/(.*?)/', item['image']).group(1)
            else:
                item['image'] = ""
                item['image_blob'] = ""
                item['id'] = ""
            item['trailer'] = ""
            item['url'] = response.url
            item['network'] = "Thai Swinger"
            item['parent'] = "Thai Swinger"
            item['site'] = "Thai Swinger"

            yield self.check_item(item, self.days)
