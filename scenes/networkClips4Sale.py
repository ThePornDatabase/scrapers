import re
import string
import scrapy
import tldextract
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteClips4SaleSpider(BaseSceneScraper):

    sites = [
        ['Clips4Sale', 'Primal', 'Primal\'s Custom XXX', '107990', 'primals-custom-videos'],
        ['Clips4Sale', 'Primal', 'Clips4Sale: Primal\'s Girls Grappling', '46940', 'primal-s-girl-s-grappling'],
        ['Clips4Sale', 'Primal', 'Primal\'s Mental Domination', '24134', 'primals-mental-domination'],
        ['Clips4Sale', 'Primal', 'Clips4Sale: Primal\'s Handjobs', '41770', 'primal-s-handjobs'],
        ['Clips4Sale', 'Primal', 'Primal\'s Dark Reflections', '98931', 'primals-dark-reflections'],
        ['Clips4Sale', 'Primal', 'Clips4Sale: Primal\'s Disgraced Superheroines', '53607', 'primals-disgraced-superheroines'],
        ['Clips4Sale', 'Primal', 'Primal\'s Superheroine Shame', '50111', 'primal-s-superheroine-shame'],
        ['Clips4Sale', 'Primal', 'Primal\'s Women Entranced', '56163', 'primals-women-entranced'],
        ['Clips4Sale', 'Primal', 'Clips4Sale: Primal\'s Taboo Family Relations', '67653', 'primals-taboo-family-relations'],
        ['Clips4Sale', 'Primal', 'Clips4Sale: Primal\'s Teasing Edging Grinding', '45057', 'primal-s-teasing--edging-grinding'],
        ['Clips4Sale', 'Primal', 'Clips4Sale: Primal\'s POV Family Lust', '48125', 'primals-pov-family-lust'],
        ['Clips4Sale', 'Primal', 'Primal\'s Foot Fantasies', '58943', 'primal-s-foot-fantasies-'],
        ['Clips4Sale', 'Primal', 'Primal\'s Savage Tales', '88150', 'primals-savage-tales'],
        ['Clips4Sale', 'Primal', 'Primal\'s Ticklegasm', '55561', 'primal-s-ticklegasm'],
        ['Clips4Sale', 'Primal', 'Primal\'s MILFs', '130495', 'primals-milfs'],
        ['Clips4Sale', 'Primal', 'Primal\'s Sex Fights', '46197', 'primals-sex-fights'],
        ['Clips4Sale', 'Primal', 'Clips4Sale: Primal\'s Fantasy POV', '137897', 'primals-fantasy-pov'],
        ['Clips4Sale', 'Primal', 'Primal\'s Bondage Sex POV', '147745', 'primals-bondage-sex-pov'],
        ['Clips4Sale', 'Primal', 'Primal\'s Femme Fatale Nylon Vixens', '139363', 'primals-femme-fatale-nylon-vixens'],
        ['Clips4Sale', 'Primal', 'Primal\'s BBWs', '44723', 'primals-bbws'],
        ['Clips4Sale', 'Primal', 'Clips4Sale: Primal\'s Footjobs', '49351', 'primal-s-footjobs'],
        ['Clips4Sale', 'Borderland Bound', 'Borderland Bound', '64171', 'borderland-bound-'],
        ['Clips4Sale', 'Ginarys Kinky Adventures', 'Ginarys Kinky Adventures', '45669', 'ginary-s-kinky-adventures-'],
        ['Clips4Sale', 'Ginarys Kinky Adventures', 'Ginarys Giantess Adventures', '77757', 'ginary-s-giantess-adventures-'],
        ['Clips4Sale', 'Ginarys Kinky Adventures', 'Ginarys Tickle Adventures', '71128', 'ginary-s-tickle-adventures'],
        ['Clips4Sale', 'Superbound', 'Superbound', '8178', 'superbound'],
        ['Clips4Sale', 'Cruel Mistresses', 'Cruel Mistresses', '39213', 'cruel-caning-and-whipping-'],
        ['Clips4Sale', 'American Mean Girls', 'American Mean Girls', '32364', 'american-mean-girl'],
        ['Clips4Sale', 'Watch Me Audition', 'Watch Me Audition', '80069', 'watch-me-audition'],
        ['Clips4Sale', 'Jerky Girls', 'Jerky Girls', '2511', 'jerky-girls'],
        ['Clips4Sale', 'Mind Under Master', 'Mind Under Master', '118498', 'mind-under-master'],
        ['Clips4Sale', 'Xev Bellringer', 'Xev Bellringer', '75701', 'xev-bellringer'],
        ['Clips4Sale', 'Jerky Wives', 'Jerky Wives', '28671', 'jerky-wives-'],
        ['Clips4Sale', 'Bareback Studios', 'Bareback Studios', '35625', 'bare-back-studios'],
        ['Clips4Sale', 'Bareback Studios', 'Bareback Studios', '35625', 'bare-back-studios'],
        ['Clips4Sale', 'Mandy Flores', 'Mandy Flores', '33729', 'mandy-flores'],
        ['Clips4Sale', 'FM Concepts', 'FM Concepts', '116614', 'fm-concepts-1080p-bondage-store'],
        ['Clips4Sale', 'Mouth Stuffed and Tied Up Girls', 'Mouth Stuffed and Tied Up Girls', '4458', 'mouth-stuffed-and-tied-up-girls'],
        ['Clips4Sale', 'Jon Woods', 'American Damsels', '6571', 'american-damsels-by-jon-woods'],
        ['Clips4Sale', 'Girls Controlled', 'Girls Controlled To Be Bad', '10982', 'robo-pimp-girls-trained-to-be-bad'],
        ['Clips4Sale', 'Mark Rockwell', 'Marks Head Bobbers and Hand Jobbers', '47321', 'marks-head-bobbers-and-hand-jobbers'],
        ['Clips4Sale', 'Aaliyah Taylor', 'Aliyah Taylors Fetish', '70866', 'aaliyah-taylor-s-fetish'],
        ['Clips4Sale', 'Family Therapy (Clips4Sale)', 'Family Therapy (Clips4Sale)', '81593', 'family-therapy'],
        ['Clips4Sale', 'Brat Attack', 'Brat Attack', '83427', 'brat-attack'],
        ['Clips4Sale', 'BlackCow Video', 'BlackCow Video', '15814', 'blackcow-video'],
        ['Clips4Sale', 'Got Milked Studios', 'Got Milked Studios', '16034', 'black-slave-fantacies-'],
        ['Clips4Sale', 'Cory Chase', 'Corys Super Heroine Adventures', '32589', 'cory-s-super-heroine-adventures'],
        ['Clips4Sale', 'Cory Chase', 'Chase Water Babes', '32587', 'chase-water-babes'],
        ['Clips4Sale', 'Cory Chase', 'Kinky Cory', '41549', 'kinki-cory'],
        ['Clips4Sale', 'Cory Chase', 'Mixed Model Wrestling', '32588', 'mixed-model-wrestling'],
        ['Clips4Sale', 'GwenMedia', 'GwenMedia', '16700', 'gwenmedia-femdom-latex-fetish'],
        ['Clips4Sale', 'Sinn Sage Dreams', 'Sinn Sage Dreams', '96823', 'sinn-sage-dreams'],
        ['Clips4Sale', 'Aaliyah Taylors Fetish', 'Aaliyah Taylors Fetish', '70866', 'aaliyah-taylor-s-fetish'],
        ['Clips4Sale', 'Ashley Fires Fetish Clips', 'Ashley Fires Fetish Clips', '5177', 'ashley-fires-fetish-clips'],
        ['All Her Luv', 'Missa X', 'Missa X', '51941', 'missa'],
        ['Clips4Sale', 'Cock Ninja Studios', 'Cock Ninja Studios', '79893', 'cock-ninja-studios'],
        ['Clips4Sale', 'Pampered Penny', 'Pampered Penny', '11315', 'pampered-penny'],
        ['Clips4Sale', 'Miss Penny Barber', 'Miss Penny Barber', '18369', 'miss-penny-barber'],
        ['Clips4Sale', 'VMVideo', 'VMVideo', '174737', 'vince-may-video'],
        ['Clips4Sale', 'Angel the Dreamgirl', 'Angel the Dreamgirl', '68591', 'angel-the-dreamgirl'],
        ['Clips4Sale', 'K Klixen Productions', 'K Klixen Productions', '7373', 'k-handjob-by-klixen-'],
        ['Clips4Sale', 'Dick Sucking Lips And Facials', 'Dick Sucking Lips And Facials', '78419', 'dick-sucking-lips-and-spit'],
        ['Clips4Sale', 'Feet of Philly', 'Feet of Philly', '40511', 'feet-of-philly'],
        ['Clips4Sale', 'Cruel Unusual Femdom', 'Cruel Unusual Femdom', '5751', 'cruel---unusual-femdom'],
        ['Clips4Sale', 'Ruthless Vixens Femdom', 'Ruthless Vixens Femdom', '9085', 'ruthless-vixens-femdom'],
        ['Clips4Sale', 'XXXTREMECOMIXXX', 'XXXTREMECOMIXXX', '56081', 'xxxtremecomixxx'],
        ['Clips4Sale', 'Robomeats', 'Robomeats', '50885', 'robomeats'],
        ['Clips4Sale', 'The Tabooddhist', 'The Tabooddhist', '62135', 'dan-s-porn-and-taboo'],
        ['Clips4Sale', 'Bondage Junkies', 'Bondage Junkies', '47664', 'bondagejunkies-clips'],
        ['Clips4Sale', 'KICK ASS BONDAGE BY ROPEMARKED', 'KICK ASS BONDAGE BY ROPEMARKED', '39599', 'kick-ass-bondage-by-girls-in-a-bind'],
        ['Clips4Sale', 'Fetish Cartel', 'Fetish Cartel', '3044', 'fetish-cartel'],
        ['Clips4Sale', 'Philly Butt Sluts', 'Philly Butt Sluts', '40522', 'philly-butt-sluts'],
        ['Clips4Sale', 'Pedi Police', 'Pedi Police', '124175', 'pedi-police'],
        ['Clips4Sale', 'Barely Legal Foot Jobs', 'Barely Legal Foot Jobs', '40521', 'barely-legal-foot-jobs'],
        ['Clips4Sale', 'SilverCherrys Handjobs With a Twist', 'SilverCherrys Handjobs With a Twist', '79', 'silvercherrys-handjobs-with-a-twist'],
        ['Clips4Sale', 'Eros Handjobs N Blowjobs', 'Eros Handjobs N Blowjobs', '105416', '105416-eros-handjobs-n-blowjobs'],
        ['Clips4Sale', 'Lexis Taboo Diaries', 'Lexis Taboo Diaries', '113974', 'lexis-taboo-diaries'],
        ['Clips4Sale', 'Clips4Sale: TABOO', 'Clips4Sale: TABOO', '58471', 'taboo'],
        ['Clips4Sale', 'Old School Ties By Steve Villa', 'Old School Ties By Steve Villa', '17008', 'tied-up---gagged-by-steve-villa'],
        ['Clips4Sale', 'Hardcore Foot Sex', 'Hardcore Foot Sex', '28231', 'hardcore-foot-sex'],
        ['Clips4Sale', 'FM Concepts 1080p Men In Bondage', 'FM Concepts 1080p Men In Bondage', '117240', 'FM-Concepts-1080p-Men-In-Bondage'],
        ['Clips4Sale', 'Addie Juniper Fetish Clips', 'Addie Juniper Fetish Clips', '4502', 'addie-juniper-fetish-clips'],
        ['Clips4Sale', 'Play With Amai', 'Play With Amai', '47204', 'play-with-amai'],
        ['Clips4Sale', 'Fetish by Daisy Haze', 'Fetish by Daisy Haze', '71770', 'daisys-desires'],
        ['Clips4Sale', 'Jerk4PrincessUK', 'Jerk4PrincessUK', '36426', 'jerk4princessuk'],
        ['Clips4Sale', 'Naughty Midwest Girls (Clips4Sale)', 'Naughty Midwest Girls (Clips4Sale)', '3664', 'naughty-midwest-girls-videoclips'],
        ['Clips4Sale', 'Lilus Handjobs', 'Lilus Handjobs', '7325', 'i-jerk-off-100--strangers-hommme-hj'],
        ['Clips4Sale', 'Miss Lilu', 'Miss Lilu', '3010', 'Miss-LiLu'],
        ['Clips4Sale', 'Fetish Liza Clips', 'Fetish Liza Clips', '88414', 'fetish-liza-clips'],
        ['Clips4Sale', 'Kinky Leather Clips', 'Kinky Leather Clips', '83433', 'kinky-leather-clips'],
        ['Clips4Sale', 'GloveMansion', 'GloveMansion', '78265', 'glove-sex-clips'],
        ['Clips4Sale', 'Lucid Dreaming', 'Lucid Dreaming', '145433', 'lucid-dreaming'],
        ['Clips4Sale', 'Mandy Marx', 'Mandy Marx', '120911', 'mandy-marx'],
        ['Clips4Sale', 'Divine Goddess Amber', 'Divine Goddess Amber', '229077', 'divine-goddess-amber'],
        ['Clips4Sale', 'AstroDomina', 'AstroDomina', '56587', 'astrodomina'],
        ['Clips4Sale', 'Custom Fetish Cumshots', 'Custom Fetish Cumshots', '104694', 'custom-fetish-cumshots'],
        ['Clips4Sale', 'Cruel Anettes Fetish Store', 'Cruel Anettes Fetish Store', '122893', 'cruel-anettes-fetish-store'],
        ['Clips4Sale', 'Kenny Kong AMWF Porn', 'Kenny Kong AMWF Porn', '105418', 'kenny-kong-amwf-porn'],
        ['Clips4Sale', 'Cruel Punishments - Severe Femdom', 'Cruel Punishments - Severe Femdom', '20885', 'cruel-punishments---severe-femdom-'],
        ['Clips4Sale', 'Princess Camryn', 'Princess Camryn', '117722', 'princess-camryn'],
        ['Clips4Sale', 'Eva de Vil', 'Eva de Vil', '122965', 'eva-de-vil'],
        ['Clips4Sale', 'Mandy Flores', 'Mandy Flores', '33729', 'mandy-flores'],
        ['Clips4Sale', 'Angel The Dreamgirl', 'Angel The Dreamgirl', '68591', 'angel-the-dreamgirl'],
        ['Clips4Sale', 'Lelu Love - Cum Inside, Lets Play', 'Lelu Love - Cum Inside, Lets Play', '44611', 'lelu-love---cum-inside--let-s-play'],
        ['Clips4Sale', 'Naughty Girls', 'Naughty Girls', '148381', '148381-naughty-girls'],
        ['Clips4Sale', 'Bratty Bunny', 'Bratty Bunny', '35587', 'Bratty-Bunny'],
        ['Clips4Sale', 'POV Central', 'POV Central', '15933', 'pov-central'],
        ['Clips4Sale', 'Mistress - T - Fetish Fuckery', 'Mistress - T - Fetish Fuckery', '23869', 'mistress---t---fetish-fuckery'],
        ['Clips4Sale', 'Princess Camryn', 'Princess Camryn', '117722', 'princess-camryn'],
        ['Clips4Sale', 'Nathan Blake XXX', 'Nathan Blake XXX', '94243', 'nathan-blake-xxx'],
        ['Clips4Sale', 'JBC Videos Pantyhose', 'JBC Videos Pantyhose', '32173', 'jbc-videos-pantyhose'],
        ['Clips4Sale', 'Alex Mack Clip Store', 'Alex Mack Clip Store', '143621', 'alex-mack-clip-store'],
        ['Clips4Sale', 'J Macs POV', 'J Macs POV', '151671', 'j-macs-pov'],
        ['Clips4Sale', 'Queens of Kink', 'Queens of Kink', '74545', 'queens-of-kink'],
        ['Clips4Sale', 'Natalie Wonder Clips', 'Natalie Wonder Clips', '79477', 'natalie-wonder-clips'],
        ['Clips4Sale', 'Hoby Buchanon Facefucks Chicks', 'Hoby Buchanon Facefucks Chicks', '116032', 'hoby-buchanon-facefucks-chicks'],
        ['Clips4Sale', 'Fifi Foxx Fantasies', 'Fifi Foxx Fantasies', '120643', 'fifi-foxx-fantasies'],
        ['Clips4Sale', 'Alexis Playground', 'Alexis Playground', '33899', 'milf-alexis-rain-s-playground'],
        ['Clips4Sale', 'Andrea Rosus Kinky Explorations', 'Andrea Rosus Kinky Explorations', '75279', 'andrea-rosu-s-kinky-explorations'],
        ['Clips4Sale', 'Handjob Honeys and Blowjob Babes', 'Handjob Honeys and Blowjob Babes', '162', 'Handjob-Honeys-and-Blowjob-Babes'],
        ['Clips4Sale', 'Jan Burton', 'Jan Burton', '2853', 'milf-jan-seduces-real-stepson-tom'],
        ['Clips4Sale', 'Asian Gypsy Snow', 'Asian Gypsy Snow', '74789', 'feet-4-dinner'],
        ['Clips4Sale', 'Tammie Madison', 'Tammie Madison', '95015', 'tammie-madison'],
        ['Clips4Sale', 'FemmeLife', 'FemmeLife', '57775', 'codewordsquirrel'],
        ['Clips4Sale', 'Meana Wolf (Clips4Sale)', 'Meana Wolf (Clips4Sale)', '81629', 'mean-wolf'],
        ['Clips4Sale', 'BrokeAmateurs Clips Store', 'BrokeAmateurs Clips Store', '15842', 'brokeamateurs-clips-store'],
        ['Clips4Sale', 'GodMother The Great Video Store', 'GodMother The Great Video Store', '2519', 'godmother-the-great-video-store'],
        ['Clips4Sale', 'AngryHJs', 'AngryHJs', '137383', 'angryhjs'],
        ['Clips4Sale', 'Humiliation from Miss Alika', 'Humiliation from Miss Alika', '147267', 'humiliation-from-miss-alika'],
        ['Clips4Sale', 'Jerky Sluts', 'Jerky Sluts', '51543', 'jerky-sluts-------'],
        ['Clips4Sale', 'Bratty Foot Girls', 'Bratty Foot Girls', '40537', 'bratty-foot-girls'],
        ['Clips4Sale', 'Women on Top - of men', 'Women on Top - of men', '7740', 'women-on-top---of-men'],
        ['Clips4Sale', 'Jakes Blows Tugs n Toes', 'Jakes Blows Tugs n Toes', '77551', 'blows-and-toes'],
        ['Clips4Sale', 'Clips4Sale: SSBBW Juicy Jackie', 'Clips4Sale: SSBBW Juicy Jackie', '135731', 'ssbbw-juicy-jackie'],
        ['Clips4Sale', 'Clips4Sale: BBW Feedee Bonnies clips', 'Clips4Sale: BBW Feedee Bonnies clips', '72633', 'bbw-feedee-bonnie-s-clips'],
        ['Clips4Sale', 'Clips4Sale: BBW CHLOE', 'Clips4Sale: BBW CHLOE', '134447', 'bbw-chloe'],
        ['Clips4Sale', 'Clips4Sale: CreamPuff', 'Clips4Sale: CreamPuff', '104420', 'creampuff'],
        ['Clips4Sale', 'Clips4Sale: Ssbbw Bubbly Booty', 'Clips4Sale: Ssbbw Bubbly Booty', '130003', 'ssbbw-bubbly-booty'],
        ['Clips4Sale', 'Clips4Sale: SSBBW Foxy Roxxie', 'Clips4Sale: SSBBW Foxy Roxxie', '18516', 'ssbbw-foxy-roxxie'],
        ['Clips4Sale', 'Clips4Sale: SSBBW Reenaye Starr', 'Clips4Sale: SSBBW Reenaye Starr', '14925', 'ssbbw-reenaye-starr'],
        ['Clips4Sale', 'Clips4Sale: Jae SSBBW', 'Clips4Sale: Jae SSBBW', '16339', 'jae-ssbbw'],
        ['Clips4Sale', 'Clips4Sale: Brianna and Jae Fat Fetish Clips', 'Clips4Sale: Brianna and Jae Fat Fetish Clips', '111076', 'brianna-and-jae-fat-fetish-clips'],
        ['Clips4Sale', 'Clips4Sale: SSBBW Briannas Fat Fetish Clips', 'Clips4Sale: SSBBW Briannas Fat Fetish Clips', '69525', 'ssbbw-brianna-s-fat-fetish-clips'],
        ['Clips4Sale', 'Clips4Sale: Kyras BBW Fetish Depot', 'Clips4Sale: Kyras BBW Fetish Depot', '111606', 'kyrakane-clip-store'],
        ['Clips4Sale', 'Clips4Sale: SSBBW Pinup BODacious Kellie Kay', 'Clips4Sale: SSBBW Pinup BODacious Kellie Kay', '21475', 'ssbbw-pinup-bodacious-kellie-kay-'],
        ['Clips4Sale', 'Clips4Sale: SSBBWLEIGHTON', 'Clips4Sale: SSBBWLEIGHTON', '118282', 'ssbbwleighton'],
        ['Clips4Sale', 'Clips4Sale: loveadipose', 'Clips4Sale: loveadipose', '147757', 'loveadipose'],
        ['Clips4Sale', 'Clips4Sale: BBW Casey', 'Clips4Sale: BBW Casey', '138831', 'bbw-casey'],
        ['Clips4Sale', 'Clips4Sale: Luna Love SSBBW', 'Clips4Sale: Luna Love SSBBW', '16922', 'luna-love-ssbbw'],
        ['Clips4Sale', 'Clips4Sale: SSBBW CaitiDee', 'Clips4Sale: SSBBW CaitiDee', '43781', 'ssbbw-caitidee'],
        ['Clips4Sale', 'Clips4Sale: Summer Marshmallow', 'Clips4Sale: Summer Marshmallow', '119504', 'summer-marshmallow'],
        ['Clips4Sale', 'Clips4Sale: BBWLayla', 'Clips4Sale: BBWLayla', '181173', 'bbwlayla'],
        ['Clips4Sale', 'Clips4Sale: Olivia Jaide Kink', 'Clips4Sale: Olivia Jaide Kink', '68859', 'sweetie-slut--zecora-belle'],
        ['Clips4Sale', 'Clips4Sale: DestinyBBW AND FRIENDS FETISH CLIPS', 'Clips4Sale: DestinyBBW AND FRIENDS FETISH CLIPS', '5986', 'destinybbw-and-friends-fetish-clips'],
        ['Clips4Sale', 'Clips4Sale: Sweet Adeline', 'Clips4Sale: Sweet Adeline', '68633', 'sweet-adeline-s-clip-store'],
        ['Clips4Sale', 'Clips4Sale: The BigBootyBeautyXXL Emporium', 'Clips4Sale: The BigBootyBeautyXXL Emporium', '65243', 'the-bigbootybeautyxxl-emporium'],
        ['Clips4Sale', 'Clips4Sale: Jae and Luna - THE BBW ROOMMATES', 'Clips4Sale: Jae and Luna - THE BBW ROOMMATES', '18529', 'jae-and-luna---the-bbw-roommates-'],
        ['Clips4Sale', 'Clips4Sale: HUGE n HOT', 'Clips4Sale: HUGE n HOT', '4541', 'huge-n-hot'],
        ['Clips4Sale', 'Clips4Sale: Superior Lana Blade', 'Clips4Sale: Superior Lana Blade', '229937', 'superior-lana-blade'],
        ['Clips4Sale', 'Clips4Sale: ', 'Clips4Sale: Foxxx Studios', '81539', 'princess-sasha-foxxx-'],
        ['Clips4Sale', 'Clips4Sale: ', 'Clips4Sale: Mistress Elis Euryale', '152249', 'mistress-euryale'],
        ['Clips4Sale', 'Clips4Sale: Diary of a growing girl', 'Clips4Sale: Diary of a growing girl', '81419', 'big-cutie-margot'],
        ['Clips4Sale', 'Clips4Sale: Club Steffi', 'Clips4Sale: Club Steffi', '32047', 'club-steffi'],
        ['Clips4Sale', 'Clips4Sale: Fetishmindsproductions', 'Clips4Sale: Fetishmindsproductions', '118228', 'fetishmindsproductions'],
        ['Clips4Sale', 'Clips4Sale: Dahlia Fallon', 'Clips4Sale: Dahlia Fallon', '95649', 'dahlia-fallon'],
        ['Clips4Sale', 'Clips4Sale: Marisol Price', 'Clips4Sale: Marisol Price', '199605', 'marisol-price'],
        ['Clips4Sale', 'Clips4Sale: Club Stiletto FemDom', 'Clips4Sale: Club Stiletto FemDom', '896', 'club-stiletto-femdom'],
        ['Clips4Sale', 'Clips4Sale: Filthy Fuckers', 'Clips4Sale: Filthy Fuckers', '142821', 'filthy-fuckers'],
        ['Clips4Sale', 'Clips4Sale: KathiaNobiliGirls', 'Clips4Sale: KathiaNobiliGirls', '76113', 'kathianobiligirls'],
        ['Clips4Sale', 'Clips4Sale: Brat Princess 2', 'Clips4Sale: Brat Princess 2', '21233', 'brat-princess-2'],
        ['Clips4Sale', 'Clips4Sale: Nasty Family', 'Clips4Sale: Nasty Family', '82539', 'nasty-family'],
        ['Clips4Sale', 'Clips4Sale: This Boys Dream', 'Clips4Sale: This Boys Dream', '52799', 'this-boy-s-dream'],
        ['Clips4Sale', 'Clips4Sale: That Kinky Girl', 'Clips4Sale: That Kinky Girl', '45475', 'that-kinky-girl'],
        ['Clips4Sale', 'Clips4Sale: Hot Milf and Taboo Fetishes', 'Clips4Sale: Hot Milf and Taboo Fetishes', '14439', 'hot-milf-and-taboo-fetishes'],
        ['Clips4Sale', 'Clips4Sale: Bossy Girls', 'Clips4Sale: Bossy Girls', '107974', 'bossy-girls'],
        ['Clips4Sale', 'Clips4Sale: Helena Price Taboo', 'Clips4Sale: Helena Price Taboo', '127013', 'helena-price-taboo'],
        ['Clips4Sale', 'Clips4Sale: TgirlOneGuy', 'Clips4Sale: TgirlOneGuy', '120767', 'tgirloneguy'],
        ['Clips4Sale', 'Clips4Sale: Evans Feet', 'Clips4Sale: Evans Feet', '229967', 'evansfeet'],
        ['Clips4Sale', 'Clips4Sale: Lady X', 'Clips4Sale: Lady X', '2582', 'lady-x'],
        ['Clips4Sale', 'Clips4Sale: Mistress Courtneys Fetish Lair', 'Clips4Sale: Mistress Courtneys Fetish Lair', '97973', 'mistress-courtneys-fetish-lair'],
        ['Clips4Sale', 'Clips4Sale: Sara Saint', 'Clips4Sale: Sara Saint', '162999', 'sara-saint'],
        ['Clips4Sale', 'Clips4Sale: Kenny Kong AMWF Porn', 'Clips4Sale: Kenny Kong AMWF Porn', '105418', 'kenny-kong-amwf-porn'],
        ['Clips4Sale', 'Clips4Sale: Annabelle Rogers', 'Clips4Sale: Annabelle Rogers', '140743', 'annabelle-rogers-taboo'],
        ['Clips4Sale', 'Clips4Sale: Maternal Seductions', 'Clips4Sale: Maternal Seductions', '32590', 'maternal-seductions'],
        ['Clips4Sale', 'Clips4Sale: Alysa Nylon', 'Clips4Sale: Alysa Nylon', '270421', 'alysa-nylon'],
        ['Clips4Sale', 'Clips4Sale: Bound2Burst', 'Clips4Sale: Bound2Burst', '8916', 'bound2burst-female-desperation'],
        ['Clips4Sale', 'Clips4Sale: Madame Brooks Sinister Latex Studio', 'Clips4Sale: Madame Brooks Sinister Latex Studio', '153193', 'madame-brooks-sinister-latex-studio'],
        ['Clips4Sale', 'Clips4Sale: Ashley Albans Fetish Fun', 'Clips4Sale: Ashley Albans Fetish Fun', '71774', 'ashley-alban-s-fetish-fun'],
        ['Clips4Sale', 'Clips4Sale: Femdom Delilah', 'Clips4Sale: Femdom Delilah', '254391', 'femdom-delilah'],
        ['Clips4Sale', 'Clips4Sale: Mistress Jessica Starling', 'Clips4Sale: Mistress Jessica Starling', '146727', 'mistress-jessica-starling'],
        ['Clips4Sale', 'Clips4Sale: Little Puck Perversions', 'Clips4Sale: Little Puck Perversions', '112222', 'little-puck-perversions'],
        ['Clips4Sale', 'Clips4Sale: TamyStarly CBT and Bootjobs', 'Clips4Sale: TamyStarly CBT and Bootjobs', '209723', 'tamystarly-cbt-and-bootjobs'],
        ['Clips4Sale', 'Clips4Sale: Crystal Knight', 'Clips4Sale: Crystal Knight', '96651', 'crystal-knight'],
        ['Clips4Sale', 'Clips4Sale: CinematicKink', 'Clips4Sale: CinematicKink', '215717', 'cinematickink'],
        ['Clips4Sale', 'Clips4Sale: SofiaStudios', 'Clips4Sale: SofiaStudios', '173843', 'sofiastudios'],
        ['Clips4Sale', 'Clips4Sale: Kendra James Fetish Experience', 'Clips4Sale: Kendra James Fetish Experience', '11330', 'kendra-james-fetish-exxxpierence'],
        ['Clips4Sale', 'Clips4Sale: Alicia Silvers 1111 Customs', 'Clips4Sale: Alicia Silvers 1111 Customs', '151073', 'alicia-silvers-1111-customs'],
        # ~ ['Clips4Sale', 'Clips4Sale: ', 'Clips4Sale: ', '', ''],
        # ~ ['Clips4Sale', 'Clips4Sale: ', 'Clips4Sale: ', '', ''],
    ]

    name = 'Clips4Sale'

    url = 'https://www.clips4sale.com'

    selector_map = {
        'external_id': r'studio\/.*\/(\d+)\/',
        'pagination': ''
    }

    def start_requests(self):
        link = self.url
        meta = {}
        for site in self.sites:
            meta['network'] = site[0]
            meta['parent'] = site[1]
            meta['storedsite'] = site[2]
            meta['store'] = site[3]
            meta['storename'] = site[4]
            meta['page'] = self.page

            yield scrapy.Request(url=self.get_next_page_url(link, self.page, meta['store'], meta['storename']), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def parse(self, response, **kwargs):
        scenes = self.get_scenes(response)
        count = 0
        for scene in scenes:
            count += 1
            yield scene

        if count:
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                meta = response.meta
                meta['page'] = meta['page'] + 1
                print('NEXT PAGE: ' + str(meta['page']))
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page'], meta['store'], meta['storename']), callback=self.parse, meta=meta)

    def get_next_page_url(self, base, page, store, storename):
        # ~ url = f"https://www.clips4sale.com/studio/{store}/{storename}/Cat0-AllCategories/Page{str(page)}/C4SSort-added_at/Limit24/?onlyClips=true&_data=routes%2Fstudio.$id_.$studioSlug.$"
        url = f"https://www.clips4sale.com/en/studio/{store}/{storename}/Cat0-AllCategories/Page{str(page)}/C4SSort-added_at/Limit24/?onlyClips=true&_data=routes%2F($lang).studio.$id_.$studioSlug.$"
        return url

    def get_scenes(self, response):
        jsondata = response.json()
        jsondata = jsondata['clips']
        for scene in jsondata:
            item = SceneItem()
            item['title'] = self.cleanup_title(scene['title'])
            item['id'] = scene['clipId']
            if "description" in scene and scene['description']:
                item['description'] = self.cleanup_description(re.sub('<[^<]+?>', '', scene['description']))
            else:
                item['description'] = ''
            item['image'] = self.format_link(response, scene['previewLink']).replace(" ", "%20")
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            if scene['cdn_preview_link']:
                item['trailer'] = self.format_link(response, scene['cdn_preview_link']).replace(" ", "%20")
            else:
                item['trailer'] = ""
            scene_date = self.parse_date(scene['dateDisplay'], date_formats=['%m/%d/%y %h:%m %p']).strftime('%Y-%m-%d')
            item['date'] = ""
            if scene_date:
                item['date'] = scene_date
            item['url'] = f"https://www.clips4sale.com{scene['link']}"
            item['tags'] = []
            if "related_category_links" in scene and scene['related_category_links']:
                for tag in scene['related_category_links']:
                    if "category" in tag:
                        item['tags'].append(tag['category'])
                    if "clean_name" in tag:
                        item['tags'].append(string.capwords(tag['clean_name']))
            if "keyword_links" in scene and scene['keyword_links']:
                for tag in scene['keyword_links']:
                    if "keyword" in tag:
                        item['tags'].append(string.capwords(tag['keyword']))
            if scene['duration']:
                item['duration'] = str(int(scene['duration']) * 60)
            item['site'] = self.get_site(response)
            item['parent'] = self.get_parent(response)
            item['network'] = self.get_network(response)
            item['performers'] = self.get_performers(response)

            yield self.check_item(item, self.days)

    def get_site(self, response):
        meta = response.meta
        if "Missa X" in meta['storedsite']:
            title = self.process_xpath(response, self.get_selector_map('title')).get()
            if "allherluv" in title.lower():
                return "All Her Luv"
            if "missax" in title.lower():
                return "Missa X"
            if "apovstory" in title.lower():
                return "A POV Story"

        if meta['storedsite']:
            return meta['storedsite']
        return tldextract.extract(response.url).domain

    def get_parent(self, response):
        meta = response.meta
        if meta['parent']:
            return meta['parent']
        return tldextract.extract(response.url).domain

    def get_network(self, response):
        meta = response.meta
        if meta['network']:
            return meta['network']
        return tldextract.extract(response.url).domain

    def get_performers(self, response):
        if "alysa-nylon" in response.url:
            return ['Alysa Nylon']
        if "annabelle-rogers" in response.url:
            return ['Annabelle Rogers']
        if "astrodomina" in response.url:
            return ['AstroDomina']
        if "andrea-rosu-s" in response.url:
            return ['Andrea Rosu']
        if "crystal-knight" in response.url:
            return ['Crystal Knight']
        if "daisys-desires" in response.url:
            return ['Daisy Haze']
        if "mistress-jessica-starling" in response.url:
            return ['Jessica Starling']
        if "divine-goddess-amber" in response.url:
            return ['Divine Goddess Amber']
        if "addie-juniper" in response.url:
            return ['Addie Juniper']
        if "superior-lana-blade" in response.url:
            return ['Lana Blade']
        if "mistress-euryale" in response.url:
            return ['Elis Euryale']
        if "mandy-marx" in response.url:
            return ['Mandy Marx']
        if "marisol-price" in response.url:
            return ['Marisol Price']
        if "princess-sasha-foxxx" in response.url:
            return ['Sasha Foxxx']
        if "dahlia-fallon" in response.url:
            return ['Dahlia Fallon']
        if "mistress-courtneys-fetish-lair" in response.url:
            return ['Mistress Courtney']
        if "evansfeet" in response.url:
            return ['Lis Evans']
        if "mean-wolf" in response.url:
            return ['Meana Wolf']
        if "little-puck-perversions" in response.url:
            return ['Little Puck']
        if "milf-jan-seduces" in response.url:
            return ['Jan Burton']
        if "natalie-wonder" in response.url:
            return ['Natalie Wonder']
        if "princess-camryn" in response.url:
            return ['Princess Camryn']
        if "tammie-madison" in response.url:
            return ['Tammie Madison']
        if "tgirloneguy" in response.url:
            return ['Kendall Penny']
        if "sara-saint" in response.url:
            return ['Sara Saint']
        if "tamystarly-cbt" in response.url:
            return ['Tamy Starly']
        return []
