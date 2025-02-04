import re
import string
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkFerroNetworkSpider(BaseSceneScraper):
    name = 'FerroNetwork'

    start_urls = [
        'http://updates.ferronetwork.com'
    ]

    selector_map = {
        'type': 'Scene',
        'external_id': r'',
        'pagination': '/updates%s.shtml',
    }

    def get_next_page_url(self, base, page):
        if page == 1:
            return "http://updates.ferronetwork.com/updates.shtml"
        return self.format_url(base, self.get_selector_map('pagination') % page)

    def get_scenes(self, response):
        scenes = response.xpath('//table[@class="rezphoto"]//img/ancestor::td[1]')
        for scene in scenes:
            item = self.init_scene()
            item['performers'] = scene.xpath('.//a[contains(@href, "?a=search")]/text()').getall()
            item['performers'] = list(map(lambda x: string.capwords(x.strip()), item['performers']))
            item['title'] = ", ".join(item['performers'])
            item['url'] = scene.xpath('./a[1]/@href').get()
            item['image'] = scene.xpath('./a/img/@src').get()
            item['image_blob'] = self.get_image_blob_from_link(item['image'])

            sceneid = re.search(r'/(\w+)/video/(\d+\w+?)', item['image'])
            if sceneid:
                item['id'] = sceneid.group(1) + sceneid.group(2)
            site = scene.xpath('.//p/a/text()').get()
            item['site'] = re.sub(r'\.\w{3,4}$', '', site)
            item['parent'] = 'FerroNetwork'
            item['network'] = 'FerroNetwork'
            item['type'] = "Scene"

            datetext = scene.xpath('.//span/text()').get()
            datetext = datetext.replace(" ", "")

            scenedate = re.search(r'(\d{2}\.\d{2}\.\d{4})', datetext).group(1)
            item['date'] = self.parse_date(scenedate, date_formats=['%d.%m.%Y']).strftime('%Y-%m-%d')

            minutes = re.search(r'(\d+)min', datetext)
            seconds = re.search(r'(\d+)sec', datetext)
            duration = 0
            if minutes:
                duration = duration + int(minutes.group(1)) * 60
            if seconds:
                duration = duration + int(seconds.group(1))
            item['duration'] = str(duration)

            if item['id']:
                yield self.check_item(item, self.days)
            else:
                print(item)
