import json
from requests import get
import string
from urllib.parse import urlparse
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class VixenScraper(BaseSceneScraper):
    name = 'Vixen'
    network = 'vixen'

    custom_settings = {
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_impersonate.ImpersonateDownloadHandler",
            "https": "scrapy_impersonate.ImpersonateDownloadHandler",
        },
    }

    start_urls = [
        'https://www.vixen.com',
        'https://www.blacked.com',
        'https://www.tushy.com',
        'https://www.blackedraw.com',
        'https://www.tushyraw.com',
        'https://www.deeper.com',
        'https://www.milfy.com',
        'https://www.slayed.com',
        'https://www.wifey.com',
    ]

    headers = {
        "Accept-Encoding": "gzip, deflate",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "DNT": "1",
    }        

    sites = {
        'VIXEN': 'Vixen',
        'BLACKED': 'Blacked',
        'TUSHY': 'Tushy',
        'BLACKEDRAW': 'BlackedRaw',
        'TUSHYRAW': 'TushyRaw',
        'DEEPER': 'Deeper',
        'SLAYED': 'Slayed',
        'MILFY': 'Milfy',
        'WIFEY': 'Wifey',
    }

    selector_map = {
        'external_id': '',
    }

    page = 0
    per_page = 200

    async def start(self):
        ip = get('https://api.ipify.org').content.decode('utf8')
        print('My public IP address is: {}'.format(ip))
        for link in self.start_urls:

          headers = self.headers.copy()
          headers['Referer'] = link
          yield scrapy.Request(
              url=link + '/graphql',
              callback=self.parse,
              method='POST',
              headers=headers,
              meta={'page': self.page, 'link': link, 'impersonate': 'chrome120'},
              body=self.get_graphql_search_body(self.per_page, self.page, link),
          )

    def parse(self, response, **kwargs):
        jsondata = response.json()['data']['findVideos']
        scenes = jsondata['edges']
        headers = self.headers.copy()
        headers['Referer'] = response.meta['link']
        for item in scenes:
            sceneid = item['node']['slug']
            scene = self.init_scene()
            scene['date'] = self.parse_date(item['node']['releaseDate']).strftime('%Y-%m-%d')
            if self.check_item(scene, self.days):

              body = self.get_graphql_body(sceneid, response.url)
              yield scrapy.Request(
                  url=response.url,
                  callback=self.parse_scene,
                  method='POST',
                  headers=headers,
                  meta={'impersonate': 'chrome120'},
                  body=body,
              )

        if 'page' in response.meta and response.meta['page'] < self.limit_pages and jsondata['pageInfo']['hasNextPage']:
            meta = self.copy_meta(response)
            meta['page'] = meta['page'] + 1

            print('NEXT PAGE: ' + str(meta['page']))
            yield scrapy.Request(
                url=response.url,
                callback=self.parse,
                method='POST',
                headers = headers,
                meta=meta,
                body=self.get_graphql_search_body(self.per_page, meta['page'], response.url),
            )

    def parse_scene(self, response):
        data = response.json()['data']['findOneVideo']
        scene = self.init_scene()

        # ~ try:
        scene['id'] = data['id']

        scene['title'] = self.cleanup_title(data['title'])
        scene['description'] = self.cleanup_description(data['description']) if 'description' in data else ''

        site = data['site']
        if site.upper() in self.sites:
            site = self.sites[site.upper()]
        scene['site'] = site

        if "runLength" in data and data['runLength']:
            scene['duration'] = self.duration_to_seconds(data['runLength'])

        scene['network'] = 'Vixen'
        scene['parent'] = site

        scene['date'] = self.parse_date(data['releaseDate']).strftime('%Y-%m-%d')
        if self.check_item(scene, self.days):
          scene['url'] = self.format_link(response, '/videos/' + data['slug'])

          if "directors" in data and len(data['directors']):
              scene['director'] = data['directors'][0]['name']

          scene['performers'] = []
          for model in data['models']:
              scene['performers'].append(model['name'])

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

          scene['trailer'] = ''

          yield self.check_item(scene, self.days)

        # ~ except Exception:
            # ~ print(f"Failed Request on: {response.url}")

    def get_graphql_search_body(self, per_page, page, link):
        site_name = urlparse(link).hostname.replace('www.', '').replace('.com', '').upper()

        return json.dumps({
            'operationName': 'getFilteredVideos',
            'variables': {
                'site': site_name,
                'skip': per_page * page,
                'first': per_page,
                'order': {
                    'field': 'releaseDate',
                    'desc': True,
                },
                'filter': [],
            },
            'query': self.get_grapgql_search_query(),
        })

    def get_grapgql_search_query(self):
        return '''
query getFilteredVideos(
  $order: ListOrderInput!
  $filter: [ListFilterInput!]
  $site: Site!
  $first: Int!
  $skip: Int!
) {
  findVideos(
    input: {
      filter: $filter
      order: $order
      first: $first
      skip: $skip
      site: $site
    }
  ) {
    edges {
      node {
        id: uuid
        videoId
        slug
        releaseDate
      }
    }
    pageInfo {
      hasNextPage
      hasPreviousPage
    }
    totalCount
  }
}
'''

    def get_graphql_body(self, sceneid, link):
        site_name = urlparse(link).hostname.replace('www.', '').replace('.com', '').upper()

        return json.dumps({
            'operationName': 'getVideo',
            'variables': {
                'videoSlug': sceneid,
                'site': site_name
            },
            'query': self.get_grapgql_query(),
        })

    def get_grapgql_query(self):
        return '''
query getVideo($videoSlug: String, $site: Site) {
  findOneVideo(input: { slug: $videoSlug, site: $site }) {
    id: uuid
    videoId
    slug
    title
    site
    description
    releaseDate
    runLength
    chapters {
      video {
        title
        seconds
      }
    }
    directors {
      name
    }
    models {
      name
      slug
    }
    previews {
      poster {
        ...PreviewInfo
      }
    }
    images {
      poster {
        ...ImageInfo
      }
    }
  }
}
fragment ImageInfo on Image {
  src
  placeholder
  width
  height
  highdpi {
    double
    triple
  }
}

fragment PreviewInfo on Preview {
  src
  width
  height
  type
}

'''
