import re
import string
from datetime import date, timedelta
import tldextract

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


def match_site(argument):
    match = {
        'cruelamazons': "Cruel Amazons",
        'cruel-ballbustings': "Cruel Ballbustings",
        'cruel-handjobs': "Cruel Handjobs",
        'cruel-strapon': "Cruel Strapon",
        'domina-amanda': "Domina Amanda",
        'ep-castings': "EP Castings",
        'ep-cinema': "EP Cinema",
        'lady-jenny': "Lady Jenny",
        'mistress-ariel': "Mistress Ariel",
        'mood-castings': "Mood Castings",
        'mood-cinema': "Mood Cinema",
        'russian-spanking': "Russian Spanking",
    }
    return match.get(argument, argument)


def site_tags(argument):
    match = {
        'cruelamazons': ['Female Domination', 'Bondage', 'BDSM', 'Whipping', 'Pain'],
        'cruel-ballbustings': ['Female Domination', 'Bondage', 'BDSM', 'Whipping', 'Pain', 'CBT'],
        'cruel-handjobs': ['Female Domination', 'Bondage', 'BDSM', 'Handjob'],
        'cruel-strapon': ['Female Domination', 'Bondage', 'BDSM', 'Pegging', 'Pain'],
        'domina-amanda': ['Female Domination', 'Bondage', 'BDSM', 'Whipping', 'Pain'],
        'ep-castings': ['Domination', 'Bondage', 'BDSM', 'Whipping', 'Pain'],
        'ep-cinema': ['Domination', 'Bondage', 'BDSM', 'Whipping', 'Pain'],
        'lady-jenny': ['Female Domination', 'Bondage', 'BDSM', 'Whipping', 'Pain', 'CBT'],
        'mistress-ariel': ['Female Domination', 'Bondage', 'BDSM', 'Whipping', 'Pain'],
        'mood-castings': ['Domination', 'Bondage', 'BDSM', 'Spanking', 'Pain'],
        'mood-cinema': ['Domination', 'Bondage', 'BDSM', 'Spanking', 'Pain'],
        'russian-spanking': ['Domination', 'Bondage', 'BDSM', 'Spanking', 'Pain'],
    }
    return match.get(argument, argument)


class NetworkMoodUniverseSpider(BaseSceneScraper):
    name = 'MoodUniverse'
    network = 'Mood Universe'

    start_urls = [
        'http://cruelamazons.com',
        'http://cruel-ballbustings.com',
        'http://cruel-handjobs.com',
        'http://cruel-strapon.com',
        'http://domina-amanda.com',
        'http://archive.ep-castings.com',
        'http://ep-castings.com',
        'http://ep-cinema.com',
        'http://lady-jenny.com',
        'http://mistress-ariel.com',
        'http://mood-castings.com',
        'http://mood-cinema.com',
        'http://russian-spanking.com',
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'external_id': '',
        'trailer': '',
        'pagination': '/home.php?page=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class,"update")]')
        for scene in scenes:
            item = SceneItem()

            title = scene.xpath('./div[@class="text"]/h2/text()')
            if title:
                item['title'] = string.capwords(title.get())
            else:
                item['title'] = ''

            image = scene.xpath('.//a[contains(@class,"shot2")]/@href')
            if image:
                image = image.get()
                image = re.sub(r'\?.*', '', image)
                item['image'] = self.format_link(response, image)
            else:
                item['image'] = None

            item['image_blob'] = None

            item['url'] = response.url

            scenedate = scene.xpath('.//span[@class="date"]/text()')
            if scenedate:
                scenedate = scenedate.get().strip()
                item['date'] = self.parse_date(scenedate, date_formats=['%d %b %Y']).isoformat()
            else:
                item['date'] = self.parse_date('today').isoformat()

            item['id'] = scene.xpath('./@id').get().strip()

            item['tags'] = site_tags(tldextract.extract(response.url).domain)
            item['performers'] = []
            item['trailer'] = ''
            item['description'] = ''

            item['network'] = "Mood Universe"
            if "archive" in response.url:
                item['parent'] = "EP Castings Archive"
                item['site'] = "EP Castings Archive"
            else:
                item['parent'] = match_site(tldextract.extract(response.url).domain)
                item['site'] = match_site(tldextract.extract(response.url).domain)

            if item['id'] and item['title']:
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
