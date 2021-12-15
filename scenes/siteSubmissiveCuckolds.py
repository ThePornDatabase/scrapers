import re
from datetime import date, timedelta
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
        scenes = response.xpath('//td[./img[contains(@src, "sexyfootgirls")]]')
        for scene in scenes:
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
                item['date'] = self.parse_date('today').isoformat()

            description = scene.xpath('.//div[contains(@style, "padding-top")]/text()')
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

            image = scene.xpath('./img[contains(@src, "sexyfootgirls")]/@src').get()
            if image:
                item['image'] = image.strip().replace(" ", "%20")
            else:
                item['image'] = None

            item['image_blob'] = None

            trailer = scene.xpath('.//div[@class="popup_block"]/embed/@flashvars').get()
            if trailer:
                trailer = re.search(r'(/trailer.*?\.mp4)', trailer)
                if trailer:
                    trailer = trailer.group(1)
                    item['trailer'] = "http://submissivecuckolds.com/" + trailer.strip().replace(" ", "%20")
            else:
                item['trailer'] = ''

            if image:
                externalid = re.search(r'.*/(\d+)\.jpg', item['image'])
                if externalid:
                    item['id'] = externalid.group(1)

            item['url'] = response.url

            item['site'] = "Submissive Cuckolds"
            item['parent'] = "Submissive Cuckolds"
            item['network'] = "Submissive Cuckolds"

            if item['id'] and item['date'] and "Pics: " not in item['description']:
                days = int(self.days)
                if days > 27375:
                    filterdate = "0000-00-00"
                else:
                    filterdate = date.today() - timedelta(days)
                    filterdate = filterdate.strftime('%Y-%m-%d')

                if self.debug:
                    if not item['date'] > filterdate:
                        item['filtered'] = "Scene filtered due to date restraint"
                    print(item)
                else:
                    if filterdate:
                        if item['date'] > filterdate:
                            yield item
                    else:
                        yield item

    def get_next_page_url(self, base, page):
        page = str((int(page) - 1) * 18)
        return self.format_url(base, self.get_selector_map('pagination') % page)
