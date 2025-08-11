import re
import datetime
import string
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteIWantClipsSpecificSpider(BaseSceneScraper):
    name = 'IWantClipsSpecific'
    network = 'I Want Clips'

    start_urls = [
        'https://iwantclips.com',
    ]

    cookies = {'accepted': '1', 'member_id': '0'}

    selector_map = {
        'external_id': '(\\d+)$',
        'pagination': '/?page=%s'
    }

    def start_requests(self):
        if not hasattr(self, 'start_urls'):
            raise AttributeError('start_urls missing')

        if not self.start_urls:
            raise AttributeError('start_urls selector missing')
        page = int(self.page) - 1

        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, page + 1), callback=self.parse_token, meta={'page': page, 'url': link}, cookies=self.cookies)

    def get_next_page_url(self, base, page):
        return f"https://iwantclips.com/store/1437281/Kim-and-Vivi?page={page}"

    def parse_token(self, response):
        # ~ match = re.search(r'searchClient.*?, \'(.*?)\'', response.text)
        # ~ token = match.group(1)
        token = "1"
        return self.call_algolia(response.meta['page'], token, response.meta['url'])

    def parse(self, response, **kwargs):
        if response.status == 200:
            scenes = self.get_scenes(response)
            count = 0
            for scene in scenes:
                count += 1
                yield scene

            if count:
                if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                    next_page = response.meta['page'] + 1
                    yield self.call_algolia(next_page, response.meta['token'], response.meta['url'])

    def get_scenes(self, response):
        # ~ print(response.json())
        for scene in response.json()['results'][0]['hits']:
            scene = scene['document']
            item = SceneItem()
            item['image'] = scene['thumbnail_url']
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            if 'preview_mp4_url' in scene:
                item['trailer'] = scene['preview_mp4_url']
                if "https" not in item['trailer'].lower():
                    item['trailer'] = None
            else:
                item['trailer'] = None
            item['id'] = scene['content_id']
            item['title'] = string.capwords(scene['title'])
            item['description'] = scene['description']

            if scene['publish_date']:
                item['date'] = datetime.datetime.utcfromtimestamp(scene['publish_date']).isoformat()
                # ~ print(f"Datetime: {scene['publish_date']}     Parsed_date: {item['date']}")
            else:
                print("Date not provided, using today")
                item['date'] = self.parse_date('today').isoformat()
            item['performers'] = [scene['model_username']]
            if " and " in scene['model_username'].lower():
                item['performers'] = scene['model_username'].lower().split(" and ")
            if " & " in scene['model_username'].lower():
                item['performers'] = scene['model_username'].lower().split(" & ")

            item['performers'] = list(map(lambda x: string.capwords(x.strip()), item['performers']))

            if len(item['performers']) > 1:
                item['performers'] = [f"{performer} ({scene['member_id']})" for performer in item['performers']]

            item['tags'] = scene['categories'] + scene['keywords']
            item['tags'] = [i for i in item['tags'] if i]

            item['site'] = "I Want Clips"
            item['parent'] = "I Want Clips"
            item['network'] = "I Want Clips"
            item['url'] = scene['content_url']

            yield self.check_item(item, self.days)

    def call_algolia(self, page, token, referrer):
        # ~ print (f'Page: {page}        Token: {token}     Referrer: {referrer}')
        # ~ algolia_url = 'https://tsmkfa364q-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia for vanilla JavaScript 3.27.1;JS Helper 2.26.0&x-algolia-application-id=TSMKFA364Q&x-algolia-api-key=%s' % token
        # ~ algolia_url = 'https://n95emuhkii-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(3.33.0)%3B%20Browser%20(lite)%3B%20instantsearch.js%20(3.4.0)%3B%20JS%20Helper%202.26.1&x-algolia-application-id=N95EMUHKII&x-algolia-api-key=' + token
        # ~ algolia_url = 'https://n95emuhkii-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(3.33.0)%3B%20Browser%20(lite)%3B%20instantsearch.js%20(3.4.0)%3B%20JS%20Helper%202.26.1&x-algolia-application-id=N95EMUHKII&x-algolia-api-key=' + token
        # ~ algolia_url = 'https://bajc2td3pou5fs7mp.a1.typesense.net/multi_search?x-typesense-api-key=M0hkQ2FVZGVNM3NQS0lQdjZVYWkzTUlxaHhNbUFhT1g1bU4zU3BydktkND1KcGRYeyJleGNsdWRlX2ZpZWxkcyI6ImJsb2NrZWRfY291bnRyeSxibG9ja2VkX3VzZXJzLGJsb2NrZWRfcmVnaW9uLGJsb2NrZWRfY2l0eSxibG9ja2VkX3Bvc3RhbCIsImZpbHRlcl9ieSI6InByaWNlOj4wICYmIG1lbWJlcl9pZDo9MTYyNTE5MyAmJiBibG9ja2VkX3VzZXJzOiE9MCAmJiBibG9ja2VkX2NvdW50cnk6IT0zOCAmJiBibG9ja2VkX3JlZ2lvbjohPTY3MSAmJiBibG9ja2VkX2NpdHk6IT0xMDUxOSAmJiBibG9ja2VkX3Bvc3RhbDohPTEwNTE5ICYmIG51ZGl0eTo9Tm9uLU51ZGUiLCJleHBpcmVzX2F0IjoxNzM4Nzk1ODUwfQ%3D%3D'
        # ~ algolia_url = 'https://bajc2td3pou5fs7mp.a1.typesense.net/multi_search?x-typesense-api-key=b1lRVVdJVHJTSU8vaFgzOXh6QVIxMWtSSDNtVzhyOHZIY1Y2YjNJMWlybz1KcGRYeyJleGNsdWRlX2ZpZWxkcyI6ImJsb2NrZWRfY291bnRyeSxibG9ja2VkX3VzZXJzLGJsb2NrZWRfcmVnaW9uLGJsb2NrZWRfY2l0eSxibG9ja2VkX3Bvc3RhbCIsImZpbHRlcl9ieSI6InByaWNlOj4wICYmIG1lbWJlcl9pZDo9NjI3MDc3ICYmIGJsb2NrZWRfdXNlcnM6IT0wICYmIGJsb2NrZWRfY291bnRyeTohPTM4ICYmIGJsb2NrZWRfcmVnaW9uOiE9NjcxICYmIGJsb2NrZWRfY2l0eTohPTEwNTE5ICYmIGJsb2NrZWRfcG9zdGFsOiE9MTA1MTkgJiYgbnVkaXR5Oj1Ob24tTnVkZSIsImV4cGlyZXNfYXQiOjE3NDQ1MjA4NjB9'
        # ~ algolia_url = 'https://bajc2td3pou5fs7mp.a1.typesense.net/multi_search?x-typesense-api-key=VnkzNW5qWk8wYTNlTHFOQ1hzZE13TzJFQUVWcllFN3drZ2hOL2M0bHJDaz1KcGRYeyJleGNsdWRlX2ZpZWxkcyI6ImJsb2NrZWRfY291bnRyeSxibG9ja2VkX3VzZXJzLGJsb2NrZWRfcmVnaW9uLGJsb2NrZWRfY2l0eSxibG9ja2VkX3Bvc3RhbCIsImZpbHRlcl9ieSI6InByaWNlOj4wICYmIG1lbWJlcl9pZDo9OTc0ODA2ICYmIGJsb2NrZWRfdXNlcnM6IT0wICYmIGJsb2NrZWRfY291bnRyeTohPTM4ICYmIGJsb2NrZWRfcmVnaW9uOiE9NjcxICYmIGJsb2NrZWRfY2l0eTohPTEwNTE5ICYmIGJsb2NrZWRfcG9zdGFsOiE9MTA1MTkiLCJleHBpcmVzX2F0IjoxNzQ1MTU4OTg1fQ%3D%3D'
        algolia_url = 'https://bajc2td3pou5fs7mp.a1.typesense.net/multi_search?x-typesense-api-key=UDJKYnMyTjVhWXR0SEUweUoxdndrMlI2a3VkeWxRelBrL2dBUU9XSndOdz1KcGRYeyJleGNsdWRlX2ZpZWxkcyI6ImJsb2NrZWRfY291bnRyeSxibG9ja2VkX3VzZXJzLGJsb2NrZWRfcmVnaW9uLGJsb2NrZWRfY2l0eSxibG9ja2VkX3Bvc3RhbCIsImZpbHRlcl9ieSI6InByaWNlOj4wICYmIHByaWNlOjwxMDAwMSAmJiAgYmxvY2tlZF91c2VyczohPTAgJiYgIGJsb2NrZWRfY291bnRyeTohPTM4ICAmJiAgYmxvY2tlZF9yZWdpb246IT02NzEgICYmICBibG9ja2VkX2NpdHk6IT0xMDUxOSAgJiYgIGJsb2NrZWRfcG9zdGFsOiE9MTA1MTkgIiwiZXhwaXJlc19hdCI6MTc0ODcxNjczM30%3D'

        headers = {
            'Content-Type': 'application/json',
            'Referer': self.get_next_page_url(referrer, page)
        }
        # ~ jbody = '{"requests":[{"indexName":"prod_main_page","params":"query=&page=' + str(page) + '&highlightPreTag=__ais-highlight__&highlightPostTag=__%2Fais-highlight__&clickAnalytics=true&facets=%5B%5D&tagFilters="}]}'
        # ~ jbody = '{"requests":[{"indexName":"v1_artist_page","params":"query=&maxValuesPerFacet=1000&page=' + str(page) + '&highlightPreTag=__ais-highlight__&highlightPostTag=__%2Fais-highlight__&clickAnalytics=true&facets=%5B%22categories%22%2C%22categories%22%2C%22categories%22%2C%22categories%22%5D&tagFilters="}]}'
        # ~ jbody = '{"searches":[{"sort_by":"publish_time:desc,popularity:desc","query_by":"title,description,member_id,model_username,categories,price_range,nudity,keywords,viewable_by,aa_ai,aa_body-shape,aa_body-type,aa_breast-size,aa_butt-size,aa_butt-type,aa_eye-color,aa_foot-size,aa_glasses,aa_hair-color,aa_hair-length,aa_height,aa_piercings,aa_pubic-hair,aa_tattoos,aa_origin-country,aa_race,aa_age,aa_circumcised,aa_endowment,aa_ethnicity,aa_girth,aa_language,aa_nose,aa_qwe,aa_wake,aa_wake-attributes,aa_abs","highlight_full_fields":"title,description,member_id,model_username,categories,price_range,nudity,keywords,viewable_by,aa_ai,aa_body-shape,aa_body-type,aa_breast-size,aa_butt-size,aa_butt-type,aa_eye-color,aa_foot-size,aa_glasses,aa_hair-color,aa_hair-length,aa_height,aa_piercings,aa_pubic-hair,aa_tattoos,aa_origin-country,aa_race,aa_age,aa_circumcised,aa_endowment,aa_ethnicity,aa_girth,aa_language,aa_nose,aa_qwe,aa_wake,aa_wake-attributes,aa_abs","collection":"prod_content","q":"*","facet_by":"type,categories,type,categories","filter_by":"member_id:1625193","max_facet_values":1000,"page":' + str(page) + ',"per_page":26}]}'
        # ~ jbody = '{"searches":[{"sort_by":"publish_time:desc,popularity:desc","query_by":"title,description,member_id,model_username,categories,price_range,nudity,keywords,viewable_by,aa_ai,aa_body-shape,aa_body-type,aa_breast-size,aa_butt-size,aa_butt-type,aa_eye-color,aa_foot-size,aa_glasses,aa_hair-color,aa_hair-length,aa_height,aa_piercings,aa_pubic-hair,aa_tattoos,aa_origin-country,aa_race,aa_age,aa_circumcised,aa_endowment,aa_ethnicity,aa_girth,aa_language,aa_nose,aa_qwe,aa_wake,aa_wake-attributes,aa_abs","highlight_full_fields":"title,description,member_id,model_username,categories,price_range,nudity,keywords,viewable_by,aa_ai,aa_body-shape,aa_body-type,aa_breast-size,aa_butt-size,aa_butt-type,aa_eye-color,aa_foot-size,aa_glasses,aa_hair-color,aa_hair-length,aa_height,aa_piercings,aa_pubic-hair,aa_tattoos,aa_origin-country,aa_race,aa_age,aa_circumcised,aa_endowment,aa_ethnicity,aa_girth,aa_language,aa_nose,aa_qwe,aa_wake,aa_wake-attributes,aa_abs","collection":"prod_content","q":"*","facet_by":"type,categories,type,categories","filter_by":"member_id:627077","max_facet_values":1000,"page":' + str(page) + ',"per_page":26}]}'
        # ~ jbody = '{"searches":[{"sort_by":"publish_time:desc,popularity:desc","query_by":"title,description,member_id,model_username,categories,price_range,nudity,keywords,viewable_by,aa_ai,aa_body-shape,aa_body-type,aa_breast-size,aa_butt-size,aa_butt-type,aa_eye-color,aa_foot-size,aa_glasses,aa_hair-color,aa_hair-length,aa_height,aa_piercings,aa_pubic-hair,aa_tattoos,aa_origin-country,aa_race,aa_age,aa_circumcised,aa_endowment,aa_ethnicity,aa_girth,aa_language,aa_nose,aa_qwe,aa_wake,aa_wake-attributes,aa_abs","highlight_full_fields":"title,description,member_id,model_username,categories,price_range,nudity,keywords,viewable_by,aa_ai,aa_body-shape,aa_body-type,aa_breast-size,aa_butt-size,aa_butt-type,aa_eye-color,aa_foot-size,aa_glasses,aa_hair-color,aa_hair-length,aa_height,aa_piercings,aa_pubic-hair,aa_tattoos,aa_origin-country,aa_race,aa_age,aa_circumcised,aa_endowment,aa_ethnicity,aa_girth,aa_language,aa_nose,aa_qwe,aa_wake,aa_wake-attributes,aa_abs","collection":"prod_content","q":"*","facet_by":"type,categories,type,categories","filter_by":"member_id:974806","max_facet_values":1000,"page":' + str(page) + ',"per_page":27}]}'
        jbody = '{"searches":[{"sort_by":"publish_time:desc,popularity:desc","query_by":"title,description,member_id,model_username,categories,price_range,nudity,keywords,viewable_by,aa_ai,aa_body-shape,aa_body-type,aa_breast-size,aa_butt-size,aa_butt-type,aa_eye-color,aa_foot-size,aa_glasses,aa_hair-color,aa_hair-length,aa_height,aa_piercings,aa_pubic-hair,aa_tattoos,aa_origin-country,aa_race,aa_age,aa_circumcised,aa_endowment,aa_ethnicity,aa_girth,aa_language,aa_nose,aa_qwe,aa_wake,aa_wake-attributes,aa_abs","highlight_full_fields":"title,description,member_id,model_username,categories,price_range,nudity,keywords,viewable_by,aa_ai,aa_body-shape,aa_body-type,aa_breast-size,aa_butt-size,aa_butt-type,aa_eye-color,aa_foot-size,aa_glasses,aa_hair-color,aa_hair-length,aa_height,aa_piercings,aa_pubic-hair,aa_tattoos,aa_origin-country,aa_race,aa_age,aa_circumcised,aa_endowment,aa_ethnicity,aa_girth,aa_language,aa_nose,aa_qwe,aa_wake,aa_wake-attributes,aa_abs","collection":"prod_content","q":"*","facet_by":"type,categories,type,categories","filter_by":"member_id:1437281","max_facet_values":1000,"page":' + str(page) + ',"per_page":36}]}'

        return scrapy.Request(
            url=algolia_url,
            method='post',
            body=jbody,
            meta={'token': token, 'page': page, 'url': referrer},
            callback=self.parse,
            headers=headers
        )
