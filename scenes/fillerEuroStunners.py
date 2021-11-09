import re
from datetime import datetime
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem

    # This site is being updated, but not for any sites that are needed.  A lot of the sites that were
    # originally scraped from Data18 had further updates past where Data18 lost the 21Sextury feeds
    # so this is just a one-time scrape to pull those additional scenes.  On this site they only
    # range from the 2015-2020 or so timeframe


class EurostunnersFillerSpider(BaseSceneScraper):
    name = 'Eurostunners'
    network = "Eurostunners"

    url = 'https://eurostunners.com'

    paginations = [
        ['/showcase/21%20Erotic%20Anal/{0}/','21 Erotic Anal', '21Sextury', 'Gamma Enterprises','2000-01-01T12:00:00','current'],
        ['/showcase/21FootArt/{0}/','21FootArt', '21Sextury', 'Gamma Enterprises','2000-01-01T12:00:00','current'],
        ['/showcase/Anal%20Teen%20Club/{0}/','Anal Teen Club', '21Sextury', 'Gamma Enterprises','2000-01-01T12:00:00','current'],
        ['/showcase/Busty%20Fever/{0}/','Busty Fever', '21Sextury', 'Gamma Enterprises','2000-01-01T12:00:00','current'],
        ['/showcase/Daily%20Sex%20Dose/{0}/','Daily Sex Dose', '21Sextury', 'Gamma Enterprises','2011-07-05T12:00:00','current'],
        ['/showcase/DP%20Overload/{0}/','DP Overload', '21Sextury', 'Gamma Enterprises','2012-03-06T12:00:00','current'],
        ['/showcase/Enslaved%20Gals/{0}/','Enslaved Gals', '21Sextury', 'Gamma Enterprises','2012-06-18T12:00:00','current'],
        ['/showcase/Grandpas%20Fuck%20Teens/{0}/','Grandpas Fuck Teens', '21Sextury', 'Gamma Enterprises','2018-03-25T12:00:00','current'],
        ['/showcase/Intermixed%20Sluts/{0}/','Intermixed Sluts', '21Sextury', 'Gamma Enterprises','2012-05-20T12:00:00','current'],
        ['/showcase/Lust%20For%20Anal/{0}/','Lust For Anal', '21Sextury', 'Gamma Enterprises','2012-05-24T12:00:00','current'],
        ['/showcase/Lusty%20Busty%20Chix/{0}/','Lusty Busty Chix', '21Sextury', 'Gamma Enterprises','2012-05-28T12:00:00','current'],
        ['/showcase/Lusty%20Grandmas/{0}/','Lusty Grandmas', '21Sextury', 'Gamma Enterprises','2018-03-30T12:00:00','current'],
        ['/showcase/Oral%20Quickies/{0}/','Oral Quickies', '21Sextury', 'Gamma Enterprises','2012-05-04T12:00:00','current'],
        ['/showcase/Teach%20Me%20Fisting/{0}/','Teach Me Fisting', '21Sextury', 'Gamma Enterprises','2018-03-27T12:00:00','current'],
        ['/showcase/Teen%20Bitch%20Club/{0}/','Teen Bitch Club', '21Sextury', 'Gamma Enterprises','2012-05-19T12:00:00','current'],

        ['/showcase/Wifeys%20World/{0}/','Wifeys World', 'Wifeys World', 'Wifeys World','2000-01-01T12:00:00','current', 'https://pornstar-scenes.com/'],
    ]

    selector_map = {
        'title': '//script[@type="application/ld+json"]/text()',
        'description': '//script[@type="application/ld+json"]/text()',
        'date': '//script[@type="application/ld+json"]/text()',
        'image': '//script[@type="application/ld+json"]/text()',
        'performers': '//h1/a[contains(@href,"model")]/text()',
        'tags': '//div[@class="card-body"]//a[contains(@href,"/tag/")]/text()',
        'external_id': '.*\/(.+)\/$',
        'trailer': '//script[@type="application/ld+json"]/text()',
        'pagination': '/shoots/latest?page=%s'
    }

    def start_requests(self):
        for pagination_item in self.paginations:
            pagination = pagination_item[0]
            site = pagination_item[1]
            parent = pagination_item[2]
            network = pagination_item[3]
            fromdate = pagination_item[4]
            todate = pagination_item[5]
            if pagination_item[6]:
                self.url = pagination_item[6]
            if todate.lower() == 'current':
                todate = datetime.now()
                todate = todate.isoformat()
            yield scrapy.Request(url=self.get_next_page_url(self.url, self.page, pagination),
                                 callback=self.parse,
                                 meta={
                                    'page': self.page,
                                    'pagination': pagination,
                                    'site': site,
                                    'parent': parent,
                                    'network': network,
                                    'fromdate': fromdate,
                                    'todate': todate},
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
        meta = response.meta
        scenes = response.xpath('//a[@class="scene"]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)


    def get_next_page_url(self, url, page, pagination):
        return self.format_url(url, pagination.format(page))

    def get_title(self, response):
        title = self.process_xpath(
            response, self.get_selector_map('title')).get()
        if title:
            if '"name"' in title:
                title = re.search('Object\",\"name\":\s+\"(.*?)\"', title).group(1)
                if title:
                    return title.strip().title()
        return ''

    def get_description(self, response):
        description = self.process_xpath(
            response, self.get_selector_map('description')).get()
        if description:
            if '"description"' in description:
                description = re.search('\"description\":\s+\"(.*?)\"', description).group(1)
                if description:
                    return description.strip()
        return ''

    def get_date(self, response):
        date = self.process_xpath(
            response, self.get_selector_map('date')).get()
        if date:
            if '"uploadDate"' in date:
                date = re.search('\"uploadDate\":\s+\"(.*?)\"', date).group(1)
                if date:
                    return date.strip()
        return ''

    def get_image(self, response):
        image = self.process_xpath(
            response, self.get_selector_map('image')).get()
        if image:
            if '"thumbnailUrl"' in image:
                image = re.search('\"thumbnailUrl\":\s+\"(.*?)\"', image).group(1)
                if image:
                    if image[0:2] == "//":
                        image = "https:" + image
                    image = image.replace('https:https:', 'https:')
                    return image.strip()
        return ''

    def get_trailer(self, response):
        trailer = self.process_xpath(
            response, self.get_selector_map('trailer')).get()
        if trailer:
            if '"contentUrl"' in trailer:
                trailer = re.search('\"contentUrl\":\s+\"(.*?)\"', trailer).group(1)
                if trailer:
                    if trailer[0:2] == "//":
                        trailer = "https:" + trailer
                    trailer = trailer.replace('https:https:', 'https:')
                    return trailer.strip()
        return ''


    def get_site(self, response):
        meta = response.meta
        if meta['site']:
            return meta['site']
        return tldextract.extract(response.url).domain

    def get_network(self, response):
        meta = response.meta
        print (f'Network Meta: {meta}')
        if meta['network']:
            return meta['network']
        return tldextract.extract(response.url).domain

    def get_parent(self, response):
        meta = response.meta
        if meta['parent']:
            return meta['parent']
        return tldextract.extract(response.url).domain



    def parse_scene(self, response):
        meta = response.meta
        item = SceneItem()

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

        if 'network' in response.meta:
            item['network'] = response.meta['network']
        else:
            item['network'] = self.get_network(response)

        if 'parent' in response.meta:
            item['parent'] = response.meta['parent']
        else:
            item['parent'] = self.get_parent(response)

        if item['date'] >= meta['fromdate'] and item['date'] <= meta['todate']:
            if self.debug:
                print(item)
            else:
                yield item
