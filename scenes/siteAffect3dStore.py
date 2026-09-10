import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteAffect3dStoreSpider(BaseSceneScraper):
    name = 'Affect3dStore'
    network = 'Affect3dStore'
    parent = 'Affect3dStore'
    site = 'Affect3dStore'

    start_urls = [
        'https://affect3dstore.com',
    ]

    selector_map = {
        'title': '//h1[@class="page-title"]/span/text()',
        'description': '//div[@itemprop="description"]/p//text()',
        # The store shows no release date anywhere on a product page
        'date': '',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '',
        'tags': '//div[contains(@class,"breadcrumbs")]//a/text()',
        'external_id': r'/([a-z0-9-]+)/?$',
        'trailer': '',
        'pagination': '/ai-3d-animation-porn-videos/short-clips?p=%s',
    }

    # Breadcrumb trail is Home > Animations > Short Clips; only the last two are useful
    tag_trash = ['home']

    def get_scenes(self, response):
        scenes = response.xpath('//a[contains(@class, "product-item-link")]/@href').getall()
        for scene in scenes:
            # The quick-view control is an <a href="#"> with the same class
            if '/short-clips/' in scene:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_id(self, response):
        """Prefer the Magento SKU (REDROBOT3D0081) over the URL slug - it is stable
        across the store's periodic URL restructures."""
        sku = response.xpath('//div[@itemprop="sku"]/text()').get()
        if sku and sku.strip():
            return sku.strip()
        return super().get_id(response)

    def get_tags(self, response):
        tags = super().get_tags(response)
        return [tag for tag in tags if tag.lower() not in self.tag_trash]
