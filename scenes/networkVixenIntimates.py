import re
import json
import string
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class VixenIntimatesScraper(BaseSceneScraper):
    name = 'VixenIntimates'
    network = 'vixen'

    start_urls = [
        'https://www.vixen.com',
    ]

    sites = {
        'VIXEN': 'Vixen',
        'Intimates': 'Vixen Intimates',
        'Behind The Scenes': 'Vixen Behind the Scenes',
        'Compilations': 'Vixen Compilations'
    }

    slugs = ["intimates", "behind-the-scenes", "compilations"]
    # ~ slugs = ["behind-the-scenes"]

    selector_map = {
        'external_id': '',
    }

    page = 0
    per_page = 12

    def start_requests(self):
        meta = {}
        meta['page'] = self.page
        link = 'https://www.vixen.com/graphql'
        for channel in self.slugs:
            meta['slug'] = channel
            yield scrapy.Request(link, callback=self.parse, method='POST', headers={'Content-Type': 'application/json'}, meta=meta, body=self.get_graphql_search_body(self.per_page, self.page, link, meta['slug']))

    def parse(self, response, **kwargs):
        meta = response.meta
        jsondata = response.json()['data']['findOneChannel']['videos']
        scenes = jsondata['edges']
        for item in scenes:
            sceneid = item['node']['videoSlug']
            yield scrapy.Request(url=response.url, callback=self.parse_scene, method='POST', headers={'Content-Type': 'application/json'}, body=self.get_graphql_body(sceneid, response.url), meta=meta)

        if 'page' in response.meta and response.meta['page'] < self.limit_pages:
            meta['page'] = meta['page'] + 1

            print('NEXT PAGE: ' + str(meta['page']))
            yield scrapy.Request(url=response.url, callback=self.parse, method='POST', headers={'Content-Type': 'application/json'}, meta=meta, body=self.get_graphql_search_body(self.per_page, meta['page'], response.url, meta['slug']))

    def parse_scene(self, response):
        meta = response.meta
        data = response.json()['data']['findOneVideo']
        scene = SceneItem()

        # ~ try:
        scene['id'] = re.search(r'\:(.*)', data['id']).group(1)

        scene['title'] = self.cleanup_title(data['title'])
        scene['description'] = self.cleanup_description(data['description']) if 'description' in data else ''

        site = data['channel']['name']
        if site in self.sites:
            site = self.sites[site]
        scene['site'] = site

        scene['network'] = 'Vixen'
        scene['parent'] = 'Vixen'

        scene['date'] = self.parse_date(data['releaseDate']).isoformat()
        slug = re.search(r'\:(.*)', data['id']).group(1)
        scene['url'] = f"https://members.vixen.com/channels/{meta['slug']}/videos/{slug}"

        scene['performers'] = []
        for model in data['modelsSlugged']:
            scene['performers'].append(string.capwords(model['name']))

        scene['tags'] = []
        if data['tags']:
            for tag in data['tags']:
                scene['tags'].append(tag)

        scene['duration'] = self.duration_to_seconds(data['runLengthFormatted'])

        scene['markers'] = []
        if 'chapters' in data:
            if data['chapters']:
                for timetag in data['chapters']['video']:
                    timestamp = {}
                    timestamp['name'] = self.cleanup_title(timetag['title'])
                    timestamp['start'] = str(timetag['seconds'])
                    scene['markers'].append(timestamp)
                    scene['tags'].append(timestamp['name'])

        scene['tags'] = list(map(lambda x: string.capwords(x.strip()), list(set(scene['tags']))))

        largest = 0
        for image in data['images']['poster']:
            if image['width'] > largest:
                scene['image'] = image['src']
            largest = image['width']

        largest = 0
        scene['image_blob'] = self.get_image_blob_from_link(scene['image'])
        scene['image'] = re.search(r'(.*?)\?', scene['image']).group(1)

        scene['trailer'] = ''

        yield self.check_item(scene, self.days)

    def get_graphql_search_body(self, per_page, page, link, channelslug):
        return json.dumps({
            'operationName': 'getChannelInfo',
            'variables': {
                'channelSlug': channelslug,
                'sortField': "releaseDate",
                'sortOrderDesc': True,
                'skip': per_page * page
            },
            'query': self.get_grapgql_search_query(),
        })

    def get_grapgql_search_query(self):
        return '''
query getChannelInfo($channelSlug: String, $channelPackSlug: String, $sortField: String!, $skip: Int!, $sortOrderDesc: Boolean!) {
  findOneChannel(
    input: {slug: $channelSlug, channelPackSlug: $channelPackSlug, site: CHANNELS}
  ) {
    name
    slug
    channelId
    isNewContentBadgeEnabled
    description
    packs {
      channelPackId
      channelPackName
      channelPackSlug
      __typename
    }
    isThirdPartyChannel
    url
    images {
      header {
        src
        placeholder
        height
        width
        highdpi {
          double
          triple
          __typename
        }
        __typename
      }
      logo {
        src
        placeholder
        height
        width
        highdpi {
          double
          triple
          __typename
        }
        __typename
      }
      __typename
    }
    videos(
      input: {site: CHANNELS, first: 12, skip: $skip, channelPackSlug: $channelPackSlug, order: {desc: $sortOrderDesc, field: $sortField}}
    ) {
      edges {
        node {
          uuid
          videoId
          id: uuid
          title
          videoSlug: slug
          rating
          expertReview {
            global
            __typename
          }
          releaseDate
          isExclusive
          channel {
            isThirdPartyChannel
            channelId
            channelPackId
            channelPackName
            name
            slug
            url
            __typename
          }
          modelsSlugged: models {
            name
            __typename
          }
          previews {
            listing {
              src
              width
              height
              type
              name
              __typename
            }
            __typename
          }
          images {
            listing {
              src
              placeholder
              height
              width
              highdpi {
                double
                triple
                __typename
              }
              fileExtensions
              name
              __typename
            }
            __typename
          }
          __typename
        }
        cursor
        __typename
      }
      totalCount
      __typename
    }
    __typename
  }
}
'''

    def get_graphql_body(self, sceneid, link):
        return json.dumps({
            'operationName': 'getChannelVideo',
            'variables': {
                'videoSlug': sceneid,
            },
            'query': self.get_grapgql_query(),
        })

    def get_grapgql_query(self):
        return '''
query getChannelVideo($videoSlug: String) {
  findOneVideo(input: {slug: $videoSlug, site: CHANNELS}) {
    channel {
      channelId
      channelPackId
      channelPackName
      isThirdPartyChannel
      __typename
    }
    newId: videoId
    videoId
    id: uuid
    title
    description
    descriptionHtml
    modelsSlugged: models {
      name
      __typename
    }
    rating
    expertReview {
      global
      __typename
    }
    runLengthFormatted: runLength
    releaseDate
    videoUrl1080P: videoTokenId
    trailerTokenId
    picturesInSet
    images {
      poster {
        src
        placeholder
        width
        height
        highdpi {
          double
          triple
          __typename
        }
        name
        __typename
      }
      __typename
    }
    tags
    channel {
      channelId
      isThirdPartyChannel
      name
      slug
      url
      __typename
    }
    downloadResolutions {
      label
      size
      width
      res
      __typename
    }
    related(count: 2) {
      title
      id: uuid
      videoId
      slug
      modelsSlugged: models {
        name
        __typename
      }
      releaseDate
      rating
      expertReview {
        global
        __typename
      }
      channel {
        channelId
        isThirdPartyChannel
        channelPackId
        channelPackName
        __typename
      }
      images {
        listing {
          src
          width
          height
          name
          __typename
        }
        __typename
      }
      previews {
        listing {
          src
          width
          height
          type
          name
          __typename
        }
        __typename
      }
      __typename
    }
    userVideoReview {
      slug
      rating
      __typename
    }
    __typename
  }
}
'''
