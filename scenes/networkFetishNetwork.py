import re
import tldextract
import scrapy
from datetime import date, timedelta
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


def match_site(argument):
    match = {
        'AmateurBondageVideos.com': 'Amateur Bondage Videos',
        'AmateurSmothering.com': 'Amateur Smothering',
        'AmateurTrampling.com': 'Amateur Trampling',
        'BondageAuditions.com': 'Bondage Auditions',
        'BrainWashedTeens.com': 'Brainwashed Teens',
        'BreastBondageVideos.com': 'Breast Bondage Videos',
        'BrutalBallBusting.com': 'Brutal Ball Busting',
        'BrutalCastings.com': 'Brutal Castings',
        'DeviceBondageVideos.com': 'Device Bondage Videos',
        'EliteSmothering.com': 'Elite Smothering',
        'EliteSpanking.com': 'Elite Spanking',
        'FaceSittingFreaks.com': 'Face Sitting Freaks',
        'FemDominas.com': 'Fem Dominas',
        'FetishDolls.com': 'Fetish Dolls',
        'FootdomVideos.com': 'Footdom Videos',
        'FootJobAddict.com': 'Footjob Addict',
        'GlamBitches.com': 'Glambitches',
        'HelplessTeens.com': 'Helpless Teens',
        'InternetCreeper.com': 'Internet Creeper',
        'JerkOffInstructors.com': 'Jerkoff Instructors',
        'KinkyCarmen.com': 'Kinky Carmen',
        'LatinSmokers.com': 'Latin Smokers',
        'Missogyny.com': 'Missogyny',
        'MyKinkyDiary.com': 'My Kinky Diary',
        'OperationEscort.com': 'Operation Escort',
        'PainFreaks.com': 'Pain Freaks',
        'PainVixens.com': 'Pain Vixens',
        'PantyhoseCreep.com': 'Pantyhose Creep',
        'PantyhosePops.com': 'Pantyhose Pops',
        'PureSmoking.com': 'Pure Smoking',
        'PureSmothering.com': 'Pure Smothering',
        'PureSpanking.com': 'Pure Spanking',
        'RealBondageVideos.com': 'Real Bondage Videos',
        'RickSavage.com': 'Rick Savage',
        'RopeBondageVideos.com': 'Rope Bondage Videos',
        'SexualDisgrace.com': 'Sexual Disgrace',
        'ShamedSluts.com': 'Shamed Sluts',
        'Smoke4You.com': 'Smoke4You',
        'SmotherSluts.com': 'Smother Sluts',
        'StrapOnSquad.com': 'Strapon Squad',
        'Taboo18.com': 'Taboo18',
        'TeenCreeper.com': 'Teen Creeper',
        'TokyoSlaves.com': 'Tokyo Slaves',
    }
    return match.get(argument, argument)


class FetishNetworkSpider(BaseSceneScraper):
    name = 'FetishNetwork'
    network = 'Fetish Network'
    parent = 'Fetish Network'

    start_urls = [
        'http://www.fetishnetwork.com',
    ]

    pagination = [
        '/t2/show.php?a=2065_%s&nats=typein.4.10.10.0.0.0.0.0',
        '/t2/show.php?a=2040_%s&uvar=typein.4.10.10.0.0.0.0.0',
        '/t2/show.php?a=1824_%s&uvar=typein.4.10.10.0.0.0.0.0'
    ]

    selector_map = {
        'title': '//div[contains(@class,"video-name-area")]/h3/text()',
        'description': '//div[contains(@class,"description-long-text")]/text()',
        'performers': "",
        'date': '//div[contains(@class,"date-section")]/h4/text()',
        'image': '//video[@id="videoplayer"]/@poster',
        'tags': '//span[contains(text(),"Genres:")]/following-sibling::span/a/text()',
        'external_id': r'lid=(\d+)',
        'trailer': '',
        'pagination': '/t2/show.php?a=2040_%s&uvar=typein.4.10.10.0.0.0.0.0'
    }

    def start_requests(self):
        if not hasattr(self, 'start_urls'):
            raise AttributeError('start_urls missing')

        if not self.start_urls:
            raise AttributeError('start_urls selector missing')

        for pagination in self.pagination:
            for link in self.start_urls:
                yield scrapy.Request(url=self.get_next_page_url(link, self.page, pagination),
                                     callback=self.parse,
                                     meta={'page': self.page, 'pagination': pagination},
                                     headers=self.headers,
                                     cookies=self.cookies)

    def parse(self, response, **kwargs):
        scenes = self.get_scenes(response)
        count = 0
        for scene in scenes:
            count += 1
            yield scene

        if count:
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                meta = response.meta
                meta['page'] = meta['page'] + 1
                pagination = meta['pagination']
                print('NEXT PAGE: ' + str(meta['page']))
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page'], pagination),
                                     callback=self.parse,
                                     meta=meta,
                                     headers=self.headers,
                                     cookies=self.cookies)

    def get_next_page_url(self, base, page, pagination):
        return self.format_url(
            base, pagination % page)

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class,"border-aera")]/div/a[contains(@href,"refstat")]/@href').getall()
        for scene in scenes:
            scene = "http://www.fetishnetwork.com/t2/" + scene
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        site = response.xpath('//div[contains(@class,"bigtext-section")]/h3/span[contains(text(),"Videos")]/text()').get()
        if site:
            if "Videos" in site:
                site = re.search('(.*) Videos', site).group(1)
                if site:
                    site = site.strip()
            site = match_site(site)

        if not site:
            site = tldextract.extract(response.url).domain

        return site

    def get_performers(self, response):
        if "1824" in response.url:
            return []

        titlestring = response.xpath('//div[contains(@class,"video-name-area")]/h3/text()').get()
        if re.search(' - ', titlestring):
            titlestring = re.search('(.*) - ', titlestring).group(1)

        titlestring = titlestring.strip()
        titlestring = titlestring.replace("&", ",")
        if "," in titlestring:
            performers = titlestring.split(",")
            performers = list(map(lambda x: x.strip(), performers))
            performers = list(map(lambda x: x.replace("Teen Creeper ", "").strip(), performers))
            return performers

        if titlestring:
            title_list = titlestring.split()
            if len(title_list) == 2 or len(title_list) == 3:
                return [titlestring]
            return ''

    def get_title(self, response):
        title = response.xpath('//title/text()').get()
        if title:
            if re.search(r'(.*) \|', title):
                title = re.search(r'(.*) \|', title).group(1)
        else:
            title = response.xpath('//div[contains(@class,"video-name-area")]/h3/text()').get()

        if title:
            title = title.strip()
            return title
        return ''

    def get_id(self, response):
        search = re.search(r'\/(\d+)\/', response.url, re.IGNORECASE).group(1)
        return search

    def get_image(self, response):
        image = self.process_xpath(response, self.get_selector_map('image')).get()
        if not image:
            image = response.xpath('//video[contains(@id,"my-video")]/@poster').get()

        if not image:
            image = response.xpath('//div[@class="row"]//img[contains(@src,"thumbs/01.jpg")]/@src').get()
        if not image:
            image = response.xpath('//div[contains(@class,"banner-img-single")]/img/@src').get()

        if image:
            image = "http://www.fetishnetwork.com/t2/" + image
            return self.format_link(response, image)
        return ''

    def parse_scene(self, response):
        item = SceneItem()

        if response.xpath('//div[contains(@class,"video-name-area")]/h3/text()'):

            if 'title' in response.meta and response.meta['title']:
                item['title'] = response.meta['title']
            else:
                item['title'] = self.get_title(response)

            if 'description' in response.meta:
                item['description'] = response.meta['description']
            else:
                item['description'] = self.get_description(response)

            if 'site' in response.meta:
                item['site'] = response.meta['site']
            else:
                item['site'] = self.get_site(response)

            if 'date' in response.meta:
                item['date'] = response.meta['date']
            else:
                item['date'] = self.get_date(response)

            if 'image' in response.meta:
                item['image'] = response.meta['image']
            else:
                item['image'] = self.get_image(response)

            item['image_blob'] = None

            if 'performers' in response.meta:
                item['performers'] = response.meta['performers']
            else:
                item['performers'] = self.get_performers(response)

            if 'tags' in response.meta:
                item['tags'] = response.meta['tags']
            else:
                item['tags'] = self.get_tags(response)

            if 'id' in response.meta:
                item['id'] = response.meta['id']
            else:
                item['id'] = self.get_id(response)

            if 'trailer' in response.meta:
                item['trailer'] = response.meta['trailer']
            else:
                item['trailer'] = self.get_trailer(response)

            item['url'] = self.get_url(response)

            if hasattr(self, 'network'):
                item['network'] = self.network
            else:
                item['network'] = self.get_network(response)

            if hasattr(self, 'parent'):
                item['parent'] = self.parent
            else:
                item['parent'] = self.get_parent(response)

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
