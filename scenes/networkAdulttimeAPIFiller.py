import re
import string
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem

# NOTE!   This scraper _ONLY_ pulls scenes from AdultTime sites with publicly available video index pages.
#         It will not pull any scenes or images that are unavailable if you simply go to the specific site
#         as a guest user in an incognito browser


def match_site(argument):
    match = {}
    return match.get(argument.lower(), argument)


class AdultTimeAPISpider(BaseSceneScraper):
    name = 'AdulttimeAPIFiller'
    network = 'Gamma Enterprises'

    start_urls = 'https://www.adulttime.com'

    sites = [
        'all-sexstudio',
        'extremepickups',
        'femalesubmission',
        'haileyroseshowcase-channel',
        'futaworld-at',
        'intimatelypov',
        # 'milfmayhem',
        'toywithme',
        'upclosex',
        'polyfamilylife',
        'preggoworld',
        'raunch',
        'theyeslist-channel',
    ]

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

    selector_map = {
        'external_id': '(\\d+)$',
        'pagination': '/en/videos?page=%s'
    }

    def start_requests(self):
        if not hasattr(self, 'start_urls'):
            raise AttributeError('start_urls missing')

        if not self.start_urls:
            raise AttributeError('start_urls selector missing')
        page = int(self.page) - 1

        for site in self.sites:
            link = 'https://www.adulttime.com'
            yield scrapy.Request("https://www.21sextury.com/en/videos/page/1", callback=self.parse_token, meta={'page': page, 'url': link, 'sitelink': link, 'parsesite': site}, dont_filter=True)

    def get_next_page_url(self, base, page):
        if "isthisreal" in base or "touchmywife" in base or "zerotolerance" in base:
            pagination = '/en/videos/page/%s'
        else:
            pagination = self.get_selector_map('pagination')
        return self.format_url(base, pagination % page)

    def parse_token(self, response):
        match = re.search(r'\"apiKey\":\"(.*?)\"', response.text)
        token = match.group(1)
        return self.call_algolia(response.meta['page'], token, response.meta['sitelink'], response.meta['parsesite'])

    def parse(self, response, **kwargs):
        meta = response.meta
        if response.status == 200:
            scenes = self.get_scenes(response)
            count = 0
            for scene in scenes:
                count += 1
                yield scene

            if count:
                if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                    next_page = response.meta['page'] + 1
                    yield self.call_algolia(next_page, response.meta['token'], response.meta['sitelink'], meta['parsesite'])

    def get_scenes(self, response):
        # ~ print(response.json()['results'])
        meta = response.meta
        for scene in response.json()['results'][0]['hits']:
            item = SceneItem()

            item['image'] = ''
            for size in self.image_sizes:
                if size in scene['pictures']:
                    item['image'] = 'https://images-fame.gammacdn.com/movies' + \
                                    scene['pictures'][size]
                    break

            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            # ~ item['image_blob'] = None

            item['trailer'] = ''
            for size in self.trailer_sizes:
                if size in scene['trailers']:
                    item['trailer'] = scene['trailers'][size]
                    break

            item['id'] = scene['objectID'].split('-')[0]

            if 'title' in scene and scene['title']:
                item['title'] = scene['title']
            else:
                item['title'] = scene['movie_title']

            item['title'] = string.capwords(item['title'])

            if 'description' in scene:
                item['description'] = scene['description']
            elif 'description' in scene['_highlightResult']:
                item['description'] = scene['_highlightResult']['description']['value']
            if 'description' not in item:
                item['description'] = ''

            if self.parse_date(scene['release_date']):
                item['date'] = self.parse_date(scene['release_date']).isoformat()
            else:
                item['date'] = self.parse_date('today').isoformat()
            item['performers'] = list(
                map(lambda x: x['name'], scene['actors']))
            item['tags'] = list(map(lambda x: x['name'], scene['categories']))
            item['tags'] = list(filter(None, item['tags']))

            item['duration'] = scene['length']

            if "all-sexstudio" in meta['parsesite']:
                item['site'] = "All-Sex Studio"
                item['parent'] = "All-Sex Studio"
                item['url'] = f"https://members.adulttime.com/en/video/all-sexstudio/{scene['url_title']}/{str(scene['clip_id'])}"

            if "extremepickups" in meta['parsesite']:
                item['site'] = "Extreme Pickups"
                item['parent'] = "Extreme Pickups"
                item['url'] = f"https://members.adulttime.com/en/video/extremepickups/{scene['url_title']}/{str(scene['clip_id'])}"

            if "femalesubmission" in meta['parsesite']:
                item['site'] = "Female Submission"
                item['parent'] = "Female Submission"
                item['url'] = f"https://members.adulttime.com/en/video/femalesubmission/{scene['url_title']}/{str(scene['clip_id'])}"

            if "haileyroseshowcase-channel" in meta['parsesite']:
                item['site'] = "Hailey Roses Showcase"
                item['parent'] = "Hailey Roses Showcase"
                item['url'] = f"https://members.adulttime.com/en/video/haileyroseshowcase-channel/{scene['url_title']}/{str(scene['clip_id'])}"

            if "upclosex" in meta['parsesite']:
                if "sitename" in scene and scene['sitename'] and "vr" in scene['sitename']:
                    item['site'] = scene['sitename']
                else:
                    item['site'] = "Upclose"
                item['parent'] = "Upclose"

            if "futaworld" in meta['parsesite']:
                item['site'] = "Futa World"
                item['parent'] = "Futa World"

            if "milfmayhem" in meta['parsesite']:
                item['site'] = scene['sitename']
                item['parent'] = scene['sitename']

            if "toywithme" in meta['parsesite']:
                item['site'] = "Toy With Me"
                item['parent'] = "Toy With Me"

            if "intimatelypov" in meta['parsesite']:
                item['site'] = "Intimately POV"
                item['parent'] = "Intimately POV"

            if "preggoworld" in meta['parsesite']:
                item['site'] = "PreggoWorld"
                item['parent'] = "PreggoWorld"

            if "raunch" in meta['parsesite']:
                item['site'] = "Raunch"
                item['parent'] = "Raunch"

            if "theyeslist" in meta['parsesite']:
                item['site'] = "TheYesList"
                item['parent'] = "TheYesList"

            if "poly" in meta['parsesite'] and "family" in meta['parsesite']:
                item['site'] = "PolyFamilyLife"
                item['parent'] = "PolyFamilyLife"

            item['network'] = self.network

            if "url" not in item or not item['url']:
                item['url'] = f"https://members.adulttime.com/en/video/adulttime/{scene['url_title']}/{str(scene['clip_id'])}"

            yield self.check_item(item, self.days)

    def call_algolia(self, page, token, site, parsesite):
        # ~ print (f'Page: {page}        Token: {token}     Referrer: {referrer}')
        # ~ algolia_url = 'https://tsmkfa364q-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia for vanilla JavaScript 3.27.1;JS Helper 2.26.0&x-algolia-application-id=TSMKFA364Q&x-algolia-api-key=%s' % token

        # UpcloseX
        # ~ algolia_url = 'https://tsmkfa364q-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(3.35.1)%3B%20Browser%20(lite)%3B%20react%20(16.14.0)%3B%20react-instantsearch%20(5.7.0)%3B%20JS%20Helper%202.26.0&x-algolia-application-id=TSMKFA364Q&x-algolia-api-key=' + token

        # ToyWithMe
        algolia_url = 'https://tsmkfa364q-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(3.35.1)%3B%20Browser%20(lite)%3B%20react%20(18.2.0)%3B%20react-instantsearch%20(5.7.0)%3B%20JS%20Helper%202.26.0&x-algolia-application-id=TSMKFA364Q&x-algolia-api-key=' + token

        referrer = "https://members.adulttime.com"
        headers = {
            'Content-Type': 'application/json',
            'Referer': 'https://members.adulttime.com/'
        }

        # All Sex Studio
        if "all-sexstudio" in parsesite:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Amembers%22%2C%22site%3Aadulttime%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&clickAnalytics=true&facetFilters=%5B%5B%22serie_name%3AAll-Sex%20Studio%22%5D%5D&facetingAfterDistinct=true&facets=%5B%22actors.name%22%2C%22categories.name%22%2C%22hasSubtitle%22%2C%22length_range_15min%22%2C%22network.lvl0%22%2C%22serie_name%22%2C%22subtitles.languages%22%2C%22video_formats.format%22%5D&filters=(content_tags%3A\'trans\'%20OR%20content_tags%3A\'straight\'%20OR%20content_tags%3A\'lesbian\'%20OR%20content_tags%3A\'gay\'%20OR%20content_tags%3A\'bisex\'%20OR%20content_tags%3A\'futa\')%20AND%20(upcoming%3A\'0\')&highlightPostTag=__%2Fais-highlight__&highlightPreTag=__ais-highlight__&hitsPerPage=60&maxValuesPerFacet=1000&page=' + str(page) + '&query=&tagFilters="}]}'

        # Extreme Pickups
        if "extremepickups" in parsesite:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"clickAnalytics=true&facetFilters=%5B%22upcoming%3A0%22%2C%5B%22network.lvl1%3AAdult%20Time%20Originals%20%3E%20Extreme%20Pickups%22%5D%5D&facets=%5B%22network.lvl0%22%2C%22network.lvl1%22%5D&filters=(content_tags%3A\'trans\'%20OR%20content_tags%3A\'straight\'%20OR%20content_tags%3A\'lesbian\'%20OR%20content_tags%3A\'gay\'%20OR%20content_tags%3A\'bisex\'%20OR%20content_tags%3A\'futa\')&hitsPerPage=24&page=' + str(page) + '&tagFilters="}]}'

        # Female Submission
        if "femalesubmission" in parsesite:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"clickAnalytics=true&facetFilters=%5B%22upcoming%3A0%22%2C%5B%22network.lvl1%3AAdult%20Time%20Originals%20%3E%20Femalesubmission%22%5D%5D&facets=%5B%22network.lvl0%22%2C%22network.lvl1%22%5D&filters=(content_tags%3A\'trans\'%20OR%20content_tags%3A\'straight\'%20OR%20content_tags%3A\'lesbian\'%20OR%20content_tags%3A\'gay\'%20OR%20content_tags%3A\'bisex\'%20OR%20content_tags%3A\'futa\')&hitsPerPage=24&page=' + str(page) + '&tagFilters="}]}'

        # Hailey Roses Showcase
        if "haileyroses" in parsesite:
            jbody = '{"requests":[{"indexName":"all_scenes_datetitle_asc","params":"clickAnalytics=true&facetFilters=%5B%5B%22network.lvl1%3AAdult%20Time%20Originals%20%3E%20Hailey%20Rose%20Showcase%22%5D%5D&facets=%5B%22network.lvl0%22%2C%22network.lvl1%22%5D&filters=(content_tags%3A\'trans\'%20OR%20content_tags%3A\'straight\'%20OR%20content_tags%3A\'lesbian\'%20OR%20content_tags%3A\'gay\'%20OR%20content_tags%3A\'bisex\'%20OR%20content_tags%3A\'futa\')&hitsPerPage=24&tagFilters="}]}'

        # Intimately POV
        if "intimatelypov" in parsesite:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=1000&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Amembers%22%2C%22site%3Aadulttime%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&filters=(content_tags%3A\'trans\'%20OR%20content_tags%3A\'straight\'%20OR%20content_tags%3A\'lesbian\'%20OR%20content_tags%3A\'gay\'%20OR%20content_tags%3A\'bisex\')&facets=%5B%22hasSubtitle%22%2C%22categories.name%22%2C%22video_formats.format%22%2C%22length_range_15min%22%2C%22actors.name%22%2C%22subtitles.languages%22%2C%22availableOnSite%22%2C%22upcoming%22%2C%22serie_name%22%2C%22network.lvl0%22%5D&tagFilters=&facetFilters=%5B%5B%22serie_name%3AIntimately%20POV%22%5D%2C%5B%22upcoming%3A0%22%5D%5D"}]}'

        # Poly Family Life
        if "poly" in parsesite and "family" in parsesite:
            jbody = '{"requests":[{"indexName":"all_scenes_datetitle_asc","params":"query=&hitsPerPage=60&maxValuesPerFacet=1000&page=' + str(page) + '&clickAnalytics=true&facetFilters=%5B%5B%22serie_name%3APoly%20Family%20Life%22%5D%5D&facets=%5B%5D&filters=(content_tags%3A\'trans\'%20OR%20content_tags%3A\'straight\'%20OR%20content_tags%3A\'lesbian\'%20OR%20content_tags%3A\'gay\'%20OR%20content_tags%3A\'bisex\'%20OR%20content_tags%3A\'futa\')&hitsPerPage=24&tagFilters="}]}'

        # Upclose
        if "upclosex" in parsesite:
            # ~ jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=1000&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Amembers%22%2C%22site%3Aadulttime%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22isVR%22%2C%22video_formats%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%2C%22hasPpu%22%2C%22ppu_infos%22%2C%22action_tags%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&filters=(content_tags%3A\'trans\'%20OR%20content_tags%3A\'straight\'%20OR%20content_tags%3A\'lesbian\'%20OR%20content_tags%3A\'gay\'%20OR%20content_tags%3A\'bisex\')&facets=%5B%22hasSubtitle%22%2C%22categories.name%22%2C%22video_formats.format%22%2C%22length_range_15min%22%2C%22actors.name%22%2C%22subtitles.languages%22%2C%22availableOnSite%22%2C%22upcoming%22%2C%22serie_name%22%2C%22network.lvl0%22%5D&tagFilters=&facetFilters=%5B%5B%22serie_name%3AUp%20Close%22%5D%2C%5B%22upcoming%3A0%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=1000&page=0&analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Amembers%22%2C%22site%3Aadulttime%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22isVR%22%2C%22video_formats%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%2C%22hasPpu%22%2C%22ppu_infos%22%2C%22action_tags%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=false&filters=(content_tags%3A\'trans\'%20OR%20content_tags%3A\'straight\'%20OR%20content_tags%3A\'lesbian\'%20OR%20content_tags%3A\'gay\'%20OR%20content_tags%3A\'bisex\')&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=serie_name&facetFilters=%5B%5B%22upcoming%3A0%22%5D%5D"},{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=1&maxValuesPerFacet=1000&page=0&analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Amembers%22%2C%22site%3Aadulttime%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&attributesToRetrieve=%5B%22isVR%22%2C%22video_formats%22%2C%22clip_id%22%2C%22title%22%2C%22url_title%22%2C%22pictures%22%2C%22categories%22%2C%22actors%22%2C%22release_date%22%2C%22sitename%22%2C%22clip_length%22%2C%22upcoming%22%2C%22network_name%22%2C%22length%22%2C%22ratings_up%22%2C%22ratings_down%22%2C%22rating_rank%22%2C%22clip_path%22%2C%22channels%22%2C%22mainChannel%22%2C%22views%22%2C%22award_winning%22%2C%22directors%22%2C%22trailers%22%2C%22subtitles%22%2C%22objectID%22%2C%22subtitle_id%22%2C%22source_clip_id%22%2C%22hasPpu%22%2C%22ppu_infos%22%2C%22action_tags%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=false&filters=(content_tags%3A\'trans\'%20OR%20content_tags%3A\'straight\'%20OR%20content_tags%3A\'lesbian\'%20OR%20content_tags%3A\'gay\'%20OR%20content_tags%3A\'bisex\')&attributesToHighlight=%5B%5D&attributesToSnippet=%5B%5D&tagFilters=&facets=upcoming&facetFilters=%5B%5B%22serie_name%3AUp%20Close%22%5D%5D"}]}'
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=1000&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Amembers%22%2C%22site%3Aadulttime%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&filters=(content_tags%3A\'trans\'%20OR%20content_tags%3A\'straight\'%20OR%20content_tags%3A\'lesbian\'%20OR%20content_tags%3A\'gay\'%20OR%20content_tags%3A\'bisex\')&facets=%5B%22hasSubtitle%22%2C%22categories.name%22%2C%22video_formats.format%22%2C%22length_range_15min%22%2C%22actors.name%22%2C%22subtitles.languages%22%2C%22availableOnSite%22%2C%22upcoming%22%2C%22network.lvl0%22%2C%22network.lvl1%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%2C%5B%22network.lvl0%3AUp%20Close%22%5D%5D"}]}'

        # ToyWithMe
        if "toywithme" in parsesite:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=1000&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Amembers%22%2C%22site%3Aadulttime%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&filters=(content_tags%3A\'trans\'%20OR%20content_tags%3A\'straight\'%20OR%20content_tags%3A\'lesbian\'%20OR%20content_tags%3A\'gay\'%20OR%20content_tags%3A\'bisex\')&facets=%5B%22hasSubtitle%22%2C%22categories.name%22%2C%22video_formats.format%22%2C%22length_range_15min%22%2C%22actors.name%22%2C%22subtitles.languages%22%2C%22availableOnSite%22%2C%22upcoming%22%2C%22serie_name%22%2C%22network.lvl0%22%5D&tagFilters=&facetFilters=%5B%5B%22serie_name%3AToy%20With%20Me%22%5D%2C%5B%22upcoming%3A0%22%5D%5D"}]}'

        # Futa World
        if "futaworld" in parsesite:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"query=&hitsPerPage=60&maxValuesPerFacet=1000&page=' + str(page) + '&analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Amembers%22%2C%22site%3Aadulttime%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&facetingAfterDistinct=true&clickAnalytics=true&filters=(content_tags%3A\'trans\'%20OR%20content_tags%3A\'straight\'%20OR%20content_tags%3A\'lesbian\'%20OR%20content_tags%3A\'gay\'%20OR%20content_tags%3A\'bisex\'%20OR%20content_tags%3A\'futa\')&facets=%5B%22hasSubtitle%22%2C%22categories.name%22%2C%22video_formats.format%22%2C%22length_range_15min%22%2C%22actors.name%22%2C%22subtitles.languages%22%2C%22availableOnSite%22%2C%22upcoming%22%2C%22network.lvl0%22%2C%22network.lvl1%22%5D&tagFilters=&facetFilters=%5B%5B%22upcoming%3A0%22%5D%2C%5B%22network.lvl1%3AAdult%20Time%20Originals%20%3E%20Futa%20World%22%5D%5D"}]}'

        # Milf Mayhem Channel
        if "milfmayhem" in parsesite:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Amembers%22%2C%22site%3Aadulttime%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&clickAnalytics=true&facetFilters=%5B%22categories.name%3AMilf%22%5D&facetingAfterDistinct=true&facets=%5B%22actors.name%22%2C%22categories.name%22%2C%22hasSubtitle%22%2C%22length_range_15min%22%2C%22network.lvl0%22%2C%22subtitles.languages%22%2C%22video_formats.format%22%5D&filters=(content_tags%3A\'trans\'%20OR%20content_tags%3A\'straight\'%20OR%20content_tags%3A\'lesbian\'%20OR%20content_tags%3A\'gay\'%20OR%20content_tags%3A\'bisex\'%20OR%20content_tags%3A\'futa\')%20AND%20(upcoming%3A\'0\')&highlightPostTag=__%2Fais-highlight__&highlightPreTag=__ais-highlight__&hitsPerPage=60&maxValuesPerFacet=1000&page=' + str(page) + '&query=&tagFilters="}]}'

        # PreggoWorld
        if "preggoworld" in parsesite:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Amembers%22%2C%22site%3Aadulttime%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&clickAnalytics=true&facetFilters=%5B%5B%22serie_name%3APreggo%20World%22%5D%5D&facetingAfterDistinct=true&facets=%5B%22actors.name%22%2C%22categories.name%22%2C%22hasSubtitle%22%2C%22length_range_15min%22%2C%22network.lvl0%22%2C%22serie_name%22%2C%22subtitles.languages%22%2C%22video_formats.format%22%5D&filters=(content_tags%3A\'trans\'%20OR%20content_tags%3A\'straight\'%20OR%20content_tags%3A\'lesbian\'%20OR%20content_tags%3A\'gay\'%20OR%20content_tags%3A\'bisex\'%20OR%20content_tags%3A\'futa\')%20AND%20(upcoming%3A\'0\')&highlightPostTag=__%2Fais-highlight__&highlightPreTag=__ais-highlight__&hitsPerPage=60&maxValuesPerFacet=1000&page=' + str(page) + '&query=&tagFilters="}]}'

        # Raunch
        if "raunch" in parsesite:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Amembers%22%2C%22site%3Aadulttime%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&clickAnalytics=true&facetFilters=%5B%5B%22serie_name%3ARaunch%22%5D%5D&facetingAfterDistinct=true&facets=%5B%22actors.name%22%2C%22categories.name%22%2C%22hasSubtitle%22%2C%22length_range_15min%22%2C%22network.lvl0%22%2C%22serie_name%22%2C%22subtitles.languages%22%2C%22video_formats.format%22%5D&filters=(content_tags%3A\'trans\'%20OR%20content_tags%3A\'straight\'%20OR%20content_tags%3A\'lesbian\'%20OR%20content_tags%3A\'gay\'%20OR%20content_tags%3A\'bisex\'%20OR%20content_tags%3A\'futa\')%20AND%20(upcoming%3A\'0\')&highlightPostTag=__%2Fais-highlight__&highlightPreTag=__ais-highlight__&hitsPerPage=60&maxValuesPerFacet=1000&page=' + str(page) + '&query=&tagFilters="}]}'

        # TheYesList
        if "theyeslist" in parsesite:
            jbody = '{"requests":[{"indexName":"all_scenes_latest_desc","params":"analytics=true&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Amembers%22%2C%22site%3Aadulttime%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&clickAnalytics=true&facetFilters=%5B%5B%22network.lvl1%3AAdult%20Time%20Originals%20%3E%20The%20Yes%20List%22%5D%5D&facetingAfterDistinct=true&facets=%5B%22actors.name%22%2C%22categories.name%22%2C%22hasSubtitle%22%2C%22length_range_15min%22%2C%22network.lvl0%22%2C%22network.lvl1%22%2C%22subtitles.languages%22%2C%22video_formats.format%22%5D&filters=(content_tags%3A\'trans\'%20OR%20content_tags%3A\'straight\'%20OR%20content_tags%3A\'lesbian\'%20OR%20content_tags%3A\'gay\'%20OR%20content_tags%3A\'bisex\'%20OR%20content_tags%3A\'futa\')%20AND%20(upcoming%3A\'0\')&highlightPostTag=__%2Fais-highlight__&highlightPreTag=__ais-highlight__&hitsPerPage=60&maxValuesPerFacet=1000&page=0&query=&tagFilters="},{"indexName":"all_scenes_latest_desc","params":"analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Amembers%22%2C%22site%3Aadulttime%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&clickAnalytics=false&facetFilters=%5B%5B%22network.lvl0%3AAdult%20Time%20Originals%22%5D%5D&facetingAfterDistinct=true&facets=%5B%22network.lvl0%22%2C%22network.lvl1%22%5D&filters=(content_tags%3A\'trans\'%20OR%20content_tags%3A\'straight\'%20OR%20content_tags%3A\'lesbian\'%20OR%20content_tags%3A\'gay\'%20OR%20content_tags%3A\'bisex\'%20OR%20content_tags%3A\'futa\')%20AND%20(upcoming%3A\'0\')&highlightPostTag=__%2Fais-highlight__&highlightPreTag=__ais-highlight__&hitsPerPage=0&maxValuesPerFacet=1000&page=0&query="},{"indexName":"all_scenes_latest_desc","params":"analytics=false&analyticsTags=%5B%22component%3Asearchlisting%22%2C%22section%3Amembers%22%2C%22site%3Aadulttime%22%2C%22context%3Avideos%22%2C%22device%3Adesktop%22%5D&clickAnalytics=false&facetingAfterDistinct=true&facets=%5B%22network.lvl0%22%5D&filters=(content_tags%3A\'trans\'%20OR%20content_tags%3A\'straight\'%20OR%20content_tags%3A\'lesbian\'%20OR%20content_tags%3A\'gay\'%20OR%20content_tags%3A\'bisex\'%20OR%20content_tags%3A\'futa\')%20AND%20(upcoming%3A\'0\')&highlightPostTag=__%2Fais-highlight__&highlightPreTag=__ais-highlight__&hitsPerPage=0&maxValuesPerFacet=1000&page=' + str(page) + '&query=&facetFilters=undefined"}]}'

        return scrapy.Request(
            url=algolia_url,
            method='post',
            body=jbody,
            meta={'token': token, 'page': page, 'url': referrer, 'sitelink': site, 'parsesite': parsesite},
            callback=self.parse,
            headers=headers
        )
