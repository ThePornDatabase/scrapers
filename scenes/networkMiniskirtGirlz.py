import re
import requests
from requests import get
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkMiniskirtGirlzSpider(BaseSceneScraper):
    name = 'MiniskirtGirlz'

    start_urls = [
        ['https://miniskirtgirlz.com', 'https://miniskirtgirlz.com/001_FreeDesignPages/FreeHome.htm', 'https://miniskirtgirlz.com/001_FreeDesignPages/PP10msk_Hme_%s.htm', 43, "MiniskirtGirls"],
        ['https://miniskirtgirlz.com', 'https://miniskirtgirlz.com/001_FreeDesignPages/ArseFirst_HomePage.htm', 'https://miniskirtgirlz.com/001_FreeDesignPages/ArseFirst_Page%s.htm', 15, "ArseFirst"],
        ['https://miniskirtgirlz.com', 'https://miniskirtgirlz.com/001_FreeDesignPages/creampiefunbabes_HomePage.htm', 'https://miniskirtgirlz.com/001_FreeDesignPages/creampiefunbabes_Page%s.htm', 16, "CreampieFunBabes"],
        ['https://miniskirtgirlz.com', 'https://miniskirtgirlz.com/001_FreeDesignPages/Spunkymilfs_HomePage.htm', 'https://miniskirtgirlz.com/001_FreeDesignPages/Spunkymilfs_HomePage_%s.htm', 11, "SpunkyMILFs"],
        ['https://miniskirtgirlz.com', 'https://miniskirtgirlz.com/001_FreeDesignPages/CreamAcademy_HomePage.htm', 'https://miniskirtgirlz.com/001_FreeDesignPages/CreamAcademy_HomePage_%s.htm', 19, "CreamAcademy"],
        ['https://miniskirtgirlz.com', 'https://miniskirtgirlz.com/001_FreeDesignPages/spunkyBBWs_HomePage.htm', 'https://miniskirtgirlz.com/001_FreeDesignPages/spunkyBBWs_HomePage_%s.htm', 7, "SpunkyBBWs"],
        ['https://miniskirtgirlz.com', 'https://miniskirtgirlz.com/001_FreeDesignPages/SpunkInMyBum_HomePage.htm', 'https://miniskirtgirlz.com/001_FreeDesignPages/SpunkInMyBum_HomePage_%s.htm', 11, "SpunkInMyBum"],
        ['https://miniskirtgirlz.com', 'https://miniskirtgirlz.com/001_FreeDesignPages/SpunkyFantasia_HomePage.html', 'https://miniskirtgirlz.com/001_FreeDesignPages/SpunkyFantasia_Page_%s.htm', 9, "SpunkyFantasia"],
        ['https://miniskirtgirlz.com', 'https://miniskirtgirlz.com/001_FreeDesignPages/BimboSeeder_HomePage.html', 'https://miniskirtgirlz.com/001_FreeDesignPages/BimboSeeder_HP_0%s.htm', 7, "BimboSeeder"],
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/001_FreeDesignPages/PP10msk_Hme_%s.htm',
    }

    def get_next_page_url(self, page, first_page, pagination, max_page):
        if page == 1:
            return first_page

        page = max_page - page
        if page:
            if page < 10 and "spunkymilfs" not in pagination.lower() and "creamacademy" not in pagination.lower() and "spunkybbw" not in pagination.lower() and "spunkinmybum" not in pagination.lower():
                page = str(page).rjust(2, '0')
            url = pagination % page
            request = requests.get(url)
            if request.status_code == 404:
                url = url + "l"
            return url
        return "https://www.google.com"

    def start_requests(self):
        ip = get('https://api.ipify.org').content.decode('utf8')
        print('My public IP address is: {}'.format(ip))

        meta = {}
        meta['page'] = self.page

        for link in self.start_urls:
            meta['url'] = link[0]
            meta['first_page'] = link[1]
            meta['pagination'] = link[2]
            meta['max_pages'] = link[3]
            meta['site'] = link[4]
            yield scrapy.Request(url=self.get_next_page_url(self.page, meta['first_page'], meta['pagination'], meta['max_pages']), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def parse(self, response, **kwargs):
        meta = response.meta
        scenes = self.get_scenes(response)
        count = 0
        for scene in scenes:
            count += 1
            yield scene

        if 'page' in response.meta and response.meta['page'] < meta['max_pages']:
            meta['page'] = meta['page'] + 1
            print('NEXT PAGE: ' + str(meta['page']))
            yield scrapy.Request(url=self.get_next_page_url(meta['page'], meta['first_page'], meta['pagination'], meta['max_pages']), callback=self.parse, meta=meta)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//video')
        for scene in scenes:
            item = self.init_scene()
            item['url'] = response.url
            image = scene.xpath('./@poster')
            if image:
                image = image.get()
                image = image.replace("../", "/")
                item['image'] = self.format_link(response, image)
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
            else:
                image = scene.xpath('./ancestor::tr[1]/preceding-sibling::tr[1]//img/@src')
                if image:
                    image = image.get()
                    image = image.replace("../", "/")
                    item['image'] = self.format_link(response, image)
                    item['image_blob'] = self.get_image_blob_from_link(item['image'])

            trailer = scene.xpath('./source/@src')
            if trailer:
                trailer = trailer.get()
                trailer = trailer.replace("../", "/")
                if trailer:
                    item['trailer'] = self.format_link(response, trailer)

            searchString = ""
            if item['image']:
                searchString = re.search(r'Update.*?/(.*?)/', item['image'])
                if searchString:
                    searchString = searchString.group(1)
                    title = scene.xpath(f"//ancestor::tr/preceding-sibling::tr//strong//ancestor::td//img[contains(@src, '{searchString}')]//ancestor::td[1]//strong//text()|//video//ancestor::tr/preceding-sibling::tr//p//ancestor::td//img[contains(@src, '{searchString}')]//ancestor::td[@valign='middle'][1]//p/text()")
                    if title:
                        title = self.cleanup_title(title.get())
                        title = title.replace("Uploaded", "").replace(":", "").strip()
                        item['title'] = title

            item['site'] = meta['site']
            item['parent'] = item['site']
            if item['image']:
                item['id'] = re.search(r'.*\/(.*)_.*?\d+w', item['image'])
                if item['id']:
                    item['id'] = item['id'].group(1)
            item['network'] = "MiniskirtGirlz"
            item['type'] = "Scene"
            if title and item['id']:
                yield item
