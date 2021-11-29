import json
from datetime import date, timedelta
from urllib.parse import urlparse
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class VixenScraper(BaseSceneScraper):
    name = 'Vixen'
    network = 'vixen'

    start_urls = [
        'https://www.vixen.com',
        'https://www.blacked.com',
        'https://www.tushy.com',
        'https://www.blackedraw.com',
        'https://www.tushyraw.com',
        'https://www.deeper.com',
        'https://www.slayed.com',
    ]

    sites = {
        'VIXEN': 'Vixen',
        'BLACKED': 'Blacked',
        'TUSHY': 'Tushy',
        'BLACKEDRAW': 'BlackedRaw',
        'TUSHYRAW': 'TushyRaw',
        'DEEPER': 'Deeper',
        'SLAYED': 'Slayed',
    }

    selector_map = {
        'external_id': '',
    }

    page = 0
    per_page = 200

    def start_requests(self):
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
        json = response.json()['data']['findVideos']
        scenes = json['edges']
        for item in scenes:
            id = item['node']['slug']
            yield scrapy.Request(
                url=response.url,
                callback=self.parse_scene,
                method='POST',
                headers={'Content-Type': 'application/json'},
                body=self.get_graphql_body(id, response.url),
            )

        if 'page' in response.meta and response.meta['page'] < self.limit_pages and json['pageInfo']['hasNextPage']:
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
        data = response.json()['data']['findOneVideo']

        scene = SceneItem()

        scene['id'] = data['id']
        scene['title'] = self.cleanup_title(data['title'])
        scene['description'] = self.cleanup_description(data['description']) if 'description' in data else ''

        site = data['site']
        if site.upper() in self.sites:
            site = self.sites[site.upper()]
        scene['site'] = site

        scene['network'] = 'Vixen'
        scene['parent'] = site
        scene['image_blob'] = None

        scene['date'] = self.parse_date(data['releaseDate']).isoformat()
        scene['url'] = self.format_link(response, '/videos/' + data['slug'])

        scene['performers'] = []
        for model in data['models']:
            scene['performers'].append(model['name'])

        scene['tags'] = []
        if data['tags']:
            for tag in data['tags']:
                scene['tags'].append(tag)

        largest = 0
        for image in data['images']['poster']:
            if image['width'] > largest:
                scene['image'] = image['src']
            largest = image['width']

        largest = 0
        for trailer in data['previews']['poster']:
            if trailer['width'] > largest:
                scene['trailer'] = trailer['src']
            largest = trailer['width']

        scene['trailer'] = '' if 'trailer' not in scene or not scene['trailer'] else scene['trailer']

        days = int(self.days)
        if days > 27375:
            filterdate = "0000-00-00"
        else:
            filterdate = date.today() - timedelta(days)
            filterdate = filterdate.strftime('%Y-%m-%d')

        if self.debug:
            if not scene['date'] > filterdate:
                scene['filtered'] = "Scene filtered due to date restraint"
            print(scene)
        else:
            if filterdate:
                if scene['date'] > filterdate:
                    yield scene
            else:
                yield scene

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

    def get_graphql_body(self, id, link):
        site_name = urlparse(link).hostname.replace('www.', '').replace('.com', '').upper()

        return json.dumps({
            'operationName': 'getVideo',
            'variables': {
                'videoSlug': id,
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
    tags
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
