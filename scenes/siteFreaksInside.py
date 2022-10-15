import re
import string
from datetime import date, timedelta
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem
from scrapy.utils.project import get_project_settings


class SiteFreaksInsideSpider(BaseSceneScraper):
    name = 'FreaksInside'

    start_urls = [
        '',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': ''
    }

    custom_settings = {
            "CONCURRENT_REQUESTS": 1,
            "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
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

        yield scrapy.Request('https://www.freaksinside.com/newsarchive.php', callback=self.parse_archives, meta=meta, headers=self.headers, cookies=self.cookies)

    def parse_archives(self, response):
        meta = response.meta
        archives = response.xpath('//td/font/a[contains(@href, "newsarchive")]/@href').getall()
        for archive in archives:
            archive = self.format_link(response, archive)
            archive_year = re.search(r'year=(\d{4})', archive).group(1)
            # ~ archive_month = re.search(r'month=(\d{1,2})', archive).group(1)
            # ~ archive_date = f"{archive_year}-{archive_month}-30"

            # ~ days = self.days
            # ~ if days:
                # ~ if days > 27375:
                    # ~ filter_date = '0000-00-00'
                # ~ else:
                    # ~ filter_date = date.today() - timedelta(days)
                    # ~ filter_date = filter_date.strftime('%Y-%m-%d')
            # ~ if not filter_date:
                # ~ filter_date = '0000-00-00'

            # ~ if archive_date > filter_date:
            # ~ if archive_year == "2009":
            yield scrapy.Request(archive, callback=self.get_scenes, meta=meta, headers=self.headers, cookies=self.cookies)

        # ~ yield scrapy.Request(response.url, callback=self.get_scenes, meta=meta, headers=self.headers, cookies=self.cookies, dont_filter=True)

    def get_scenes(self, response):
        scenes = response.xpath('//tr/td/font/b')
        for scene in scenes:
            if re.search(r'(\d{1,2}/\d{1,2}/\d{4})', scene.get()):
                item = SceneItem()
                scenedate = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', scene.get()).group(1)
                item['date'] = self.parse_date(scenedate, date_formats=['%m/%d/%Y']).isoformat()

                titlerow = scene.xpath('./../../../following-sibling::tr[2]/td/font/i/text()')
                if titlerow:
                    titlerow = titlerow.get()
                    title = re.search(r'(.*?)\|', titlerow)
                    if title:
                        item['title'] = self.cleanup_title(title.group(1))
                    else:
                        item['title'] = None

                    performers = re.search(r'freaky.*?:(.*?)\|', titlerow.lower())
                    if performers:
                        performers = performers.group(1)
                        performers = performers.split("&")
                        item['performers'] = list(map(lambda x: string.capwords(x.strip()), performers))
                        item['performers'] = [i for i in item['performers'] if i]
                    else:
                        item['performers'] = []

                image = scene.xpath('./../../../following-sibling::tr[4]//video/@poster|./../../../following-sibling::tr[4]//img[1]/@src')
                if image:
                    item['image'] = self.format_link(response, image.get())
                    item['image_blob'] = self.get_image_blob_from_link(item['image'])
                    try:
                        sceneid = re.search(r'/(\d+)/', item['image'])
                        if not sceneid:
                            sceneid = re.search(r'/clip(\d+)/', item['image'])
                        if sceneid:
                            item['id'] = sceneid.group(1)
                        else:
                            item['id'] = None
                    except:
                        print(f"Failed on item: {item['image']}")
                else:
                    item['image'] = None
                    item['image_blob'] = None
                    item['id'] = None

                trailer = scene.xpath('./../../../following-sibling::tr[4]//video/source/@src')
                if trailer:
                    item['trailer'] = self.format_link(response, trailer.get())
                else:
                    item['trailer'] = None

                item['tags'] = ['Fetish', 'Latex', 'Bondage']
                item['site'] = "Freaks Inside"
                item['parent'] = "Freaks Inside"
                item['network'] = "Freaks Inside"
                item['description'] = None
                item['url'] = response.url


                # ~ print(item)
                if item['title'] and item['id']:
                    yield item
