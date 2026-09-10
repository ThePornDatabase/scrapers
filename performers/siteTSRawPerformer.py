import re
from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.spiders.scenes._natscms import resolve_block_id


class SiteTSRawSpider(BasePerformerScraper):
    name = 'TSRawPerformer'
    network = 'TSRaw'
    parent = 'TSRaw'
    site = 'TSRaw'

    start_urls = [
        'https://www.tsraw.com',
    ]

    headers = {'X-NATS-cms-area-id': 'cc6bd0ac-a417-47d1-9868-7855b25986e5'}

    selector_map = {
        'external_id': r'',
        'pagination': '/index.php?section=1681&start=%s'
    }


    # cms_block_id belongs to a block in the tour's layout, so it changes whenever
    # the tour is re-laid-out -- and when it does the API answers
    # {"error":"cms_block_id ... not found"} and the spider silently yields
    # nothing. It is therefore looked up once per crawl; the literal below is only
    # the fallback used if that lookup fails, so this can only ever help.
    nats_site = 'https://www.tsraw.com'
    nats_block_fallback = '102035'

    @property
    def nats_block_id(self):
        if getattr(self, '_nats_block_id', None) is None:
            self._nats_block_id = resolve_block_id(self.nats_site, self.nats_block_fallback)
            if self._nats_block_id != self.nats_block_fallback:
                print('*** %s: cms_block_id %s -> %s' % (
                    self.name, self.nats_block_fallback, self._nats_block_id))
        return self._nats_block_id

    def get_next_page_url(self, base, page):
        index = str((int(page) - 1) * 72)
        url = f"https://nats.islanddollars.com/tour_api.php/content/data-values?cms_block_id={self.nats_block_id}&cms_data_type_id=4&start={index}&count=72&orderby=name_asc&text_search=&data_details_search=%7B%22100009%22:%5B%22TSRAW%22%5D%7D"
        return url

    def get_detail(self, performer, detail_name):
        details = performer.get('data_detail_values', {})
        for key, detail in details.items():
            if isinstance(detail, dict) and detail.get('name') == detail_name:
                return detail.get('value', '').strip()
        return ''

    def get_performer_image(self, performer):
        details = performer.get('data_detail_values', {})
        thumb = details.get('11', {})
        if isinstance(thumb, dict):
            content = thumb.get('content_formatted', {})
            images = content.get('image', [])
            if images:
                fileuri = images[0].get('fileuri', '')
                signature = images[0].get('signature', '')
                if fileuri:
                    return f"https://c762d323d1.mjedge.net{fileuri}?{signature}"
        return ''

    def get_performers(self, response):
        jsondata = response.json()
        performers = jsondata['data_values']
        for performer in performers:
            item = self.init_performer()
            name = performer.get('name', '')
            if ' ' not in name:
                name = f"{name} {performer.get('cms_data_value_id', '')}"
            item['name'] = name
            item['url'] = f"https://www.tsraw.com/model/{performer.get('slug', '')}/"
            item['bio'] = self.cleanup_description(performer.get('description', ''))
            item['image'] = self.get_performer_image(performer)
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            gender = self.get_detail(performer, 'Gender')
            item['gender'] = 'Transgender Female' if gender == 'Trans' else gender
            item['astrology'] = ''
            item['birthplace'] = self.get_detail(performer, 'Location')
            item['nationality'] = self.get_detail(performer, 'Nationality')
            item['ethnicity'] = self.get_detail(performer, 'Ethnicity')
            item['haircolor'] = self.get_detail(performer, 'Hair Color')
            item['eyecolor'] = self.get_detail(performer, 'Eye Color')
            weight = self.get_detail(performer, 'Weight')
            weight_match = re.search(r'(\d+)\s*kg', weight)
            item['weight'] = f"{weight_match.group(1)}kg" if weight_match else ''

            height = self.get_detail(performer, 'Height')
            height_match = re.search(r'(\d+)\s*cm', height)
            item['height'] = f"{height_match.group(1)}cm" if height_match else ''
            item['measurements'] = self.get_detail(performer, 'Measurements')
            cup_match = re.search(r'(\d+\w+)-\d+-\d+', item['measurements'])
            item['cupsize'] = cup_match.group(1) if cup_match else ''
            item['tattoos'] = ''
            item['piercings'] = ''
            item['fakeboobs'] = ''
            item['site'] = "TSRaw"
            item['network'] = "TSRaw"

            yield item
