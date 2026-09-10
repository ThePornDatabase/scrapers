import html
import json
import re

import scrapy
import unidecode

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteCustomFetishVideosSpider(BaseSceneScraper):
    name = 'CustomFetishVideos'
    site = 'Custom Fetish Videos'
    parent = 'Anatomik Media'
    network = 'Gamma Enterprises'

    start_urls = [
        'https://customfetishvideos.com',
    ]

    # The WooCommerce Store API the old spider read (/wp-json/wc/store/v1/products)
    # now answers 500 with "There has been a critical error on this website", and on
    # the scene pages the span "Models:" / "Fetish:" blocks and div.video_slide are
    # all gone.  The plain WordPress REST product endpoint still works and carries
    # everything: title, release date, synopsis, still, and both taxonomies --
    # product_tag holds the cast and product_cat the fetish list.
    selector_map = {
        'external_id': r'',
        'pagination': '/wp-json/wp/v2/product?per_page=20&_embed=1&orderby=date&order=desc&page=%s',
        'type': 'Scene',
    }

    # a section marker rather than a fetish
    NON_TAG_CATEGORIES = {'anatomik media features'}

    def get_scenes(self, response):
        try:
            products = json.loads(response.text)
        except ValueError:
            return
        if not isinstance(products, list):
            return

        for product in products:
            item = SceneItem()

            title = (product.get('title') or {}).get('rendered') or ''
            item['title'] = self.cleanup_title(unidecode.unidecode(html.unescape(title)))
            if not item['title']:
                continue

            item['id'] = str(product.get('id') or '')
            item['url'] = (product.get('link') or '').strip()

            scenedate = re.search(r'(\d{4}-\d{2}-\d{2})', product.get('date') or '')
            item['date'] = scenedate.group(1) if scenedate else None

            excerpt = (product.get('excerpt') or {}).get('rendered') or ''
            if not excerpt:
                excerpt = (product.get('content') or {}).get('rendered') or ''
            item['description'] = self.cleanup_description(
                unidecode.unidecode(html.unescape(re.sub(r'<[^<]+?>', ' ', excerpt))))

            embedded = product.get('_embedded') or {}
            media = (embedded.get('wp:featuredmedia') or [{}])[0]
            image = (media.get('source_url') or '').strip()
            item['image'] = image
            item['image_blob'] = self.get_image_blob_from_link(image) if image else None

            performers, tags = [], []
            for group in embedded.get('wp:term') or []:
                for term in group:
                    name = (term.get('name') or '').strip()
                    if not name:
                        continue
                    if term.get('taxonomy') == 'product_tag':
                        performers.append(name)
                    elif term.get('taxonomy') == 'product_cat':
                        if name.lower() not in self.NON_TAG_CATEGORIES:
                            tags.append(name)
            item['performers'] = list(dict.fromkeys(performers))
            item['tags'] = list(dict.fromkeys(tags))

            # The only trailers left are pre-signed Wasabi S3 URLs that expire within
            # hours, so there is nothing worth storing.
            item['trailer'] = ''
            item['duration'] = None
            item['site'] = self.site
            item['parent'] = self.parent
            item['network'] = self.network
            item['type'] = 'Scene'

            item = self.check_item(item, self.days)
            if item:
                yield item
