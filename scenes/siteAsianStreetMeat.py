import re
from PIL import Image
import base64
from io import BytesIO
from tpdb.helpers.http import Http
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteAsianStreetMeatSpider(BaseSceneScraper):
    name = 'AsianStreetMeat'

    start_urls = [
        'https://asianstreetmeat.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/enter/?p=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//table[@class="glass_push_more"]')
        for scene in scenes:
            item = SceneItem()
            title = scene.xpath('.//tr[@class="height100"]/td[1]/div[@class="cm"][1]/a/text()')
            if not title:
                title = scene.xpath('.//table[@class="glass_push_more"]//video/@title')
                if title:
                    title = re.search(r' - (.*) - ', title.get()).group(1)
            else:
                title = title.get()

            if title:
                item['title'] = self.cleanup_title(title)
                item['description'] = self.cleanup_description(scene.xpath('.//div[@class="blurb_v3"]//text()').get())
                item['image'] = scene.xpath('.//video/@poster').get()
                item['image_blob'] = self.get_image_blob_from_link(item['image'], headers={'Referer': 'https://asianstreetmeat.com/'})
                item['date'] = ''
                scenedate = re.search(r'photogroup/(\d{8})', item['image'])
                if scenedate:
                    item['date'] = self.parse_date(scenedate.group(1), date_formats=['%Y%m%d']).strftime('%Y-%m-%d')
                item['performers'] = []
                item['tags'] = ['Asian']
                if "anal" in item['title'].lower():
                    item['tags'].append("Anal")
                if "lesbian" in item['title'].lower():
                    item['tags'].append("Lesbian")

                item['duration'] = None
                duration = scene.xpath('.//div[@class="cm" and contains(a/text(), "minutes")]/a/text()[1]')
                if duration:
                    duration = duration.getall()
                    duration = re.search(r'(\d+)', " ".join(duration))
                    if duration:
                        item['duration'] = str(int(duration.group(1)) * 60)
                item['trailer'] = scene.xpath('.//video/source[contains(@src, ".mp4")]/@src').get()
                item['id'] = re.search(r'photogroup/(\d+)', item['image']).group(1)
                item['url'] = self.format_link(response, scene.xpath('.//div[@class="cm"]/a[contains(@href, "/join/")]/@href').get())
                item['site'] = 'Asian Street Meat'
                item['parent'] = 'Asian Street Meat'
                item['network'] = 'Asian Street Meat'
                yield self.check_item(item, self.days)

    def get_image_from_link(self, image, headers):
        if image:
            req = Http.get(image, headers=headers, verify=False)
            # ~ print(req)
            if req and req.status_code == 200:
                return req.content
        return None

    def get_image_blob_from_link(self, image, headers):
        if image:
            data = self.get_image_from_link(image, headers)
            if data:
                try:
                    img = BytesIO(data)
                    img = Image.open(img)
                    img = img.convert('RGB')
                    width, height = img.size
                    if height > 1080 or width > 1920:
                        img.thumbnail((1920, 1080))
                    buffer = BytesIO()
                    img.save(buffer, format="JPEG")
                    data = buffer.getvalue()
                except:
                    print(f"Could not decode image for evaluation: '{image}'")
                return base64.b64encode(data).decode('utf-8')
        return None
