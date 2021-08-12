import re

import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SecretFriendsSpider(BaseSceneScraper):
    name = 'SecretFriends'

    url = 'https://www.secretfriends.com'

    # This is an index site with quite a few European sites indexed.  The External IDs seem to match up with a couple
    # of sites on Metadata (ClubSweethearts for example), so I'm going ahead and including them since they're receiving 
    # newer updates

    paginations = [
        '/portal/videos?q=&website=4Kcfnm&niche=&page=%s',
        '/portal/videos?q=&website=BBvideo&niche=&page=%s',
        '/portal/videos?q=&website=BeautyAndTheSenior&niche=&page=%s',
        '/portal/videos?q=&website=ClubBangBoys&niche=&page=%s',
        '/portal/videos?q=&website=Clubsweethearts&niche=&page=%s',
        '/portal/videos?q=&website=Cuckoldest&niche=&page=%s',
        '/portal/videos?q=&website=Daringsexhd&niche=&page=%s',
        '/portal/videos?q=&website=ElegantRaw&niche=&page=%s',
        '/portal/videos?q=&website=FamilyScrew&niche=&page=%s',
        '/portal/videos?q=&website=Fetish+Prime&niche=&page=%s',
        '/portal/videos?q=&website=GrandMams&niche=&page=%s',
        '/portal/videos?q=&website=GrandparentsX&niche=&page=%s',
        '/portal/videos?q=&website=GroupBanged&niche=&page=%s',
        '/portal/videos?q=&website=GroupSexGames&niche=&page=%s',
        '/portal/videos?q=&website=Hollandschepassie&niche=&page=%s',
        '/portal/videos?q=&website=letsgobi&niche=&page=%s',
        '/portal/videos?q=&website=MatureVan&niche=&page=%s',
        '/portal/videos?q=&website=My+Milfz&niche=&page=%s',
        '/portal/videos?q=&website=peepleak&niche=&page=%s',
        '/portal/videos?q=&website=Plumperd&niche=&page=%s',
        '/portal/videos?q=&website=Pornstarclassics&niche=&page=%s',
        '/portal/videos?q=&website=RedLightSexTrips&niche=&page=%s',
        '/portal/videos?q=&website=SinfulXXX&niche=&page=%s',
        '/portal/videos?q=&website=Southernsins&niche=&page=%s',
        '/portal/videos?q=&website=Submissed&niche=&page=%s',
        '/portal/videos?q=&website=Summer+Sinners&niche=&page=%s',
        '/portal/videos?q=&website=SweetheartsClassics&niche=&page=%s',
        '/portal/videos?q=&website=Swhores&niche=&page=%s',
        '/portal/videos?q=&website=Teenrs&niche=&page=%s',
        '/portal/videos?q=&website=Youngbusty&niche=&page=%s',
    ]

    selector_map = {
        'title': '//h3/text()',
        'description': '//div[@class="top-5"]/text()',
        'date': '//span[contains(text(),"Published")]/b/text()',
        'date_formats': ['%d.%m.%Y','%y-%m-%d'],        
        'image': '//video/@poster',
        'performers': '//div[contains(text(),"Performer")]/text()',
        'tags': '//span[contains(text(),"Niches")]/following-sibling::a/text()',
        'external_id': '.*\/(.+)$',
        'trailer': '//div[@class="player-wrapper"]//video/source/@src',
    }

    def start_requests(self):
        for pagination in self.paginations:
            yield scrapy.Request(url=self.get_next_page_url(self.url, self.page, pagination),
                                 callback=self.parse,
                                 meta={
                'page': self.page, 'pagination': pagination},
                headers=self.headers,
                cookies=self.cookies)

    def parse(self, response, **kwargs):
        if response.status == 200:
            scenes = self.get_scenes(response)
            count = 0
            for scene in scenes:
                count += 1
                yield scene

            if count:
                if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                    meta = response.meta
                    meta['page'] = meta['page'] + 1
                    print('NEXT PAGE: ' + str(meta['page']))
                    yield scrapy.Request(url=self.get_next_page_url(self.url, meta['page'], meta['pagination']),
                                         callback=self.parse,
                                         meta=meta,
                                         headers=self.headers,
                                         cookies=self.cookies)

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class,"event-wrapper")]/div[contains(@class,"description")]/span/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        return response.xpath(
            '//div[@style="font-size: 12px;"]/a[contains(@href,"/site/")]/text()').get().strip()

    def get_parent(self, response):
        return response.xpath(
            '//div[@style="font-size: 12px;"]/a[contains(@href,"/site/")]/text()').get().strip()

    def get_network(self, response):
        return response.xpath(
            '//div[@style="font-size: 12px;"]/a[contains(@href,"/site/")]/text()').get().strip()

    def get_performers(self, response):
        performers = self.process_xpath(
            response, self.get_selector_map('performers')).getall()
        performers = " ".join(performers)
        performers = performers.replace('\r', '').replace('\n', '')
        if "Performer" in performers:
            if "Site" in performers:
                performers = re.search('Performer.*:(.*)Site', performers).group(1)
            else:
                performers = re.search('Performer.*:(.*)', performers).group(1)
            if performers:
                performers = performers.strip()
                performers = performers.split(",")
                performers_stripped = [s.strip() for s in performers]
                performers_stripped = [s.rstrip(',') for s in performers_stripped]
                return list(map(lambda x: x.strip(), performers_stripped))
        return []

    def get_next_page_url(self, url, page, pagination):
        return self.format_url(url, pagination % page)

    def get_description(self, response):
        if 'description' not in self.get_selector_map():
            return ''

        description = self.process_xpath(
            response, self.get_selector_map('description')).get()

        if description is not None:
            return description.replace('Description:', '').strip()
        return ""

    def get_title(self, response):
        title = self.process_xpath(
            response, self.get_selector_map('title')).get()
        if title:
            if ":" in title:
                title = re.search(':(.*)', title).group(1)
                if title:
                    return title.strip().title()
        return ''
