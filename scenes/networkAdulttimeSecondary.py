import re
import string
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem
false = False
true = True


class AdultTimeAPISecondarySpider(BaseSceneScraper):
    name = 'AdulttimeSecondary'
    network = 'Gamma Enterprises'

    start_urls = ['https://members.adulttime.com']

    image_sizes = [
        '1920x1080',
        '1280x720',
        '960x544',
        '638x360',
        '201x147',
        '406x296',
        '307x224'
    ]

    trailer_sizes = [
        '1080p',
        '720p',
        '4k',
        '540p',
        '480p',
        '360p',
        '240p',
        '160p'
    ]

    site_list = [
        "18auditions",
        "3dgspot",
        "accidentalgangbang",
        "adulttimepilots",
        "altshift",
        "amateurgaypov",
        "analtrixxx",
        "anatomikmedia",
        "annabellerogers",
        "atldisruptivefilms",
        "baremaidens",
        "bearback",
        "beingtrans247",
        "betweenthesheetswithalisonrey",
        "blacklabelmag",
        "blackmoneyerotica",
        "blakemason",
        "blowmepov",
        "caughtfapping",
        "cardiogasm",
        "caseyatruestory",
        "covertjapan",
        "criticalmassvideo",
        "daddysboy",
        "dareweshare",
        "disruptivefilms",
        "Fine-Erotica",
        "fistingcentral",
        "fistinginferno",
        "forbiddenseductions",
        "frameleaks",
        "futa3dx",
        "futasentaisquad",
        "gangbangaccidents",
        "gayhoopla",
        "gostuckyourself",
        "grinders",
        "hentaisexschool",
        "howwomenorgasm",
        "javstudio",
        "joimom",
        "jerkbuddies",
        "johnbloomberg",
        "johnnyrapid",
        "joimom",
        "korinakova",
        "latinoboysporn",
        "lesbiandatingstories",
        "milfoverload",
        "mommysboy",
        "mugurporn",
        "muses",
        "myyoungerlover",
        "officemsconduct",
        "oralexperiment",
        "peepoodo",
        "phoenixxx",
        "pinkotgirls",
        "rodsroom",
        "sabiendemonia",
        "shapeofbeauty",
        "sinnsage",
        "sistertrick",
        "sloppytoppy",
        "stars",
        "superhornyfuntime",
        "theyeslist",
        "totalhentai",
        "touchmywife",
        "toughlovex",
        "trans500",
        "unrelatedx",
        "upclosex",
        "watchyoucheat",
        "wolfwagner",
        "womensworld",
    ]

    selector_map = {
        'external_id': '(\\d+)$',
        'pagination': '/en/videos?page=%s'
    }

    def start_requests(self):
        page = self.page
        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, page), callback=self.parse_token, meta={'page': page, 'url': link})

    def parse_token(self, response):
        match = re.search(r'\"apiKey\":\"(.*?)\"', response.text)
        token = match.group(1)
        return self.call_algolia(response.meta['page'], token, response.meta['url'])

    def parse(self, response, **kwargs):
        scenes = self.get_scenes(response)
        count = 0
        for scene in scenes:
            count += 1
            yield scene

        if 'page' in response.meta and response.meta['page'] < self.limit_pages:
            next_page = response.meta['page'] + 1
            yield self.call_algolia(next_page, response.meta['token'], response.meta['url'])

    def get_scenes(self, response):
        referrerurl = response.meta["url"]
        jsondata = response.json()['results'][0]['hits']
        for scene in jsondata:
            item = SceneItem()
            item['site'] = scene['sitename']
            if item['site'].lower().strip().replace(" ", "") in self.site_list:
                item['image'] = ''
                for size in self.image_sizes:
                    if size in scene['pictures']:
                        item['image'] = 'https://images-fame.gammacdn.com/movies' + \
                                        scene['pictures'][size]
                        break
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
                item['trailer'] = ''
                item['id'] = scene['objectID'].split('-')[0]
                if 'title' in scene and scene['title']:
                    item['title'] = scene['title']
                else:
                    item['title'] = scene['movie_title']

                item['title'] = string.capwords(item['title'])
                item['description'] = re.sub('<[^<]+?>', '', scene['description']).strip()

                if self.parse_date(scene['release_date']):
                    item['date'] = self.parse_date(scene['release_date']).isoformat()
                else:
                    item['date'] = self.parse_date('today').isoformat()
                item['duration'] = scene['length']
                item['performers'] = []
                for performer in scene['actors']:
                    item['performers'].append(string.capwords(performer['name']))
                item['tags'] = []
                for tag in scene['categories']:
                    item['tags'].append(string.capwords(tag['name']))
                item['markers'] = []
                if 'action_tags' in scene:
                    if scene['action_tags']:
                        for action in scene['action_tags']:
                            marker = {}
                            marker['name'] = action['name']
                            if string.capwords(action['name']) not in item['tags']:
                                item['tags'].append(string.capwords(action['name']))
                            marker['start'] = str(action['timecode'])
                            item['markers'].append(marker)

                item['trailer'] = ''
                for size in self.trailer_sizes:
                    if size in scene['trailers']:
                        item['trailer'] = scene['trailers'][size]
                        break

                item['parent'] = scene['network_name']
                item['network'] = self.network
                item['url'] = self.format_url(response.meta['url'], '/en/video/' + scene['sitename'] + '/' + scene['url_title'] + '/' + str(scene['clip_id']))

                #  The following sites were brought in from other scrapers.  Date limits are to avoid dupes
                donotyield = 0
                if (('mypervyfamily' in item['url'] and item['date'] < "2021-10-06") or ('Filthy Blowjobs' in item['site'] and item['date'] < "2021-09-14") or ('Filthy Massage' in item['site'] and item['date'] < "2021-09-28") or ('Filthy Newbies' in item['site'] and item['date'] < "2021-09-21") or ('Filthy POV' in item['site'] and item['date'] < "2021-10-05") or ('Filthy Taboo' in item['site'] and item['date'] < "2021-10-09")):
                    donotyield = 1

                if ('gangbangcreampie' in item['url'] and item['date'] < "2022-10-29"):
                    donotyield = 1

                if ('gloryholesecrets' in item['url'] and item['date'] < "2022-10-01"):
                    donotyield = 1

                if (('Lusty Grandmas' in item['site'] and item['date'] < "2019-02-01") or ('Grandpas Fuck Teens' in item['site'] and item['date'] < "2019-02-06") or ('Baby Got Balls' in item['site'] and item['date'] < "2008-05-04") or ('Creampie Reality' in item['site'] and item['date'] < "2006-10-04") or ('Cumming Matures' in item['site'] and item['date'] < "2009-12-01")):
                    donotyield = 1

                if (('Dominated Girls' in item['site'] and item['date'] < "2013-08-26") or ('Home Porn Reality' in item['site'] and item['date'] < "2010-06-18") or ('Mandy Is Kinky' in item['site'] and item['date'] < "2008-04-30") or ('Mighty Mistress' in item['site'] and item['date'] < "2014-05-20") or ('Teach Me Fisting' in item['site'] and item['date'] < "2019-01-29") or ('Zoliboy' in item['site'] and item['date'] < "2018-03-18") or ('Pee And Blow' in item['site'] and item['date'] < "2009-12-16") or ('Speculum Plays' in item['site'] and item['date'] < "2007-09-07")):
                    donotyield = 1

                #  Old Young Lesbian Love is returned both from Girlsway and 21Sextreme.  Only pull from Girlsway
                if "oldyounglesbianlove" in scene['sitename'] and "21sextreme" in referrerurl:
                    donotyield = 1

                matches = ['evilangelpartner', 'nudefightclub']
                if not any(x in scene['sitename'] for x in matches):
                    if not donotyield:
                        yield self.check_item(item, self.days)

    def call_algolia(self, page, token, referrer):
        algolia_url = 'https://tsmkfa364q-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(3.35.1)%3B%20Browser%20(lite)%3B%20react%20(16.14.0)%3B%20react-instantsearch%20(5.7.0)%3B%20JS%20Helper%202.26.0&x-algolia-application-id=TSMKFA364Q&x-algolia-api-key=' + token
        # ~ print(algolia_url)

        headers = {
            'Content-Type': 'application/json',
            'Referer': self.get_next_page_url(referrer, page)
        }
        page = page - 1

        # ~ jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=1000&page=' + str(page) + '&attributesToRetrieve=%5B%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22description%22%2C%22action_tags%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%2C%22hasPpu%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&filters=&facets=%5B%22hasSubtitle%22%2C%22categories.name%22%2C%22download_sizes%22%2C%22length_range_15min%22%2C%22actors.name%22%2C%22subtitles.languages%22%2C%22content_tags%22%2C%22availableOnSite%22%2C%22upcoming%22%2C%22network.lvl0%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%2C%5B%22content_tags%3Astraight%22%2C%22content_tags%3Alesbian%22%2C%22content_tags%3Abisex%22%2C%22content_tags%3Atrans%22%2C%22content_tags%3Agay%22%5D%5D"}]}'
        jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1000&maxValuesPerFacet=1000&page=' + str(page) + '&attributesToRetrieve=%5B%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22description%22%2C%22action_tags%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22download_sizes%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22download_file_sizes%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%2C%22hasPpu%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&filters=&facets=%5B%22hasSubtitle%22%2C%22categories.name%22%2C%22download_sizes%22%2C%22length_range_15min%22%2C%22actors.name%22%2C%22subtitles.languages%22%2C%22content_tags%22%2C%22availableOnSite%22%2C%22upcoming%22%2C%22network.lvl0%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%2C%5B%22content_tags%3Astraight%22%2C%22content_tags%3Alesbian%22%2C%22content_tags%3Abisex%22%2C%22content_tags%3Atrans%22%2C%22content_tags%3Agay%22%5D%5D"}]}'
        return scrapy.Request(
            url=algolia_url,
            method='post',
            body=jbody,
            meta={'token': token, 'page': page + 1, 'url': referrer},
            callback=self.parse,
            headers=headers
        )
