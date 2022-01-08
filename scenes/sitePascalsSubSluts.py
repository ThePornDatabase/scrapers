import re
import string
from datetime import date, timedelta
import datetime
import dateparser
from dateutil.relativedelta import relativedelta
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SitePascalsSubslutsSpider(BaseSceneScraper):
    name = 'PascalsSubsluts'

    start_urls = [
        'https://www.pascalssubsluts.com',
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
        'pagination': '/submissive/sluts.php?p=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class, "subMargin")]/a/@href').getall()
        for scene in scenes:
            scene = scene.replace('./', 'submissive/')
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_model_scenes)

    def parse_model_scenes(self, response):
        performer = response.xpath('//h3[@class="description-title"]/text()').get()
        performer = string.capwords(performer.strip())
        if 'submissions' in performer.lower():
            performer = ''
        scenes = response.xpath('//div[contains(@class, "individal-video-item")]')
        for scene in scenes:
            item = SceneItem()
            scenetype = string.capwords(scene.xpath('./div/span[@class="video-image-plus"]/text()').get().strip())
            scenelen = scene.xpath('./div/span[@class="video-image-time"]/text()').get().strip()

            title = scene.xpath('./h4/text()')
            if title:
                item['title'] = string.capwords(title.get().strip()) + " (" + scenetype + ")"
            else:
                item['title'] = ''

            item['description'] = string.capwords(performer) + " " + scenetype + ": " + scenelen

            scenedate = scene.xpath('./h5[@class="individal-video-upload"]/text()').get().strip()
            if scenedate:
                item['date'] = parse_date_diff(scenedate)
            else:
                item['date'] = dateparser.parse('today').isoformat()

            image = scene.xpath('./div/a/img/@src')
            if image:
                item['image'] = image.get()
            else:
                item['image'] = ''

            item['image_blob'] = ''

            if " and " in performer.lower():
                performer = performer.lower()
                item['performers'] = performer.split("and")
            else:
                item['performers'] = [performer]
            item['performers'] = list(map(lambda x: string.capwords(x.strip()), item['performers']))

            item['tags'] = ['Submissive']
            if 'solo' in scenetype.lower():
                item['tags'].append('Solo')
            if 'interview' in scenetype.lower():
                item['tags'].append('Interview')
            if 'trailer' in scenetype.lower():
                item['tags'].append('Trailer')
            if 'fuck' in scenetype.lower():
                item['tags'].append('Domination')

            sceneid = scene.xpath('./div/a/img/@alt').get()
            if sceneid:
                sceneid = re.search(r'(\d+)', sceneid)
                if sceneid:
                    item['id'] = sceneid.group(1)
                else:
                    item['id'] = ''

            item['network'] = "Pascals Subsluts"
            item['parent'] = "Pascals Subsluts"
            item['site'] = "Pascals Subsluts"
            item['url'] = response.url
            item['trailer'] = ''

            if item['id'] and item['title'] and 'trailer' not in scenetype.lower():
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


def parse_date_diff(datestring):
    today = datetime.datetime.now()
    datestring = datestring.lower()
    intervalcount = re.search(r'(\d+)', datestring).group(1)
    if not intervalcount:
        intervalcount = 0
    else:
        intervalcount = int(intervalcount)
    if "minute" in datestring:
        scenedate = today - relativedelta(minutes=intervalcount)
    if "hour" in datestring:
        scenedate = today - relativedelta(hours=intervalcount)
    if "day" in datestring:
        scenedate = today - relativedelta(days=intervalcount)
    if "today" in datestring:
        scenedate = today
    if "yesterday" in datestring:
        scenedate = today - relativedelta(days=1)
    if "week" in datestring:
        scenedate = today - relativedelta(weeks=intervalcount)
    if "month" in datestring:
        scenedate = today - relativedelta(months=intervalcount)
    if "year" in datestring:
        scenedate = today - relativedelta(years=intervalcount)

    return scenedate.isoformat()
