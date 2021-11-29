import re
import string
import tldextract
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


def match_site(argument):
    match = {
        'cruel-mistresses': "Cruel Mistresses",
        'elitepain': "Elite Pain",
        'mood-pictures': "Mood Pictures",
    }
    return match.get(argument, argument)


def site_tags(argument):
    match = {
        'cruel-mistresses': ['Female Domination', 'Bondage', 'BDSM', 'Whipping', 'Pain'],
        'mood-pictures': ['Domination', 'Bondage', 'BDSM', 'Whipping', 'Pain'],
        'elitepain': ['Domination', 'Bondage', 'BDSM', 'Whipping', 'Pain'],
    }
    return match.get(argument, argument)


class NetworkMoodUniversePagedSpider(BaseSceneScraper):
    name = 'MoodUniversePaged'
    network = 'Mood Universe'

    start_urls = [
        'http://cruel-mistresses.com',
        'http://elitepain.com',
        'http://mood-pictures.com',
    ]

    def start_requests(self):
        for link in self.start_urls:
            link = link + "/movies.php"
            yield scrapy.Request(link, callback=self.parse,
                                 meta={'page': self.page},
                                 headers=self.headers,
                                 cookies=self.cookies)

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
        if "cruel-mistresses" in response.url:
            xpath = '//div[contains(@class,"movie")]'
        else:
            xpath = '//h2[contains(@id,"newestmovie") or contains(@id,"featuremovies") or contains(@id,"classics")]/following-sibling::div'

        scenes = response.xpath(xpath)
        for scene in scenes:
            item = SceneItem()

            title = scene.xpath('./h3/text()')
            if title:
                item['title'] = string.capwords(title.get())
                item['title'] = re.sub(u'\u0096', u"\u0027", item['title'])
                item['title'] = re.sub(u'\u0092', u"\u0027", item['title'])
                item['title'] = item['title'].replace('`', '')
            else:
                item['title'] = ''

            image = scene.xpath('.//img/@src')
            if image:
                image = image.get()
                item['image'] = self.format_link(response, image)
            else:
                item['image'] = None

            item['image_blob'] = None

            item['url'] = self.format_link(response, scene.xpath('./a[1]/@href').get())

            item['date'] = self.parse_date('today').isoformat()

            item['id'] = scene.xpath('./@id').get().strip()

            item['tags'] = site_tags(tldextract.extract(response.url).domain)
            item['performers'] = []
            item['trailer'] = ''
            item['description'] = ''

            item['network'] = "Mood Universe"
            item['parent'] = match_site(tldextract.extract(response.url).domain)
            item['site'] = match_site(tldextract.extract(response.url).domain)

            if item['id'] and item['title'] and not re.match(r'best\d{1,3}', item['id']):
                yield item
