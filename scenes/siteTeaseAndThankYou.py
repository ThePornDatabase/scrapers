import re
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteTeaseAndThankYouSpider(BaseSceneScraper):
    name = 'TeaseAndThankYou'
    network = 'Tease And Thank You'
    parent = 'Tease And Thank You'
    site = 'Tease And Thank You'

    start_urls = [
        'https://www.teaseandthankyou.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/php/services.php?function=GetUpdatesByDate&param1=2022&param2=12',
        'type': 'Scene',
    }

    def get_next_page_url(self, base, page):
        submonths = int(page) - 1
        date = datetime.now()
        targetdate = date + relativedelta(months=-submonths)
        month = targetdate.strftime('%m')
        year = targetdate.strftime('%Y')
        url = f'https://www.teaseandthankyou.com/php/services.php?function=GetUpdatesByDate&param1={year}&param2={month}'
        return url

    def get_scenes(self, response):
        jsondata = json.loads(response.text)
        for scene in jsondata:
            item = SceneItem()
            item['title'] = self.cleanup_title(scene['Title'])
            item['description'] = self.cleanup_description(scene['Description'])
            item['date'] = scene['PublishDate']
            item['id'] = scene['ID']
            item['tags'] = []
            for tag in scene['HashTags']:
                item['tags'].append(tag['Hashtag'])
            if '#' in scene['Models']:
                item['performers'] = re.findall(r'\#(.*?)\#', scene['Models'])
            else:
                item['performers'] = []
            item['trailer'] = ''
            item['image'] = f'https://teaseandthankyou.com/updatepreviews/{scene["Folder"]}/videosimage/{scene["VideosImage"]}'.replace(" ", "%20")
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['type'] = 'Scene'
            item['site'] = 'Tease And Thank You'
            item['parent'] = 'Tease And Thank You'
            item['network'] = 'Tease And Thank You'
            item['url'] = 'https://www.teaseandthankyou.com/taty.html'
            yield self.check_item(item, self.days)
