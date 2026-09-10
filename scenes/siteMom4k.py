import json

from tpdb.BaseSceneScraper import BaseSceneScraper


def unflatten(flat, index=0, seen=None):
    """Resolve Nuxt's devalue-flattened payload into ordinary Python objects.

    The array holds every distinct value once; any integer inside a container is
    an index back into that array, and negative indices are the JS constants.
    """
    if seen is None:
        seen = {}
    if isinstance(index, int) and index < 0:
        return {-3: float('nan'), -4: float('inf'), -5: float('-inf'), -6: -0.0}.get(index)
    if index in seen:
        return seen[index]
    node = flat[index]
    if isinstance(node, list):
        if node and node[0] in ('Reactive', 'ShallowReactive', 'Ref', 'ShallowRef', 'EmptyRef', 'EmptyShallowRef'):
            return unflatten(flat, node[1], seen)
        out = []
        seen[index] = out
        for entry in node:
            out.append(unflatten(flat, entry, seen) if isinstance(entry, int) else entry)
        return out
    if isinstance(node, dict):
        out = {}
        seen[index] = out
        for key, value in node.items():
            out[key] = unflatten(flat, value, seen) if isinstance(value, int) else value
        return out
    seen[index] = node
    return node


class SiteMom4kSpider(BaseSceneScraper):
    name = 'Mom4k'
    network = 'Mom4k'
    parent = 'Mom4k'
    site = 'Mom4k'

    start_urls = [
        'https://mom4k.com',
    ]

    # The tour is a client-rendered Nuxt app, so nothing matches an XPath against
    # the served markup any more.  The server-side render still ships the whole
    # release list in the __NUXT_DATA__ script tag, which carries more than the
    # old scene pages did (cast with genders, tags, trailer, poster), so the
    # listing alone is scraped and no scene request is made.
    selector_map = {
        'external_id': r'/video/(.*)',
        'pagination': '/?page=%s',
        'type': 'Scene',
    }

    def get_releases(self, response):
        payload = response.xpath('//script[@id="__NUXT_DATA__"]/text()').get()
        if not payload:
            return []
        data = unflatten(json.loads(payload))
        releases = data.get('data', {}).get('tourMainPageData', {}).get('latestReleases', {})
        return releases.get('items') or []

    def get_scenes(self, response):
        for release in self.get_releases(response):
            item = self.init_scene()

            item['title'] = release.get('title') or ''
            item['description'] = self.cleanup_description(release.get('description') or '')
            item['id'] = str(release.get('releaseId') or release.get('id') or '')
            item['url'] = '%s/video/%s' % (self.start_urls[0], release.get('cachedSlug') or '')

            item['date'] = ''
            if release.get('releasedAt'):
                item['date'] = self.parse_date(release['releasedAt'].split("T")[0], date_formats=['%Y-%m-%d']).isoformat()

            item['image'] = release.get('posterUrl') or release.get('thumbUrl') or ''
            item['image_blob'] = self.get_image_blob_from_link(item['image']) if item['image'] else ''
            item['trailer'] = release.get('trailerUrl') or ''

            item['performers'] = [actor['name'] for actor in release.get('actors') or [] if actor.get('name')]
            item['performers_data'] = self.get_performers_data(release)
            item['tags'] = [tag.replace("_", " ").title() for tag in release.get('tags') or []]

            item['site'] = self.site
            item['parent'] = self.parent
            item['network'] = self.network
            item['type'] = 'Scene'

            if item['title'] and item['id']:
                yield self.check_item(item, self.days)

    def get_performers_data(self, release):
        genders = {'girl': 'Female', 'guy': 'Male', 'trans': 'Trans'}
        performers_data = []
        for actor in release.get('actors') or []:
            if not actor.get('name'):
                continue
            performer = {'name': actor['name'], 'network': self.network, 'site': self.site, 'extra': {}}
            if actor.get('gender') in genders:
                performer['extra']['gender'] = genders[actor['gender']]
            performers_data.append(performer)
        return performers_data
