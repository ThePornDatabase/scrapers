import re
import datetime
from dateutil.relativedelta import relativedelta
import urllib.parse
import scrapy
from tpdb.items import PerformerItem

from tpdb.BasePerformerScraper import BasePerformerScraper


class NetworkMetArtPerformerSpider(BasePerformerScraper):
    selector_map = {
        'external_id': 'movie\\/(.+)',
        'pagination': '/api/models?first=40&page=%s&order=RATING&direction=DESC'
    }

    name = 'MetArtPerformer'
    network = 'metart'

    start_urls = [
        "https://www.alsscan.com",
        "https://www.eroticbeauty.com",
        "https://www.errotica-archives.com",
        "https://www.eternaldesire.com",
        "https://www.lovehairy.com",
        "https://www.metart.com",
        "https://www.metartx.com",
        "https://www.rylskyart.com",
        "https://www.sexart.com",
        "https://www.straplez.com",
        "https://www.stunning18.com",
        "https://www.thelifeerotic.com",
        "https://www.vivthomas.com",
        # 'https://www.hustlerunlimited.com',
        # 'https://www.barelylegal.com/'
    ]

    def get_performers(self, response):
        meta = response.meta
        performers = response.json()['models']
        for performer in performers:
            perf_name = performer['name']
            perf_link = self.format_link(response, f"/api/model?name={urllib.parse.quote_plus(perf_name)}&after=0&order=DATE&direction=DESC")
            yield scrapy.Request(perf_link, callback=self.parse_performer, meta=meta)

    def parse_performer(self, response):
        perf = response.json()
        item = PerformerItem()
        current_date = datetime.date.today()

        item['name'] = perf['name']
        item['image'] = f"https://cdn77.metartnetwork.com/{perf['siteUUID']}{perf['headshotImagePath']}"
        item['image_blob'] = self.get_image_blob_from_link(item['image'])
        item['gender'] = perf['gender'].title()

        if perf['age'] and perf['age'] >= 18:
            item['birthday'] = current_date - relativedelta(years=perf['age'])
            item['birthday'] = item['birthday'].strftime("%Y-%m-%d")
        else:
            item['birthday'] = ''

        if perf['biography']:
            CleanString = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
            item['bio'] = re.sub(CleanString, '', perf['biography']).replace("\r", "").replace("\n", "").replace("\t", "")
        else:
            item['bio'] = ''

        if perf['ethnicity']:
            item['ethnicity'] = perf['ethnicity'].title()
        else:
            item['ethnicity'] = ''

        if perf['eyes']:
            item['eyecolor'] = perf['eyes'].title()
        else:
            item['eyecolor'] = ''

        if perf['hair']:
            item['haircolor'] = perf['hair'].title()
        else:
            item['haircolor'] = ''

        if perf['height']:
            item['height'] = str(perf['height']) + "cm"
        else:
            item['height'] = ''

        if perf['weight']:
            item['weight'] = str(perf['weight']) + "kg"
        else:
            item['weight'] = ''

        if perf['country'] and perf['country']['name'] and perf['country']['name'].lower() != "unknown":
            item['nationality'] = perf['country']['name'].title()
        else:
            item['nationality'] = ''

        if perf['country'] and perf['country']['name'] and perf['country']['name'].lower() != "unknown":
            item['birthplace'] = perf['country']['name'].title()
        else:
            item['birthplace'] = ''

        item['cupsize'] = ''
        item['fakeboobs'] = None
        item['measurements'] = ''
        item['astrology'] = ''
        item['piercings'] = ''
        item['tattoos'] = ''
        item['network'] = 'metart'
        item['url'] = self.format_link(response, perf['path'])

        yield item
