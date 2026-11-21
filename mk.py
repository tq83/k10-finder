import json
H="https://www.hemmings.com/classifieds/listing/"
E="https://www.ebay.com/itm/"
def e(id,y,m,eng,tr,price,mi,seller,notes,imgs,end):
    return dict(source="eBay Motors",url=E+id,year_make_model=y,engine=eng,transmission=tr,price=price,auction_end=end,mileage=mi,location="United States (city not shown in text)",seller=seller,notes=notes,photos=imgs,verified="opened listing page")
I=lambda l:["https://i.ebayimg.com/images/g/%s/s-l1600.webp"%x for x in l]
d=[
e("147690453952","1977 Chevrolet K-10","","350ci V8","4-speed manual","$30,110 BIN/Best Offer ($250 deposit)","33,621","grautogallery (93.1%, 278)","Dealer; True Blue; stock B6865 K (same unit as Hemmings GR Auto Gallery 1977 K10)",I(["eUoAAeSwVnJq5UMd","Ne0AAeSwOXZq5UMd","7-cAAeSwfjFq5UMd","dEIAAeSwomBq5UMd","7TwAAeSwWKVq5UMd","7rYAAeSwXX1q5UMd"]),"Listing ends ~6d11h (Fri 7:27 PM)"),
e("257859877806","1967 Chevrolet K10","","350ci V8","Turbo 350 automatic","$47,999 BIN/Best Offer","62,385","Gearhead Classics (100%, 961)","Red; dealer; Secure Purchase",I(["SzAAAeSwYHpq2WcW","QzUAAeSwUOdq2WcV","RscAAeSwQYhq2WcW","O3sAAeSw1Tpq2WcW","P6kAAeSwA~tq2WcW","O3kAAeSw1Tpq2WcW"]),"~4d11h left (Wed 7:34 PM)"),
e("128203915958","1979 Chevrolet K-10 Bonanza short bed 4x4","","350ci 4bbl V8","TH350 automatic","$36,500 BIN/Best Offer ($250 deposit)","45,380","Classic Auto Mall, Morgantown PA (classicautomall, 100%)","Nicely optioned, Rancho RS5000 shocks; same unit as Hemmings/Classic.com Morgantown 1979",I(["z18AAeSwAwZq6oih","zecAAeSwbNlq6oih","0bMAAeSwSO1q6oih","yyMAAeSwejxq6oih","0ZAAAeSwadlq6oii","x9IAAeSwXmpq6oih"]),"~2d10h left (Mon 6:46 PM)"),
e("227619269653","1984 Chevrolet K10 Silverado 4x4","","V8 crate engine (per title)","Automatic","$30,900 BIN","108,315","AP Vintage Motors (266)","Clean title; AC; crate engine swap",I(["DWMAAeSw-Mdqert8","Ao8AAeSwCclqert7","mnsAAeSwnu5qert7","gTcAAeSwO2lqert7","mnoAAeSwnu5qert7","wwcAAeSwJgVqert7"]),"~3d8h left (Tue 4:21 PM)"),
e("147662620454","1971 Chevrolet K-10 4x4","","350ci V8","Automatic","$39,995 BIN/Best Offer","97,158","classicsandbeyond (83.3%, 44)","Clean title",I(["VDIAAeSwsdVq6mpl","VMAAAeSw9uxq6mpl","TMgAAeSwE9Zq6mpl","S9IAAeSwvIxq6mpl","S~gAAeSw6B5q6mpl","U1wAAeSw4fpq6mpl"]),"~11d4h left (12/02 12:50 PM)"),
]
def h(slug,y,eng,tr,price,mi,loc,seller,notes,img,v="opened; price = first $ figure on page, verify"):
    return dict(source="Hemmings",url=H+slug,year_make_model=y,engine=eng,transmission=tr,price=price,auction_end=None,mileage=mi,location=loc,seller=seller,notes=notes,photos=img,verified=v)
d+=[
h("1970-chevrolet-k10-de-witt-ia-2977864","1970 Chevrolet K10 4x4 8-ft bed","350 V8 (Edelbrock/Holley, Hooker headers)","4-speed manual","$39,997","not stated (dealer says exempt)","De Witt, IA","Thiel Motor Sales (dealer)","Blue/white two-tone, Rough Country lift, 33in BFG KO, dealer ad is hype-heavy; 'good driver not show piece'",["https://assets.hemmings.com/uimage/162220248-770-0.jpg"]),
h("1976-chevrolet-k10-lithia-springs-ga-2977185","1976 Chevrolet K10 4x4 (red)","350 V8","4-speed automatic (per ad)","$50,495 (first $ shown; other figures $29,495/$47,495 - verify)","n/a","Lithia Springs, GA","dealer (not captured)","Dana 44 front/12-bolt rear",["https://assets.hemmings.com/uimage/162118484-770-0.jpg"],"opened; price unclear"),
h("1979-chevrolet-k10-morgantown-pa-2976738","1979 Chevrolet K-10 Bonanza SWB 4x4","350","TH350 auto","$36,500","45,380","Morgantown, PA","Classic Auto Mall","Same as eBay 128203915958",[]),
h("1967-chevrolet-k10-north-east-pa-2976033","1967 Chevrolet K10","n/a","n/a","$43,991 (first $ shown, other $40,483/$38,983 - verify)","n/a","North East, PA","dealer (not captured)","Not verified 4x4/details",[]),
h("1977-chevrolet-k10-grand-rapids-mi-2975886","1977 Chevrolet K10 (white/blue)","n/a","Manual","see eBay $30,110","33,621","Grand Rapids, MI","lovingtheclassics / GR Auto Gallery","Same as eBay 147690453952",["https://assets.hemmings.com/uimage/162004571-770-0.jpg"]),
h("1971-chevrolet-k10-bellevue-wa-2974508","1971 Chevrolet K10 Cheyenne 4x4 resto-mod","n/a","Automatic","$69,950 or $49,950 on page - verify","555 (odometer field)","Bellevue, WA","Park Place LTD (dealer)","Black over black; resto-modded",["https://assets.hemmings.com/uimage/161899708-770-0.jpg"]),
h("1985-chevrolet-k10-runnemede-nj-2974306","1985 Chevrolet K10 4x4 (blue)","n/a","n/a","$26,000 (other $59,000 on page - verify)","83,593","Runnemede, NJ","Gateway Classic Cars Philadelphia","VIN 1GCEK14H4FF324855",["https://assets.hemmings.com/uimage/161882038-770-0.jpg"]),
h("1986-chevrolet-k10-mankato-mn-2973426","1986 Chevrolet K10 Scottsdale 4x4 (russet)","350 V8","700R4 auto","$30,175 (other $21,900 - verify)","60,761","Mankato, MN","carpartsnos (dealer)","Mahogany interior",["https://assets.hemmings.com/uimage/161989624-770-0.jpg"]),
h("1987-chevrolet-k10-morgantown-pa-2972117","1987 Chevrolet K10 Silverado SWB 4x4 (red)","TBI V8 likely (not confirmed)","Automatic","$60,000 first on page - likely OUT of range, verify","82,857","Morgantown, PA","Classic Auto Mall","VIN 1GCEV14K2HF382484",["https://assets.hemmings.com/uimage/161684057-770-0.jpg"]),
h("1986-chevrolet-k10-commerce-twp-mi-2969818","1986 Chevrolet K10 (blue/white)","n/a","Automatic","$40,110 (other $17,110 - verify)","124 shown (likely wrong/TMU)","Commerce Twp, MI","lovingtheclassics","",["https://assets.hemmings.com/uimage/161497667-770-0.jpg"]),
h("1985-chevrolet-k10-grand-rapids-mi-2968719","1985 Chevrolet K10 Custom Deluxe (white/red)","n/a","Automatic","$26,110","74,386","Grand Rapids, MI","GR Auto Gallery","",["https://assets.hemmings.com/uimage/161397698-770-0.jpg"]),
]
C="https://www.classic.com/search?q=k10"
d+=[
dict(source="Classic.com (aggregator, from search list, not opened)",url=C,year_make_model="1986 Chevrolet K10 Long Bed",engine="n/a",transmission="Manual",price="$48,495",mileage="51k",location="Fort Worth, TX",seller="Streetside Classics DFW",notes="listed Nov 13, 2026; custom",photos=[],verified="search list only"),
dict(source="Classic.com (aggregator, from search list, not opened)",url=C,year_make_model="1970 Chevrolet K10 Step Side w/ fender spare",engine="n/a",transmission="Manual",price="$35,950",mileage="TMU",location="Brookings, SD",seller="B & B Auto Sales",notes="original/highly original; listed Nov 6",photos=[],verified="search list only"),
]
FB=lambda id,t,p,loc,img,n="": dict(source="Facebook Marketplace (no sign-in, search card only)",url="https://www.facebook.com/marketplace/item/%s/"%id,year_make_model=t,price=p,location=loc,photos=[img],notes=n,verified="search card only; not opened")
fb=[("29946723918268547","1981 Chevy k10","$20,000 (was $24,500)","Goodyear, AZ"),
("1095151700165442","1976 Chevy K10 lifted 4x4","$20,000","Rimrock, AZ"),
("2058458351531803","1979 Chevrolet 1500 SWB (K?)","$20,000","Kingman, AZ"),
("4469633756641975","1977 Chevrolet k10 Custom","$24,000","Prescott, AZ"),
("969900468923130","1985 Chevrolet Silverado 1500 reg cab","$26,000","Queen Creek, AZ"),
("29014812801486365","1987 Chevrolet Silverado 1500 LS 8ft (was 29,500)","$27,500","Apache Junction, AZ"),
("936549639389056","1985 Chevrolet Silverado 1500 SWB (was 42,500)","$39,500","Fountain Hills, AZ"),
("1426840322813785","1987 Chevrolet Silverado (at Dino's)","$45,000","Tucson, AZ"),
("4346952488891123","73 square body Chevy 4x4 (was 23,000)","$20,000","Temecula, CA")]
imgs={}
import re
txt=open('/workspace/k10-dashboard/fbimg.txt').read() if False else ""
d+=[dict(source="Facebook Marketplace (search card only, no sign-in)",url="https://www.facebook.com/marketplace/item/%s/"%i,year_make_model=t,price=p,location=l,photos=[],notes="4x4 not confirmed; not opened. Thumbnail fbcdn URLs omitted (expiring)",verified="search card only") for i,t,p,l in fb]
json.dump(d,open('/workspace/k10-dashboard/scan_browser_nov21.json','w'),indent=1)
print(len(d))
