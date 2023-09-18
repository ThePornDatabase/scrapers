import re
import datetime
from dateutil.relativedelta import relativedelta
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteGangbangMediaGermanySpider(BaseSceneScraper):
    name = 'GangbangMediaGermany'
    network = 'GangbangMediaGermany'
    parent = 'GangbangMediaGermany'
    site = 'GangbangMediaGermany'

    start_urls = [
        'https://p-p-p.tv',
    ]

    selector_map = {
        'title': './/div[contains(@class, "card-footer")]/p[1]/text()',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'duration': '',
        'trailer': '',
        'external_id': r'',
        'pagination': '/en/video/list?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@id, "video")]')
        for scene in scenes:
            item = SceneItem()

            item['id'] = scene.xpath('./@id').get()
            item['title'] = super().get_title(scene)
            item['description'] = ''
            item['image'] = self.format_link(response, scene.xpath('.//img/@src').get())
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['trailer'] = ''
            item['tags'] = ['European','Gangbang']
            item['performers'] = []
            scenedate = scene.xpath('.//i[contains(@class, "calendar")]/following-sibling::text()')
            if scenedate:
                item['date'] = self.get_date_from_string(scenedate.get())
            item['url'] = self.format_link(response, scene.xpath('./a/@href').get())
            item['network'] = 'GangbangMediaGermany'
            item['parent'] = 'GangbangMediaGermany'
            item['site'] = 'GangbangMediaGermany'
            yield self.check_item(item, self.days)

    def get_date_from_string(self, datestring):
        today = datetime.datetime.now()
        datestring = datestring.lower()
        intervalcount = re.search(r'(\d+)', datestring).group(1)
        if not intervalcount:
            intervalcount = 0
        else:
            intervalcount = int(intervalcount)
        if "minute" in datestring:
            date = today - relativedelta(minutes=intervalcount)
        if "hour" in datestring:
            date = today - relativedelta(hours=intervalcount)
        if "day" in datestring:
            date = today - relativedelta(days=intervalcount)
        if "today" in datestring:
            date = today
        if "yesterday" in datestring:
            date = today - relativedelta(days=1)
        if "week" in datestring:
            date = today - relativedelta(weeks=intervalcount)
        if "month" in datestring:
            date = today - relativedelta(months=intervalcount)
        if "year" in datestring:
            date = today - relativedelta(years=intervalcount)

        return date.strftime('%Y-%m-%d')
