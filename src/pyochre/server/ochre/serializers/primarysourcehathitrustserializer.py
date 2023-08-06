import os.path
import logging
from hashlib import md5
import io
import zipfile
import re
import csv
import tempfile
from rest_framework.serializers import HyperlinkedIdentityField, FileField, BooleanField, CharField
from django.conf import settings
from rdflib import Namespace
from pyochre.server.ochre.models import PrimarySource, Query, Annotation
from pyochre.server.ochre.serializers import OchreSerializer, MaterialSerializer
from rdflib import Graph, BNode, URIRef, Literal, Dataset
from rdflib.namespace import RDF, RDFS, XSD, Namespace
from pyochre.server.ochre.models import PrimarySource, User
from pairtree import PairtreeStorageFactory
from geopy.geocoders import Nominatim
from pyochre.utils import rdf_store
from pyochre.primary_sources import create_domain


logger = logging.getLogger(__name__)


OCHRE = Namespace(settings.OCHRE_NAMESPACE)


if settings.USE_CELERY:
    from celery import shared_task
else:
    def shared_task(func):
        return func

location_codes = {}
for line in """aa 	Albania
abc 	Alberta
-ac 	Ashmore and Cartier Islands
aca 	Australian Capital Territory
ae 	Algeria
af 	Afghanistan
ag 	Argentina
-ai 	Anguilla
ai 	Armenia (Republic)
-air 	Armenian S.S.R.
aj 	Azerbaijan
-ajr 	Azerbaijan S.S.R.
aku 	Alaska
alu 	Alabama
am 	Anguilla
an 	Andorra
ao 	Angola
aq 	Antigua and Barbuda
aru 	Arkansas
as 	American Samoa
at 	Australia
au 	Austria
aw 	Aruba
ay 	Antarctica
azu 	Arizona
ba 	Bahrain
bb 	Barbados
bcc 	British Columbia
bd 	Burundi
be 	Belgium
bf 	Bahamas
bg 	Bangladesh
bh 	Belize
bi 	British Indian Ocean Territory
bl 	Brazil
bm 	Bermuda Islands
bn 	Bosnia and Herzegovina
bo 	Bolivia
bp 	Solomon Islands
br 	Burma
bs 	Botswana
bt 	Bhutan
bu 	Bulgaria
bv 	Bouvet Island
bw 	Belarus
-bwr 	Byelorussian S.S.R.
bx 	Brunei
ca 	Caribbean Netherlands
cau 	California
cb 	Cambodia
cc 	China
cd 	Chad
ce 	Sri Lanka
cf 	Congo (Brazzaville)
cg 	Congo (Democratic Republic)
ch 	China (Republic : 1949- )
ci 	Croatia
cj 	Cayman Islands
ck 	Colombia
cl 	Chile
cm 	Cameroon
-cn 	Canada
co 	Curaçao
cou 	Colorado
-cp 	Canton and Enderbury Islands
cq 	Comoros
cr 	Costa Rica
-cs 	Czechoslovakia
ctu 	Connecticut
cu 	Cuba
cv 	Cabo Verde
cw 	Cook Islands
cx 	Central African Republic
cy 	Cyprus
-cz 	Canal Zone
dcu 	District of Columbia
deu 	Delaware
dk 	Denmark
dm 	Benin
dq 	Dominica
dr 	Dominican Republic
ea 	Eritrea
ec 	Ecuador
eg 	Equatorial Guinea
em 	Timor-Leste
enk 	England
er 	Estonia
-err 	Estonia
es 	El Salvador
et 	Ethiopia
fa 	Faroe Islands
fg 	French Guiana
fi 	Finland
fj 	Fiji
fk 	Falkland Islands
flu 	Florida
fm 	Micronesia (Federated States)
fp 	French Polynesia
fr 	France
fs 	Terres australes et antarctiques françaises
ft 	Djibouti
gau 	Georgia
gb 	Kiribati
gd 	Grenada
-ge 	Germany (East)
gg 	Guernsey
gh 	Ghana
gi 	Gibraltar
gl 	Greenland
gm 	Gambia
-gn 	Gilbert and Ellice Islands
go 	Gabon
gp 	Guadeloupe
gr 	Greece
gs 	Georgia (Republic)
-gsr 	Georgian S.S.R.
gt 	Guatemala
gu 	Guam
gv 	Guinea
gw 	Germany
gy 	Guyana
gz 	Gaza Strip
hiu 	Hawaii
-hk 	Hong Kong
hm 	Heard and McDonald Islands
ho 	Honduras
ht 	Haiti
hu 	Hungary
iau 	Iowa
ic 	Iceland
idu 	Idaho
ie 	Ireland
ii 	India
ilu 	Illinois
im 	Isle of Man
inu 	Indiana
io 	Indonesia
iq 	Iraq
ir 	Iran
is 	Israel
it 	Italy
-iu 	Israel-Syria Demilitarized Zones
iv 	Côte d'Ivoire
-iw 	Israel-Jordan Demilitarized Zones
iy 	Iraq-Saudi Arabia Neutral Zone
ja 	Japan
je 	Jersey
ji 	Johnston Atoll
jm 	Jamaica
-jn 	Jan Mayen
jo 	Jordan
ke 	Kenya
kg 	Kyrgyzstan
-kgr 	Kirghiz S.S.R.
kn 	Korea (North)
ko 	Korea (South)
ksu 	Kansas
ku 	Kuwait
kv 	Kosovo
kyu 	Kentucky
kz 	Kazakhstan
-kzr 	Kazakh S.S.R.
lau 	Louisiana
lb 	Liberia
le 	Lebanon
lh 	Liechtenstein
li 	Lithuania
-lir 	Lithuania
-ln 	Central and Southern Line Islands
lo 	Lesotho
ls 	Laos
lu 	Luxembourg
lv 	Latvia
-lvr 	Latvia
ly 	Libya
mau 	Massachusetts
mbc 	Manitoba
mc 	Monaco
mdu 	Maryland
meu 	Maine
mf 	Mauritius
mg 	Madagascar
-mh 	Macao
miu 	Michigan
mj 	Montserrat
mk 	Oman
ml 	Mali
mm 	Malta
mnu 	Minnesota
mo 	Montenegro
mou 	Missouri
mp 	Mongolia
mq 	Martinique
mr 	Morocco
msu 	Mississippi
mtu 	Montana
mu 	Mauritania
mv 	Moldova
-mvr 	Moldavian S.S.R.
mw 	Malawi
mx 	Mexico
my 	Malaysia
mz 	Mozambique
-na 	Netherlands Antilles
nbu 	Nebraska
ncu 	North Carolina
ndu 	North Dakota
ne 	Netherlands
nfc 	Newfoundland and Labrador
ng 	Niger
nhu 	New Hampshire
nik 	Northern Ireland
nju 	New Jersey
nkc 	New Brunswick
nl 	New Caledonia
-nm 	Northern Mariana Islands
nmu 	New Mexico
nn 	Vanuatu
no 	Norway
np 	Nepal
nq 	Nicaragua
nr 	Nigeria
nsc 	Nova Scotia
ntc 	Northwest Territories
nu 	Nauru
nuc 	Nunavut
nvu 	Nevada
nw 	Northern Mariana Islands
nx 	Norfolk Island
nyu 	New York (State)
nz 	New Zealand
ohu 	Ohio
oku 	Oklahoma
onc 	Ontario
oru 	Oregon
ot 	Mayotte
pau 	Pennsylvania
pc 	Pitcairn Island
pe 	Peru
pf 	Paracel Islands
pg 	Guinea-Bissau
ph 	Philippines
pic 	Prince Edward Island
pk 	Pakistan
pl 	Poland
pn 	Panama
po 	Portugal
pp 	Papua New Guinea
pr 	Puerto Rico
-pt 	Portuguese Timor
pw 	Palau
py 	Paraguay
qa 	Qatar
qea 	Queensland
quc 	Québec (Province)
rb 	Serbia
re 	Réunion
rh 	Zimbabwe
riu 	Rhode Island
rm 	Romania
ru 	Russia (Federation)
-rur 	Russian S.F.S.R.
rw 	Rwanda
-ry 	Ryukyu Islands, Southern
sa 	South Africa
-sb 	Svalbard
sc 	Saint-Barthélemy
scu 	South Carolina
sd 	South Sudan
sdu 	South Dakota
se 	Seychelles
sf 	Sao Tome and Principe
sg 	Senegal
sh 	Spanish North Africa
si 	Singapore
sj 	Sudan
-sk 	Sikkim
sl 	Sierra Leone
sm 	San Marino
sn 	Sint Maarten
snc 	Saskatchewan
so 	Somalia
sp 	Spain
sq 	Eswatini
sr 	Surinam
ss 	Western Sahara
st 	Saint-Martin
stk 	Scotland
su 	Saudi Arabia
-sv 	Swan Islands
sw 	Sweden
sx 	Namibia
sy 	Syria
sz 	Switzerland
ta 	Tajikistan
-tar 	Tajik S.S.R.
tc 	Turks and Caicos Islands
tg 	Togo
th 	Thailand
ti 	Tunisia
tk 	Turkmenistan
-tkr 	Turkmen S.S.R.
tl 	Tokelau
tma 	Tasmania
tnu 	Tennessee
to 	Tonga
tr 	Trinidad and Tobago
ts 	United Arab Emirates
-tt 	Trust Territory of the Pacific Islands
tu 	Turkey
tv 	Tuvalu
txu 	Texas
tz 	Tanzania
ua 	Egypt
uc 	United States Misc. Caribbean Islands
ug 	Uganda
-ui 	United Kingdom Misc. Islands
-uik 	United Kingdom Misc. Islands
-uk 	United Kingdom
un 	Ukraine
-unr 	Ukraine
up 	United States Misc. Pacific Islands
-ur 	Soviet Union
-us 	United States
utu 	Utah
uv 	Burkina Faso
uy 	Uruguay
uz 	Uzbekistan
-uzr 	Uzbek S.S.R.
vau 	Virginia
vb 	British Virgin Islands
vc 	Vatican City
ve 	Venezuela
vi 	Virgin Islands of the United States
vm 	Vietnam
-vn 	Vietnam, North
vp 	Various places
vra 	Victoria
-vs 	Vietnam, South
vtu 	Vermont
wau 	Washington (State)
-wb 	West Berlin
wea 	Western Australia
wf 	Wallis and Futuna
wiu 	Wisconsin
wj 	West Bank of the Jordan River
wk 	Wake Island
wlk 	Wales
ws 	Samoa
wvu 	West Virginia
wyu 	Wyoming
xa 	Christmas Island (Indian Ocean)
xb 	Cocos (Keeling) Islands
xc 	Maldives
xd 	Saint Kitts-Nevis
xe 	Marshall Islands
xf 	Midway Islands
xga 	Coral Sea Islands Territory
xh 	Niue
-xi 	Saint Kitts-Nevis-Anguilla
xj 	Saint Helena
xk 	Saint Lucia
xl 	Saint Pierre and Miquelon
xm 	Saint Vincent and the Grenadines
xn 	North Macedonia
xna 	New South Wales
xo 	Slovakia
xoa 	Northern Territory
xp 	Spratly Island
xr 	Czech Republic
xra 	South Australia
xs 	South Georgia and the South Sandwich Islands
xv 	Slovenia
xx 	No place, unknown, or undetermined
xxc 	Canada
xxk 	United Kingdom
-xxr 	Soviet Union
xxu 	United States
ye 	Yemen
ykc 	Yukon Territory
-ys 	Yemen (People's Democratic Republic)
-yu 	Serbia and Montenegro
za 	Zambia""".split("\n"):
    toks = line.split()
    location_codes[toks[0]] = " ".join(toks[1:])

@shared_task
def primarysource_from_hathitrust_collection(
        primarysource_id,
        collection_string,
):
    ps = PrimarySource.objects.get(id=primarysource_id)
    gc = Nominatim(user_agent="OCHRE")
    try:
        psf = PairtreeStorageFactory()
        g = Graph(base="http://test/")
        c = csv.DictReader(io.StringIO(collection_string), delimiter="\t")
        for row in c:
            toks = row["htid"].split(".")
            subcollection = toks[0]
            ident = ".".join(toks[1:])
            ht_store = psf.get_store(
                store_dir=os.path.join(
                    settings.HATHITRUST_ROOT,
                    subcollection
                ),
                uri_base=settings.OCHRE_NAMESPACE
            )
            try:
                obj = ht_store.get_object(ident, create_if_doesnt_exist=False)
            except:
                continue
            full_content = []                        
            for subpath in obj.list_parts():
                for fname in obj.list_parts(subpath):
                    if fname.endswith("zip"):
                        with zipfile.ZipFile(
                                obj.get_bytestream(
                                    "{}/{}".format(subpath, fname),
                                    streamable=True
                                )
                        ) as izf:                            
                            for page in sorted(izf.namelist()):
                                if page.endswith("txt"):
                                    txt = izf.read(page).decode("utf-8")
                                    txt = re.sub(r"\-\s*?\n\s*", "", txt)
                                    full_content.append(txt)
                                    
            full_content = "\n".join(full_content)
            # author lang title rights_date_used pub_place imprint
            text = BNode()
            textfile = BNode()
            author = BNode()
            publisher = BNode()
            publication_place = BNode()
            g.add((text, OCHRE["instanceOf"], OCHRE["Text"]))
            g.add((text, OCHRE["hasFile"], textfile))
            g.add((textfile, OCHRE["instanceOf"], OCHRE["TextFile"]))
            ms = MaterialSerializer()
            ret = ms.create({"content" : full_content.encode(), "content_type" : "text"})
            g.add((textfile, OCHRE["hasMaterialId"], Literal(ret["material_id"])))
            if "author" in row:
                g.add((author, OCHRE["hasLabel"], Literal(row["author"])))            
                g.add((text, OCHRE["hasAuthor"], author))
                g.add((author, OCHRE["instanceOf"], OCHRE["Author"]))
            if "imprint" in row:
                g.add((publisher, OCHRE["instanceOf"], OCHRE["Publisher"]))
                g.add((text, OCHRE["hasPublisher"], publisher))
                g.add((publisher, OCHRE["hasLabel"], Literal(row["imprint"])))                
            # if row.get("pub_place", None) in location_codes:
            #     loc = gc.geocode(row["pub_place"])
            #     if loc:
            #         g.add((text, OCHRE["hasLocation"], publication_place))
            #         g.add((publication_place, OCHRE["instanceOf"], OCHRE["Location"]))
            #         g.add((publication_place, OCHRE["hasLatitude"], Literal(loc.latitude)))
            #         g.add((publication_place, OCHRE["hasLongitude"], Literal(loc.longitude))
            #)
                
                #Literal(row["pub_place"])))
            if "rights_date_used" in row:
                if row["rights_date_used"].isdigit():
                    g.add((text, OCHRE["hasDate"], Literal(row["rights_date_used"], datatype=XSD.integer)))
            if "lang" in row:
                g.add((text, OCHRE["inLanguage"], Literal(row["lang"])))
            if "title" in row:
                g.add((text, OCHRE["hasLabel"], Literal(row["title"])))
        g = g.skolemize()
        store = rdf_store(settings=settings)
        dataset = Dataset(store=store, default_graph_base=OCHRE)
        logger.info("Getting the named graph corresponding to the primary source")
        ng = dataset.graph(
            OCHRE["{}_data".format(ps.id)]
        )
        for tr in g:
            ng.add(tr)
        ng.commit()
        dg = dataset.graph(
           OCHRE["{}_domain".format(ps.id)]
        )
        for s, p, o in create_domain(ps):
           dg.add((s, p, o))
        store.commit()
        ps.state = ps.COMPLETE
        ps.save()
    except Exception as e:
        ps.delete()
        raise e
    finally:
        pass


class PrimarySourceHathiTrustSerializer(OchreSerializer):    

    name = CharField(
        help_text="The name for this primary source"
    )
    collection_file = FileField(
        write_only=True,
        help_text="A collection CSV file downloaded from the HathiTrust interface"
    )
    # force = BooleanField(
    #     required=False,
    #     write_only=True,
    #     allow_null=True,
    #     default=False,
    #     help_text="Overwrite any existing primary source of the same name and creator"
    # )
    
    class Meta:
        model = PrimarySource
        slug = "From a HathiTrust collection"
        fields = [
            "name",
            "force",
            "collection_file",
            "created_by"
        ]

    def create(self, validated_data):
        if validated_data.get("force", False):
            for existing in PrimarySource.objects.filter(
                    name=validated_data["name"],
                    created_by=validated_data["created_by"]
            ):
                existing.delete()
        obj = PrimarySource(
            name=validated_data["name"],
            created_by=validated_data["created_by"],
            state=PrimarySource.PROCESSING,
            message="This primary source is being processed..."
        )
        obj.save()
        primarysource_from_hathitrust_collection.delay(
            obj.id,
            validated_data["collection_file"].read().decode("utf-8")
        )
        return obj

    def update(self, instance, validated_data):        
        super(
            PrimarySourceSerializer,
            self
        ).update(
            instance,
            validated_data
        )
        instance.save(**validated_data)
        return instance
    
