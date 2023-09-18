import re
import string
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteSubmissiveCuckoldsSpider(BaseSceneScraper):
    name = 'SubmissiveCuckolds'

    start_urls = [
        'http://submissivecuckolds.com',
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
        'pagination': '/cuckold_last_updates_tour.php?sta=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//table/tbody/tr/td')
        print(f"Scene Count: {len(scenes)}")
        for scene in scenes:
            print(response.url)
            item = SceneItem()

            title = scene.xpath('.//div[@class="lastup"]/strong/text()')
            if title:
                item['title'] = self.cleanup_title(title.get())
            else:
                item['title'] = ''

            scenedate = scene.xpath('.//div[@class="lastup"]/font/text()')
            if scenedate:
                scenedate = re.search(r'(\d{2} \w+ \d{4})', scenedate.get()).group(1)
                item['date'] = self.parse_date(scenedate, date_formats=['%d %B %Y']).isoformat()
            else:
                item['date'] = ""

            description = scene.xpath('./div/text()')
            if description:
                item['description'] = self.cleanup_description(description.get()).replace("Clips: ", "")
            else:
                item['description'] = ''

            performers = scene.xpath('.//div[@class="lastup"]/strong/text()').getall()
            if performers:
                item['performers'] = list(map(lambda x: string.capwords(x.strip()), performers))
            else:
                item['performers'] = []

            item['tags'] = ['Female Domination', 'Cuckold']

            image = scene.xpath('./img[contains(@src, "submissivecuckolds")]/@src').get()
            if image:
                item['image'] = image.strip().replace(" ", "%20")
            else:
                item['image'] = None

            item['image_blob'] = self.get_image_blob_from_link(item['image'])

            item['trailer'] = ''

            if image:
                externalid = re.search(r'.*/(\d+)\.jpg', item['image'])
                if externalid:
                    item['id'] = externalid.group(1)

            item['url'] = response.url

            item['site'] = "Submissive Cuckolds"
            item['parent'] = "Submissive Cuckolds"
            item['network'] = "Submissive Cuckolds"

            yield self.check_item(item, self.days)

    def get_next_page_url(self, base, page):
        page = str((int(page) - 1) * 18)
        return self.format_url(base, self.get_selector_map('pagination') % page)
