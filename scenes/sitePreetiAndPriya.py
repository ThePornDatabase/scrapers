import re
from tpdb.BaseSceneScraper import BaseSceneScraper


class SitePreetiAndPriyaSpider(BaseSceneScraper):
    name = 'PreetiAndPriya'

    start_urls = [
        'https://www.officialpreetiandpriya.com',
    ]

    selector_map = {
        'title': './/div[@class="uk-thumbnail-caption"]/span[1]/text()',
        'description': './/comment()[contains(., "DESC")]/following-sibling::p[1]/span/text()',
        'date': './/span[contains(text(), "ADDED:")]/following-sibling::text()[1]',
        're_date': r'(\d{2}-\w{3,4}-\d{2})',
        'date_formats': ['%d-%b-%y'],
        'image': './/img/@src',
        'performers': '',
        'tags': '',
        'duration': '',
        'trailer': '',
        'external_id': r'',
        'pagination': '/tour/index.php/latest-updates?start=%s',
        'type': 'Scene',
    }

    def get_next_page_url(self, base, page):
        page = str((int(page) - 1) * 60)
        return self.format_url(base, self.get_selector_map('pagination') % page)

    def get_scenes(self, response):
        scenes = response.xpath('//h5[contains(text(), "Video Update")]/..')
        for scene in scenes:
            item = self.init_scene()

            item['title'] = self.get_title(scene)
            item['description'] = self.get_description(scene)
            item['date'] = self.get_date(scene)

            image = scene.xpath('.//img/@src')
            if image:
                item['image'] = f"https://www.officialpreetiandpriya.com{image.get()}"
                item['image_blob'] = self.get_image_blob_from_link(item['image'])

            duration = scene.xpath('.//span[contains(text(), "DURATION:")]/following-sibling::text()[1]')
            if duration:
                duration = duration.get()
                duration = re.sub(r'[^a-z0-9]+', '', duration)
                duration = re.search(r'(\d+)m(\d+)s', duration)
                if duration:
                    minutes = int(duration.group(1)) * 60
                    seconds = int(duration.group(2))
                    duration = str(minutes + seconds)

            if duration:
                item['duration'] = duration

            if "preeti" in item['description'].lower():
                item['performers'].append("Preeti Young")
            if "priya" in item['description'].lower():
                item['performers'].append("Priya Young")
            if "twins" in item['description'].lower() or not item['performers']:
                item['performers'].append("Preeti Young")
                item['performers'].append("Priya Young")

            sceneid = scene.xpath('./../preceding-sibling::comment()')
            if sceneid:
                sceneid = sceneid.getall()
                sceneid = "".join(sceneid).replace("\n", "").replace("\r", "").replace("\t", "")
                sceneid = re.search(r'Free Tour.*?(\d+)', sceneid)
                if sceneid:
                    item['id'] = sceneid.group(1)
            if not item['id']:
                sceneid = re.search(r'(\d+)', item['image'])
                if sceneid:
                    item['id'] = sceneid.group(1)

            item['url'] = f"https://www.officialpreetiandpriya.com/tour/{item['id']}"
            item['site'] = 'Preeti And Priya'
            item['parent'] = 'Preeti And Priya'
            item['network'] = 'Preeti And Priya'
            item['type'] = 'Scene'

            yield self.check_item(item, self.days)
