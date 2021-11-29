import re
import string
from urllib.parse import urlencode
import datetime
from datetime import date, timedelta
import scrapy
from slugify import slugify
from tldextract import tldextract
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class ProjectOneServiceSpider(BaseSceneScraper):
    name = 'ProjectOneService'
    network = 'mindgeek'

    start_urls = [
        # ~ # Only need one starting URL per "site", pulls everything through common feed

        'https://www.babes.com',
        # 'https://www.babesunleashed.com',
        # 'https://www.elegantanal.com',
        # 'https://www.officeobsession.com',
        # 'https://www.stepmomlessons.com',

        'https://www.bellesafilms.com',
        # 'https://www.bellesa.com',
        # 'https://www.bellesahouse.com',

        'https://www.biempire.com',
        'https://www.brazzers.com',
        # 'https://www.babygotboobs.com',
        # 'https://www.bigbuttslikeitbig.com',
        # 'https://www.bigtitsatschool.com',
        # 'https://www.bigtitsatwork.com',
        # 'https://www.bigtitsinsports.com',
        # 'https://www.bigtitsinuniform.com',
        # 'https://www.bigwetbutts.com',
        # 'https://www.brazzersexxtra.com',
        # 'https://www.brazzersvault.com',
        # 'https://www.bustyandreal.com',
        # 'https://www.cfnm.com',
        # 'https://www.daywithapornstar.com',
        # 'https://www.dirtymasseur.com',
        # 'https://www.doctoradventures.com',
        # 'https://www.hotandmean.com',
        # 'https://www.hotchicksbigasses.com',
        # 'https://www.jugfuckers.com',
        # 'https://www.milfslikeitbig.com',
        # 'https://www.mommygotboobs.com',
        # 'https://www.momsincontrol.com',
        # 'https://www.pornstarslikeitbig.com',
        # 'https://www.realwifestories.com',
        # 'https://www.shesgonnasquirt.com',
        # 'https://www.teenslikeitbig.com',
        # 'https://www.zzseries.com',

        'https://www.bromo.com',
        # 'https://www.bromoblackmaleme.com',
        # 'https://www.bromous.com',

        'https://www.deviante.com',
        # 'https://www.eroticspice.com',
        # 'https://www.forgivemefather.com',
        # 'https://www.loveherass.com',
        # 'https://www.prettydirtyteens.com',
        # 'https://www.sexworking.com',

        'https://www.digitalplayground.com',
        'https://www.erito.com',
        'https://www.fakehub.com',
        # 'https://www.fakeagent.com',
        # 'https://www.fakeagentuk.com',
        # 'https://www.fakecop.com',
        # 'https://www.fakedrivingschool.com',
        # 'https://www.fakehospital.com',
        # 'https://www.fakehostel.com',
        # 'https://www.faketaxi.com',
        # 'https://www.fakehuboriginals.com',
        # 'https://www.femaleagent.com',
        # 'https://www.femalefaketaxi.com',
        # 'https://www.publicagent.com',

        'https://www.iconmale.com',
        'https://www.men.com',
        'https://www.metrohd.com',
        # 'https://www.devianthardcore.com',
        # 'https://www.familyhookups.com',
        # 'https://www.girlgrind.com',
        # 'https://www.kinkyspa.com',
        # 'https://www.shewillcheat.com',

        'https://www.milehighmedia.com',
        # 'https://www.doghousedigital.com',
        # 'https://www.familysinners.com',
        # 'https://www.realityjunkies.com',
        # 'https://www.sweetheartvideo.com',
        # 'https://www.sweetsinner.com',

        'https://www.milfed.com',
        # 'https://www.cherrypop.com',
        # 'https://www.doghousedigital.com',    (Crossover with MileHighMedia)
        # 'https://www.familysinners.com',      (Crossover with MileHighMedia)
        # 'https://www.lesbianolderyounger.com',
        # 'https://www.milehighmedia.com',      (Crossover with MileHighMedia)
        # 'https://www.realityjunkies.com',     (Crossover with MileHighMedia)
        # 'https://www.sweetheartvideo.com',    (Crossover with MileHighMedia)
        # 'https://www.sweetsinner.com',        (Crossover with MileHighMedia)

        'https://www.mofos.com',
        # 'https://www.bustedbabysitters.com',
        # 'https://www.dontbreakme.com',
        # 'https://www.dronehunter.com',
        # 'https://www.girlsgonepink.com',
        # 'https://www.iknowthatgirl.com',
        # 'https://www.ingangwebang.com',
        # 'https://www.latinasextapes.com',
        # 'https://www.letstryanal.com',
        # 'https://www.milfslikeitblack.com',
        # 'https://www.mofosbsides.com',
        # 'https://www.mofoslab.com',
        # 'https://www.mofosworldwide.com',
        # 'https://www.pervsonpatrol.com',
        # 'https://www.pornstarvote.com',
        # 'https://www.projectrv.com',
        # 'https://www.publicpickups.com',
        # 'https://www.realslutparty.com',
        # 'https://www.sharemybf.com',
        # 'https://www.shesafreak.com',
        # 'https://www.strandedteens.com',
        # 'https://www.thesexscout.com',

        'https://www.propertysex.com',
        'https://www.realitykings.com',
        # 'https://www.40inchplus.com',
        # 'https://www.8thstreetlatinas.com',
        # 'https://www.badtowtruck.com',
        # 'https://www.bignaturals.com',
        # 'https://www.bigtitsboss.com',
        # 'https://www.captainstabbin.com',
        # 'https://www.cfnmsecret.com',
        # 'https://www.crazyasiangfs.com',
        # 'https://www.crazycollegegfs.com',
        # 'https://www.cumfiesta.com',
        # 'https://www.daredorm.com',
        # 'https://www.eurosexparties.com',
        # 'https://www.extremeasses.com',
        # 'https://www.extremenaturals.com',
        # 'https://www.firsttimeauditions.com',
        # 'https://www.gfrevenge.com',
        # 'https://www.girlsofnaked.com',
        # 'https://www.happytugs.com',
        # 'https://www.hdlove.com',
        # 'https://www.hornybirds.com',
        # 'https://www.hotbush.com',
        # 'https://www.inthevip.com',
        # 'https://www.lilhumpers.com',
        # 'https://www.lookathernow.com',
        # 'https://www.mikeinbrazil.com',
        # 'https://www.mikesapartment.com',
        # 'https://www.milfhunter.com',
        # 'https://www.milfnextdoor.com',
        # 'https://www.momsbangteens.com',
        # 'https://www.momslickteens.com',
        # 'https://www.moneytalks.com',
        # 'https://www.monstercurves.com',
        # 'https://www.nofaces.com',
        # 'https://www.pure18.com',
        # 'https://www.recklessinmiami.com',
        # 'https://www.rkprime.com',
        # 'https://www.roundandbrown.com',
        # 'https://www.saturdaynightlatinas.com',
        # 'https://www.seemywife.com',
        # 'https://www.sneakysex.com',
        # 'https://www.streetblowjobs.com',
        # 'https://www.teenslovehugecocks.com',
        # 'https://www.welivetogether.com',
        # 'https://www.wivesinpantyhose.com',

        'https://www.sexyhub.com',
        # 'https://www.danejones.com',
        # 'https://www.fitnessrooms.com',
        # 'https://www.girlfriends.com',
        # 'https://www.lesbea.com',
        # 'https://www.massagerooms.com',
        # 'https://www.momxxx.com',

        'https://www.squirted.com',
        'https://www.thegayoffice.com',
        # 'https://www.bigdicksatschool.com',
        # 'https://www.bromous.com', (Crossover with Bromo)
        # 'https://www.drillmyhole.com',
        # 'https://www.godsofmen.com',
        # 'https://www.jizzorgy.com',
        # 'https://www.menofuk.com',
        # 'https://www.realitydudes.com',
        # 'https://www.str8chaser.com',
        # 'https://www.str8togay.com',
        # 'https://www.toptobottom.com',

        'https://www.transangelsnetwork.com',
        # 'https://www.transangels.com',

        'https://www.transharder.com',  # Seems to be the same as TransAngels, but some additional
        'https://www.transsensual.com',  # Seems to be the same as TransAngels, but some additional
        'https://www.trueamateurs.com',
        'https://www.tube8vip.com',
        'https://www.twistys.com',
        # 'https://www.anettedawn.com',
        # 'https://www.featurefilm.com',
        # 'https://www.momknowsbest.com',
        # 'https://www.nicolegraves.com',
        # 'https://www.turningtwistys.com',
        # 'https://www.twistysteasers.com',
        # 'https://www.twistyshard.com',
        # 'https://www.whengirlsplay.com',

        'https://www.whynotbi.com',
    ]

    selector_map = {
        'external_id': 'scene\\/(\\d+)'
    }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, headers=self.headers, cookies=self.cookies,
                                 meta={'url': url})

    def parse(self, response):
        token = self.get_token(response)

        headers = {
            'instance': token,
        }

        response.meta['headers'] = headers
        response.meta['limit'] = 100
        response.meta['page'] = -1
        response.meta['url'] = response.url

        return self.get_next_page(response)

    def get_scenes(self, response):
        scene_count = 0

        for scene in response.json()['result']:
            item = SceneItem()

            if scene['collections'] and len(scene['collections']):
                item['site'] = scene['collections'][0]['name']
            else:
                item['site'] = tldextract.extract(response.meta['url']).domain

            if tldextract.extract(
                    response.meta['url']).domain == 'digitalplayground':
                item['site'] = 'digitalplayground'

            item['image'] = self.get_image(scene)

            item['image_blob'] = None

            item['trailer'] = self.get_trailer(scene)
            if not item['trailer']:
                item['trailer'] = ''
            item['date'] = self.parse_date(scene['dateReleased']).isoformat()
            item['id'] = scene['id']
            item['network'] = self.network
            item['parent'] = tldextract.extract(response.meta['url']).domain

            if 'title' in scene:
                item['title'] = scene['title']
            else:
                item['title'] = item['site'] + ' ' + self.parse_date(scene['dateReleased']).strftime('%b/%d/%Y')

            if 'description' in scene:
                item['description'] = scene['description']
            else:
                item['description'] = ''

            item['performers'] = []
            for model in scene['actors']:
                item['performers'].append(model['name'])

            if 'actors' not in scene or not item['performers']:
                item['performers'] = ['Unknown']

            item['tags'] = []
            for tag in scene['tags']:
                item['tags'].append(tag['name'])

            path = '/scene/' + str(item['id']) + '/' + slugify(item['title'])
            item['url'] = self.format_url(response.meta['url'], path)

            # Deviante abbreviations
            if item['site'] == "fmf":
                item['site'] = "Forgive Me Father"
                item['parent'] = "Deviante"
            if item['site'] == "sw":
                item['site'] = "Sex Working"
                item['parent'] = "Deviante"
            if item['site'] == "pdt":
                item['site'] = "Pretty Dirty Teens"
                item['parent'] = "Deviante"
            if item['site'] == "lha":
                item['site'] = "Love Her Ass"
                item['parent'] = "Deviante"
            if item['site'] == "es":
                item['site'] = "Erotic Spice"
                item['parent'] = "Deviante"

            item['parent'] = string.capwords(item['parent'])

            scene_count = scene_count + 1
            days = int(self.days)
            if days > 27375:
                filterdate = "0000-00-00"
            else:
                filterdate = date.today() - timedelta(days)
                filterdate = filterdate.strftime('%Y-%m-%d')

            if self.debug:
                if not item['date'] > filterdate:
                    item['filtered'] = "Scene filtered due to date restraint"
                print(item)
            else:
                if filterdate:
                    if item['date'] > filterdate:
                        yield item
                else:
                    yield item

        if scene_count > 0:
            if 'page' in response.meta and (
                    response.meta['page'] % response.meta['limit']) < self.limit_pages:
                yield self.get_next_page(response)

    def get_next_page(self, response):
        meta = {
            'url': response.meta['url'],
            'headers': response.meta['headers'],
            'page': (response.meta['page'] + 1),
            'limit': response.meta['limit']
        }

        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        query = {
            'dateReleased': f"<{tomorrow}",
            'limit': meta['limit'],
            'type': 'scene',
            'orderBy': '-dateReleased',
            'offset': (meta['page'] * meta['limit']),
            'referrer': meta['url'],
        }

        print('NEXT PAGE: ' + str(meta['page']))

        link = 'https://site-api.project1service.com/v2/releases?' + \
            urlencode(query)
        return scrapy.Request(url=link, callback=self.get_scenes,
                              headers=response.meta['headers'], meta=meta)

    def get_token(self, response):
        token = re.search('instance_token=(.+?);',
                          response.headers.getlist('Set-Cookie')[0].decode("utf-8"))
        return token.group(1)

    def get_image(self, scene):
        image_arr = []
        if 'card_main_rect' in scene['images'] and len(
                scene['images']['card_main_rect']):
            image_arr = scene['images']['card_main_rect']
        elif 'poster' in scene['images'] and len(scene['images']['poster']):
            image_arr = scene['images']['poster']

        sizes = ['xx', 'xl', 'lg', 'md', 'sm']
        for index in image_arr:
            image = image_arr[index]
            for size in sizes:
                if size in image:
                    return image[size]['url']

    def get_trailer(self, scene):
        for index in scene['videos']:
            trailer = scene['videos'][index]
            for size in ['720p', '576p', '480p', '360p', '320p', '1080p', '4k']:
                if size in trailer['files']:
                    return trailer['files'][size]['urls']['view']
