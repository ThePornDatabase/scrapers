import re
import string
from requests import get
import scrapy
from datetime import datetime, timedelta
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkAPClipsSpider(BaseSceneScraper):
    name = 'APClips'
    network = 'APClips'

    start_urls = [
        'https://apclips.com',
    ]

    selector_map = {
        'title': '//h2/text()',
        'description': '//div[contains(@class, "text-medium") and contains(@class, "pr-2")]//text()',
        'date': '',
        'image': '//video/@poster',
        'tags': '//div[@class="tag-cloud"]/a/text()',
        'trailer': '',
        'external_id': r'',
        'pagination': '/videos?q=&sort=date-new&is_search=1&creator_type_filter%5B%5D=model&creator_type_filter%5B%5D=studio&creator_type_filter%5B%5D=trans&creator_type_filter%5B%5D=gay&cats=&catpref=any&tags=&tagpref=any&rating=0&minlength=2&minprice=1&maxprice=999&page=<PAGE>',
        'type': 'Scene',
    }

    def get_next_page_url(self, base, page):
        pagination = self.get_selector_map('pagination')
        pagination = pagination.replace("<PAGE>", str(page))
        return self.format_url(base, pagination)

    def start_requests(self):
        ip = get('https://api.ipify.org').content.decode('utf8')
        print('My public IP address is: {}'.format(ip))

        if self.limit_pages == 1:
            self.limit_pages = 50

        meta = {}
        meta['page'] = self.page

        singleurl = self.settings.get('url')
        if singleurl:
            yield scrapy.Request(singleurl, callback=self.parse_scene, meta=meta, headers=self.headers, cookies=self.cookies)
        else:
            for link in self.start_urls:
                yield scrapy.Request(url=self.get_next_page_url(link, self.page), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "video-col")]')
        for scene in scenes:
            sceneid = scene.xpath('.//a[contains(@class, "btn-block")]/@data-content-code')
            if sceneid:
                meta['id'] = re.search(r'-(\d+)', sceneid.get()).group(1)

            duration = scene.xpath('.//span[contains(text(), "uration")]/following-sibling::text()')
            if duration:
                meta['duration'] = self.duration_to_seconds(duration.get())

            site = scene.xpath('.//span[contains(@class, "text-smaller") and contains(text(), "by")]/strong/text()')
            if site:
                site = site.get()
                meta['performers'] = [site]
                if " and " in site.lower():
                    meta['performers'] = site.lower().split(" and ")
                if " & " in site.lower():
                    meta['performers'] = site.lower().split(" & ")

                meta['performers'] = list(map(lambda x: string.capwords(x.strip()), meta['performers']))

                if len(meta['performers']) > 1:
                    meta['performers'] = [f"{performer} ({re.sub(r'[^a-zA-Z0-9]+', '', string.capwords(site))})" for performer in meta['performers']]

                meta['site'] = f"APClips: {site}"
                meta['parent'] = "APClips"
                meta['network'] = "APClips"

            title = scene.xpath('.//span[contains(@class, "item-title")]/text()')
            if title:
                meta['title'] = self.cleanup_title(title.get())

            trailer = scene.xpath('./div[1]/a/@data-preview')
            if trailer:
                meta['trailer'] = trailer.get()

            scene = scene.xpath('./div[1]/a/@href').get()
            if meta['id']:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_date(self, response):
        daysago = response.xpath('//text()[contains(., "Added")]/following-sibling::strong/text()')
        if daysago:
            daysago = daysago.get()
            if "days ago" in daysago.lower() or "day ago" in daysago.lower():
                daysago = re.search(r'(\d+)', daysago).group(1)
                daysago = int(daysago)
                date = datetime.now() - timedelta(days=daysago)
                if date:
                    return date.strftime('%Y-%m-%d')
            if "hours ago" in daysago.lower() or "hour ago" in daysago.lower():
                hoursago = re.search(r'(\d+)', daysago).group(1)
                hoursago = int(hoursago)
                date = datetime.now() - timedelta(hours=hoursago)
                if date:
                    return date.strftime('%Y-%m-%d')
            if "mins ago" in daysago.lower() or "min ago" in daysago.lower():
                minsago = re.search(r'(\d+)', daysago).group(1)
                minsago = int(minsago)
                date = datetime.now() - timedelta(minutes=minsago)
                if date:
                    return date.strftime('%Y-%m-%d')
            if "years ago" in daysago.lower() or "year ago" in daysago.lower():
                yearsago = re.search(r'(\d+)', daysago).group(1)
                yearsago = int(yearsago) * 365
                date = datetime.now() - timedelta(days=yearsago)
                if date:
                    return date.strftime('%Y-%m-%d')
            if "months ago" in daysago.lower() or "month ago" in daysago.lower():
                monthsago = re.search(r'(\d+)', daysago).group(1)
                monthsago = int(monthsago) * 30
                date = datetime.now() - timedelta(days=monthsago)
                if date:
                    return date.strftime('%Y-%m-%d')
        print(daysago, response.url)
        return None
