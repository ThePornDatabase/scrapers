import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class TeenCoreClubSpider(BaseSceneScraper):
    name = 'TeenCoreClub'
    network = 'Teen Core Club'
    parent = 'Teen Core Club'

    start_url = 'https://api.fundorado.com'
    # Note: These scenes could all have been pulled from one API location, but the returned JSON doesn't include any
    #       site or category information, so I needed to split them up like this to return the associated site per scene
    #       I checked available scenes as of writing and there were not any duplicate ids between sites

    start_urls = [
        # ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=176&genre=0', 'TCC Network Archives'],
        # ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=178&genre=0', 'Analyzed Girls'],
        ['1944', 'Ass Teen Mouth'],
        # ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=182&genre=0', 'Bang Teen Pussy'],
        # ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=184&genre=0', 'Brutal Invasion'],
        # ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=186&genre=0', 'Cumaholic Teens'],
        # ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=188&genre=0', 'Defiled18'],
        # ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=190&genre=0', 'Double Teamed Teens'],
        # ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=192&genre=0', 'Dream Teens HD'],
        # ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=194&genre=0', 'Girls Got Cream'],
        # ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=196&genre=0', 'Hardcore Youth'],
        # ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=198&genre=0', 'Little Hellcat'],
        # ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=200&genre=0', 'Make Teen Gape'],
        # ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=202&genre=0', 'Nylon Sweeties'],
        # ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=204&genre=0', 'Seductive18'],
        # ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=206&genre=0', 'Teen Anal Casting'],
        # ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=208&genre=0', 'Teen Drillers'],
        # ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=210&genre=0', 'Teen Gina'],
        # ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=212&genre=0', 'Teens Natural Way'],
        # ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=214&genre=0', 'Teens Try Black'],
        # ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=216&genre=0', 'Try Teens'],
        # ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=218&genre=0', 'White Teens Black Cocks'],
        # ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=220&genre=0', 'Young Throats'],
        # ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=278&genre=0', 'College Party Time'],
        # ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=280&genre=0', 'Cum Filled Throat'],
        # ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=284&genre=0', 'Cumsumption Cocktail'],
        # ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=284&genre=0', 'Dirty Babysitter'],
        # ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=288&genre=0', 'Drill My Butt'],
        # ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=290&genre=0', 'Dual Throat'],
        # ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=292&genre=0', 'Gang Land Victims'],
        # ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=294&genre=0', 'Little Teen Suckers'],
        # ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=296&genre=0', 'Make Teen Moan'],
        # ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=298&genre=0', 'MegaPenetrations'],
        # ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=300&genre=0', 'Messy Gangbangs'],
        # ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=302&genre=0', 'My Black Coeds'],
        # ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=304&genre=0', 'My Latina Teen'],
        # ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=306&genre=0', 'Nasty Ass Lickers'],
        # ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=308&genre=0', 'Naughty Little Nymphs'],
        # ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=310&genre=0', 'Never Done That Before'],
        # ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=312&genre=0', 'Pink Eye Sluts'],
        # ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=314&genre=0', 'Plug2Holes'],
        # ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=316&genre=0', 'Road Gangbangs'],
        # ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=318&genre=0', 'SchoolBus Chicks'],
        # ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=320&genre=0', 'Show Me Gape'],
        # ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=322&genre=0', 'Shy Teachers Pet'],
        # ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=324&genre=0', 'Small Tits Hunter'],
        # ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=326&genre=0', 'Teenagers Going Wild'],
        # ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=328&genre=0', 'Teens Love Blacks'],
        # ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=330&genre=0', 'Teens Try Anal'],
        # ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=332&genre=0', 'Teens Want Orgies'],
        # ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=334&genre=0', 'Tugjob Queens'],
        # ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=336&genre=0', 'White Box Black Cocks'],
        # ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=362&genre=0', 'Clean My Ass'],
        # ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=362&genre=0', 'Clean My Ass'],
        # ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=366&genre=0', 'Spermantino'],
        # ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=368&genre=0', 'Teach My Ass'],
        # ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=418&genre=0', 'Russian Teen Updates'],
        # ['https://www.teencoreclub.com', '/browsevideos/api/all?page=%s&resType=site&actor=0&label=556&genre=0', 'Pussy Babes'],
    ]

    selector_map = {
        'external_id': 'updates\\/(.*)\\.html$',
        'trailer': '//video/source/@src',
        'pagination': '/tour/categories/movies_%s_d.html'
    }

    async def start(self):
        for link in self.start_urls:
            meta = {}
            meta['site_num'] = link[0]
            meta['site'] = link[1]
            meta['base_url'] = self.start_url
            meta['page'] = self.page
            yield scrapy.Request(url=self.get_next_page_url(meta['site_num'], meta['page']),
                                 callback=self.parse,
                                 meta=meta,
                                 headers=self.headers,
                                 cookies=self.cookies)

    def parse(self, response, **kwargs):
        count = 0
        scenes = self.get_scenes(response)
        if scenes:
            count = len(scenes)
            for scene in scenes:
                yield scene

        if count:
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                meta = response.meta
                meta['page'] = meta['page'] + 1
                print('NEXT PAGE: ' + str(meta['page']))
                yield scrapy.Request(url=self.get_next_page_url(meta['site_num'], meta['page']),
                                     callback=self.parse,
                                     meta=meta,
                                     headers=self.headers,
                                     cookies=self.cookies)

    def get_next_page_url(self, site_num, page):
        url = f"https://api.fundorado.com/api/videos/browse/studio/{site_num}?page={page}&sg=true&sort=release&video_type=movie&lang=en&site_id=10&genre=0&dach=false"
        return url

    def get_scenes(self, response):
        print("Hello!")
        meta = response.meta
        jsondata = response.json()
        jsondata = jsondata['videos']['data']
        # print(jsondata)
        for scene in jsondata:
            print(scene)
        #     if ("id" in scene and scene['id']) and ("slug" in scene and scene['slug']):
        #         link = f"https://api.fundorado.com/api/videodetail/{scene['id']}"
        #         yield scrapy.Request(link, callback=self.parse_scene, meta=meta, headers=self.headers)

    def parse_scene(self, response):
        scene = response.json()
        print(scene)
        item = SceneItem()
        item['title'] = self.cleanup_title(scene['video']['title'])

        item['date'] = scene['video']['dateRelease']

        item['id'] = scene['video']['id']

        description = scene['video']['description']
        if description:
            item['description'] = self.cleanup_description(description)
        else:
            item['description'] = ""

        item['image'] = self.format_link(response, scene['video']['mainPhoto']).replace(" ", "%20")
        item['image_blob'] = self.get_image_blob_from_link(item['image'])
        item['trailer'] = ""

        item['url'] = f"https://www.gayhoopla.com/video/{scene['video']['slug']}"

        item['tags'] = []
        if "tags" in scene and scene['tags']:
            for tag in scene['tags']:
                item['tags'].append(string.capwords(tag['name']))
        if "Gay" not in item['tags']:
            item['tags'].append("Gay")

        item['duration'] = self.duration_to_seconds(scene['video']['duration'])

        item['site'] = 'Gay Hoopla'
        item['parent'] = 'Gay Hoopla'
        item['network'] = 'Gay Hoopla'
        item['performers'] = []
        for model in scene['video']['models']:
            item['performers'].append(model['name'])

        yield self.check_item(item, self.days)