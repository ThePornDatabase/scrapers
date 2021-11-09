import re
import dateparser

from tpdb.BaseSceneScraper import BaseSceneScraper
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
                    item['title'] = title.group(1).strip().title()
                    item['id'] = title.group(1).strip()

            item['performers'] = []
            performers = scene.xpath('.//img[contains(@src,"fft")]/@src').get()
            if performers:
                performers = re.search(r'fft_(.*)\.', performers)
                if performers:
                    item['performers'] = [performers.group(1).strip()]

            item['date'] = ''
            date = scene.xpath('./preceding-sibling::font[1]/b/text()').getall()
            if date:
                date = "".join(date)
                date = date.replace("\r", "").replace("\n", "").replace("&nbsp;", "").strip()
                date = re.search(r'(\d{2}/\d{2}/\d{4})', date)
                if date:
                    date = date.group(1)
                    item['date'] = dateparser.parse(date.strip()).isoformat()

            if not item['date']:
                item['date'] = dateparser.parse('today').isoformat()

            description = scene.xpath('.//div[@align="justify"]/font/text()').getall()
            if description:
                description = " ".join(description)
                description = description.replace("\r", "").replace("\n", "").replace("&nbsp;", "").strip()
                description = re.sub(r'\s{3,100}', ' ', description)
                item['description'] = description.strip()
            else:
                item['description'] = ''

            item['tags'] = ['Blowjob', 'Handjob', 'Facial']

            image = scene.xpath('.//td[@rowspan="5"]//img/@src').get()
            if image:
                item['image'] = "https://jesseloadsmonsterfacials.com/visitors/" + image.strip()
            else:
                item['image'] = ''

            trailer = scene.xpath('.//a[contains(@href,"trailer")]/@href').get()
            if trailer:
                item['url'] = "https://jesseloadsmonsterfacials.com/visitors/" + trailer.strip()
                item['trailer'] = "https://jesseloadsmonsterfacials.com/visitors/" + trailer.strip().replace(".htm", ".mp4")
            else:
                item['trailer'] = ''

            item['site'] = "Jesse Loads Monster Facials"
            item['parent'] = "Jesse Loads Monster Facials"
            item['network'] = "Jesse Loads Monster Facials"

            if item['url'] and item['id']:
                yield item

    def get_next_page_url(self, base, page):
        page = str(page)
        page = page.zfill(2)
        url = self.format_url(base, self.get_selector_map('pagination') % page)
        return url
