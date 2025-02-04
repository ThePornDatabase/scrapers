import re
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteTSRiannaJamesSpider(BaseSceneScraper):
    name = 'TSRiannaJames'
    site = 'TS Rianna James'
    parent = 'TS Rianna James'
    network = 'TS Rianna James'

    start_urls = [
        'https://www.tsriannajames.com'
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'trailer': '',
        'type': 'Scene',
        'external_id': r'',
        'pagination': '/video-list?page=%s',
    }

    def get_next_page_url(self, base, page):
        page = int(page)
        if page == 1:
            return "https://www.tsriannajames.com/video-list"
        page = str(page - 1)
        return self.format_url(base, self.get_selector_map('pagination') % page)

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class, "views-row-")]')
        for scene in scenes:
            item = self.init_scene()
            title = scene.xpath('.//h2/text()').get()
            item['title'] = self.cleanup_title(title)

            description = scene.xpath('.//div[contains(@class, "text-with-summary")]//div[contains(@property, "encoded")]/text()').get()
            if description:
                item['description'] = self.cleanup_description(description.replace("&nbsp;", "").replace("\n", "").replace("\r", "").replace("\t", ""))

            image = scene.xpath('.//div[contains(@class, "field-slideshow") and contains(@class, "first")]/img[1]/@src')
            if image:
                item['image'] = image.get()
                item['image_blob'] = self.get_image_blob_from_link(item['image'])

            item['performers'] = scene.xpath('.//div[contains(text(), "Girls:")]/following-sibling::div/div/a/text()').getall()

            item['type'] = "Scene"
            item['site'] = 'TS Rianna James'
            item['network'] = 'TS Rianna James'
            item['parent'] = 'TS Rianna James'

            item['url'] = self.format_link(response, scene.xpath('./div/@about').get())
            item['id'] = re.search(r'.*/(.*?)$', item['url']).group(1)

            yield item
