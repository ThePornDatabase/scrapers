import re
from datetime import date, timedelta
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.BaseOCR import BaseOCR

from tpdb.items import SceneItem


class SiteJesseLoadsXSpider(BaseSceneScraper):
    name = 'JesseLoads'
    network = 'Jesse Loads Monster Facials'

    start_urls = [
        'https://jesseloadsmonsterfacials.com',
    ]

    selector_map = {
        'title': '//div[@class="title clear"]/h2/text()',
        'description': '//span[contains(@class,"description")]/text()',
        'date': '//span[contains(@class,"update_date")]/text()',
        'image': '//span[@class="model_update_thumb"]/img/@src',
        'performers': '//span[@class="tour_update_models"]/a/text()',
        'tags': '//span[@class="update_tags"]/a/text()',
        'external_id': r'updates/(.*).html',
        'trailer': '',
        'pagination': '/visitors/tour_%s.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//table[@width="880"]')
        for scene in scenes:
            item = SceneItem()

            item['title'] = ''
            title = scene.xpath('.//img[contains(@src,"fft")]/@src').get()
            if title:
                title = re.search(r'fft_(.*)\.', title)
                if title:
                    item['title'] = self.cleanup_title(title.group(1))
                    item['id'] = title.group(1).strip()

            item['performers'] = []
            performers = scene.xpath('.//img[contains(@src,"fft")]/@src').get()
            if performers:
                performers = re.search(r'fft_(.*)\.', performers)
                if performers:
                    item['performers'] = [performers.group(1).strip()]

            item['date'] = ''
            scenedate = scene.xpath('./preceding-sibling::font[1]/b/text()').getall()
            if scenedate:
                scenedate = "".join(scenedate)
                scenedate = scenedate.replace("\r", "").replace("\n", "").replace("&nbsp;", "").strip()
                scenedate = re.search(r'(\d{2}/\d{2}/\d{4})', scenedate)
                if scenedate:
                    scenedate = scenedate.group(1)
                    item['date'] = self.parse_date(scenedate.strip()).isoformat()

            if not item['date']:
                item['date'] = self.parse_date('today').isoformat()

            description = scene.xpath('.//div[@align="justify"]/font/text()').getall()
            if description:
                description = " ".join(description)
                description = description.replace("\r", "").replace("\n", "").replace("&nbsp;", "").strip()
                description = re.sub(r'\s{3,100}', ' ', description)
                item['description'] = self.cleanup_description(description)
            else:
                item['description'] = ''

            item['tags'] = ['Blowjob', 'Handjob', 'Facial']

            image = scene.xpath('.//td[@rowspan="5"]//img/@src')
            if image:
                item['image'] = "https://jesseloadsmonsterfacials.com/visitors/" + image.get().strip()
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
                sceneid = re.search(r'.*/(.*?)\.jpg', item['image'])
                if sceneid:
                    sceneid = re.sub(r'tour_', '', sceneid.group(1)).strip()
                    if sceneid:
                        if sceneid != item['id']:
                            item['id'] = sceneid
                            item['title'] = self.cleanup_title(sceneid)
                            item['title'] = re.sub(r'(?!\w)iii$', ' III', item['id'])
                            item['title'] = re.sub(r'(?![^i ])ii$', ' II', item['id'])
            else:
                item['image'] = ''
                item['image_blob'] = ''

            if item['image']:
                performer_image = "https://jesseloadsmonsterfacials.com/visitors/" + scene.xpath('.//img[contains(@src,"fft")]/@src').get()

                ocr = BaseOCR()
                image_data = self.get_image_from_link(performer_image)
                text = ocr.get_data_from_image(image_data)
                if text and len(text) > 5:
                    item['title'] = self.cleanup_title(text)
                    item['performers'] = [self.cleanup_title(text)]

            trailer = scene.xpath('.//a[contains(@href,"trailer")]/@href').get()
            if trailer:
                item['url'] = "https://jesseloadsmonsterfacials.com/visitors/" + trailer.strip()
                item['trailer'] = "https://jesseloadsmonsterfacials.com/visitors/" + trailer.strip().replace(".htm", ".mp4")
            else:
                item['url'] = response.url
                item['trailer'] = ''

            item['site'] = "Jesse Loads Monster Facials"
            item['parent'] = "Jesse Loads Monster Facials"
            item['network'] = "Jesse Loads Monster Facials"

            try:
                if item['url'] and item['id']:
                    yield self.check_item(item, self.days)
            except:
                print(item)
    def get_next_page_url(self, base, page):
        page = str(page)
        page = page.zfill(2)
        url = self.format_url(base, self.get_selector_map('pagination') % page)
        return url
