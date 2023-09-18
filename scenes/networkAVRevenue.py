import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem
from scrapy.utils.project import get_project_settings
from lxml import etree
from lxml.etree import XMLParser
from parsel import Selector


class NetworkAVRevenueSpider(BaseSceneScraper):
    name = 'AVRevenue'
    network = 'AV Revenue'

    NSMAP = {
        'content': "http://purl.org/rss/1.0/modules/content/",
        'wfw': "http://wellformedweb.org/CommentAPI/",
        'dc': "http://purl.org/dc/elements/1.1/",
        'atom': "http://www.w3.org/2005/Atom",
        'sy': "http://purl.org/rss/1.0/modules/syndication/",
        'slash': "http://purl.org/rss/1.0/modules/slash/",
        'media': "http://search.yahoo.com/mrss/"
    }

    start_urls = [
        'https://baberotica.com/feed?limit=0',
        'https://baberoticavr.com/feed?limit=0',
        'https://japanhdv.com/feed?limit=0',
        'https://tenshigao.com/feed?limit=0',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': ''
    }

    def start_requests(self):
        settings = get_project_settings()

        meta = {}
        meta['page'] = self.page
        if 'USE_PROXY' in settings.attributes.keys():
            use_proxy = settings.get('USE_PROXY')
        else:
            use_proxy = None

        if use_proxy:
            print(f"Using Settings Defined Proxy: True ({settings.get('PROXY_ADDRESS')})")
        else:
            try:
                if self.proxy_address:
                    meta['proxy'] = self.proxy_address
                    print(f"Using Scraper Defined Proxy: True ({meta['proxy']})")
            except Exception:
                print("Using Proxy: False")

        for link in self.start_urls:
            yield scrapy.Request(link, callback=self.get_scenes, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        # ~ response.selector.register_namespace('media', "http://search.yahoo.com/mrss/")
        parser = XMLParser(strip_cdata=False)
        # ~ etree.register_namespace('media', "http://search.yahoo.com/mrss/")

        root = etree.fromstring(response.body, parser=parser, base_url=response.url)
        selector = Selector(root=root)
        scenes = selector.xpath('//item', namespaces=self.NSMAP)
        for scene in scenes:
            item = SceneItem()
            item['title'] = self.cleanup_title(self.get_field(scene, './title/text()'))
            description = self.get_field(scene, './description/text()')
            if description:
                item['description'] = description
            else:
                item['description'] = ""
            item['date'] = ""
            scenedate = self.get_field(scene, './pubdate/text()|./pubDate/text()')
            if scenedate:
                scenedate = self.parse_date(scenedate)
                if scenedate:
                    item['date'] = scenedate.isoformat()
            item['performers'] = self.get_fields(scene, './category[contains(@domain,"model")]//text()')
            tags = self.get_fields(scene, './category[not(contains(@domain,"model"))]//text()')
            tags2 = tags.copy()
            for tag in tags2:
                matches = ['new model', 'cup size', 'hair color', 'teaser']
                if any(x in tag.lower() for x in matches) or not len(tag) > 2:
                    tags.remove(tag)
            item['tags'] = list(map(lambda x: x.strip().title(), tags))

            image = self.get_field(scene, './/media:content[@isDefault="true"]/@url')
            if not image:
                image = self.get_field(scene, './/media:content[1]/@url')
            item['image'] = image
            # ~ item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['image_blob'] = ""
            item['trailer'] = self.get_field(scene, './/media:content[contains(@url, "mp4")]/@url')
            item['url'] = self.get_field(scene, './link/text()').replace("https:https:", "https:").replace("http:http:", "http:")
            item['id'] = self.get_field(scene, './/guid//text()')
            if "japanhdv" in response.url:
                item['site'] = "Japan HDV"
                item['parent'] = "Japan HDV"
            elif "baberoticavr" in response.url:
                item['site'] = "Baberotica VR"
                item['parent'] = "Baberotica VR"
            elif "baberotica" in response.url:
                item['site'] = "Baberotica"
                item['parent'] = "Baberotica"
            elif "tenshigao" in response.url:
                item['site'] = "Tenshigao"
                item['parent'] = "Tenshigao"
            item['network'] = 'AV Revenue'

            yield self.check_item(item, self.days)

    def get_field(self, scene, xpath):
        field = scene.xpath(xpath, namespaces=self.NSMAP)
        if field:
            return field.get()
        return None

    def get_fields(self, scene, xpath):
        fields = scene.xpath(xpath, namespaces=self.NSMAP)
        if fields:
            return fields.getall()
        return None
