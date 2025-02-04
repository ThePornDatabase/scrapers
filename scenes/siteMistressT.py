import re
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteMistressTSpider(BaseSceneScraper):
    name = 'MistressT'

    start_urls = [
        'https://www.mistresst.net',
    ]

    selector_map = {
        'external_id': r'',
        # ~ 'pagination': '/video-gallery?page=%s',
        'pagination': '/video-search?search_api_views_fulltext=&page=%s',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class, "node-video")]')
        for scene in scenes:
            item = self.init_scene()

            item['title'] = self.cleanup_title(scene.xpath('.//h2/text()').get())

            scenedate = scene.xpath('.//div[contains(text(), "date:")]/following-sibling::div[1]/div/text()')
            if scenedate:
                scenedate = re.search(r'(\d{2}/\d{2}/\d{4})', scenedate.get())
                if scenedate:
                    item['date'] = self.parse_date(scenedate.group(1), date_formats=['%m/%d/%Y']).strftime('%Y-%m-%d')

            description = scene.xpath('.//div[contains(@class, "text-with-summary")]/div[1]/div/p/text()[not(contains(., "Length:"))]')
            if description:
                item['description'] = self.cleanup_description(description.get())

            tags = scene.xpath('.//div[contains(text(), "Keywords")]/following-sibling::div[1]/div/a/text()')
            if tags:
                tags = tags.getall()
                for tag in tags:
                    item['tags'].append(self.cleanup_title(tag))

            image = scene.xpath('.//img/@src')
            if image:
                item['image'] = image.get()
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
                if "?" in item['image']:
                    item['image'] = re.search(r'(.*?)\?', item['image']).group(1)

            duration = scene.xpath('.//div[contains(@class, "text-with-summary")]/div[1]/div/p/text()[contains(., "Length:")]')
            if duration:
                duration = duration.get()
                duration = re.sub(r'[^a-z0-9]+', '', duration)
                duration = re.search(r'(\d+)min', duration)
                if duration:
                    item['duration'] = str(int(duration.group(1)) * 60)

            item['id'] = scene.xpath('.//li/@id').get()
            item['url'] = f"https://www.mistresst.net/video/{item['id']}"

            item['site'] = "Mistress T"
            item['parent'] = "Mistress T"
            item['network'] = "Mistress T"
            item['type'] = "Scene"

            yield self.check_item(item, self.days)
