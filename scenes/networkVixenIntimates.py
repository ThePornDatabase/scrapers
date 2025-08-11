import json
import re
from requests import get
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem
false = False
true = True


class VixenIntimatesScraper(BaseSceneScraper):
    name = 'VixenIntimates'
    network = 'vixen'

    start_urls = [
        'https://www.vixen.com',
    ]

    selector_map = {
        'external_id': '',
    }

    page = 0
    per_page = 50

    def start_requests(self):
        ip = get('https://api.ipify.org').content.decode('utf8')
        print('My public IP address is: {}'.format(ip))
        for link in self.start_urls:
            yield scrapy.Request(
                url=link + '/graphql',
                callback=self.parse,
                method='POST',
                headers={'Content-Type': 'application/json'},
                meta={'page': self.page},
                body=self.get_graphql_search_body(self.per_page, self.page, link),
            )

    def parse(self, response, **kwargs):
        meta = response.meta
        jsondata = response.json()['data']['findVideos']
        scenes = jsondata['edges']
        for item in scenes:
            sceneid = item['node']['slug']
            meta['orig_site'] = "vixen" + re.sub(r'[^a-z]+', '', item['node']['channel']['name'].lower())
            if meta['orig_site'].lower() in ["vixencompilations", "vixenbehindthescenes", "vixenintimates"]:
                yield scrapy.Request(
                    url=response.url,
                    callback=self.parse_scene,
                    method='POST',
                    headers={'Content-Type': 'application/json'},
                    body=self.get_graphql_body(sceneid, response.url), meta=meta
                )

        if 'page' in response.meta and response.meta['page'] < self.limit_pages and jsondata['pageInfo']['hasNextPage']:
            meta = response.meta
            meta['page'] = meta['page'] + 1

            print('NEXT PAGE: ' + str(meta['page']))
            yield scrapy.Request(
                url=response.url,
                callback=self.parse,
                method='POST',
                headers={'Content-Type': 'application/json'},
                meta={'page': meta['page']},
                body=self.get_graphql_search_body(self.per_page, meta['page'], response.url),
            )

    def parse_scene(self, response):
        meta = response.meta
        data = response.json()['data']['findOneVideo']
        scene = SceneItem()

        scene['id'] = data['id'].replace("channels:", "")

        scene['title'] = self.cleanup_title(data['title'])
        scene['description'] = self.cleanup_description(data['description']) if 'description' in data else ''

        scene['site'] = meta['orig_site']

        scene['network'] = 'Vixen'
        scene['parent'] = 'Vixen'

        scene['date'] = self.parse_date(data['releaseDate']).isoformat()
        scene['url'] = self.format_link(response, '/videos/' + data['slug'])

        if "directors" in data and len(data['directors']):
            scene['director'] = data['directors'][0]['name']

        scene['performers'] = []
        for model in data['models']:
            scene['performers'].append(model['name'])

        scene['tags'] = []
        if data['tags']:
            for tag in data['tags']:
                scene['tags'].append(tag)

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

    def get_graphql_search_body(self, per_page, page, link):
        query = json.dumps({
            'operationName': 'getFilteredVideos',
            'variables': {
                'site': "CHANNELS",
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
        return query

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
        channel {
          name
        }
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
        query = json.dumps({
            'operationName': 'getVideo',
            'variables': {
                'videoSlug': sceneid,
                'site': "CHANNELS"
            },
            'query': self.get_grapgql_query(),
        })
        return query

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
    tags
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
