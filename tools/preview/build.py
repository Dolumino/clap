"""Build preview.html: the real Clap app (../clap-site/index.html) running on sample data,
so it can be published as an artifact and reviewed before anything goes live."""
import base64, colorsys, io, json, re, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).parent
import os
APP = Path(os.environ.get("CLAP_APP", str(HERE.parent.parent / "index.html")))
OUT = Path(os.environ.get("CLAP_OUT", str(HERE / "preview.html")))
NOTE = sys.argv[1] if len(sys.argv) > 1 else "Sample data, not live"

DJ = "/usr/share/fonts/truetype/dejavu/"
def font(n, s):
    try: return ImageFont.truetype(DJ + n, s)
    except Exception: return ImageFont.load_default()
def rgb(h, s, l):
    r, g, b = colorsys.hls_to_rgb((h % 360) / 360, l, s); return (int(r * 255), int(g * 255), int(b * 255))
def uri(im, fmt="JPEG", q=78):
    b = io.BytesIO(); im.save(b, fmt, quality=q) if fmt == "JPEG" else im.save(b, fmt, optimize=True)
    return f"data:image/{fmt.lower()};base64," + base64.b64encode(b.getvalue()).decode()

# ---------- Sample films (real titles and directors; artwork is generated) ----------
FILMS = [
 (1,"Anatomy of a Fall","Anatomie d'une chute","2023","Justine Triet",151,[18,80,9648],7.7,3400,"fr",200,"A trial. A marriage. A fall.","A writer is tried for her husband's death after he falls from their isolated chalet. Their partially sighted son is the only witness.",[1,3,18]),
 (2,"Past Lives","Past Lives","2023","Celine Song",106,[18,10749],7.8,2600,"en",30,"","Two childhood friends from Seoul meet again twenty years later in New York, one of them now married.",[3,2]),
 (3,"Arrival","Arrival","2016","Denis Villeneuve",116,[878,18,9648],7.6,18000,"en",215,"Why are they here?","A linguist is asked to talk with visitors whose ships hover over twelve cities. Learning their language changes how she experiences time.",[1,2]),
 (4,"Perfect Days","Perfect Days","2023","Wim Wenders",124,[18],7.8,1300,"ja",95,"","A Tokyo public-toilet cleaner keeps the same calm routine every day: cassettes, books, trees. Small disruptions hint at his past.",[4,15]),
 (5,"Parasite","기생충","2019","Bong Joon-ho",132,[53,35,18],8.5,19000,"ko",140,"Act like you own the place.","A struggling family cons its way, one job at a time, into a wealthy household. Then the house gives up a secret of its own.",[2,3]),
 (6,"In the Mood for Love","花樣年華","2000","Wong Kar-wai",98,[18,10749],8.1,2900,"zh",355,"","In 1960s Hong Kong, two neighbours learn their spouses are having an affair and drift into something they refuse to name.",[4,18]),
 (7,"Spirited Away","千と千尋の神隠し","2001","Hayao Miyazaki",125,[16,10751,14],8.5,17000,"ja",175,"","A sulky ten-year-old wanders into a bathhouse for spirits and has to work there to free her parents, who have been turned into pigs.",[1]),
 (8,"Before Sunrise","Before Sunrise","1995","Richard Linklater",101,[10749,18],7.7,4200,"en",45,"","A young American and a French student meet on a train and spend one night walking and talking through Vienna.",[2,20]),
 (9,"Portrait of a Lady on Fire","Portrait de la jeune fille en feu","2019","Céline Sciamma",122,[18,10749,36],8.1,2700,"fr",15,"","On an island in 18th-century Brittany, a painter must secretly portray a woman who refuses to pose.",[3,4]),
 (10,"Amélie","Le Fabuleux Destin d'Amélie Poulain","2001","Jean-Pierre Jeunet",122,[35,10749],7.9,11500,"fr",0,"","A shy Montmartre waitress quietly engineers small joys for the people around her.",[1,3,12]),
 (11,"Mad Max: Fury Road","Mad Max: Fury Road","2015","George Miller",120,[28,12,878],7.6,22000,"en",25,"What a lovely day.","A drifter and a rebel commander flee across the wasteland in a war rig, with a warlord's entire army behind them.",[7,1]),
 (12,"Paddington 2","Paddington 2","2017","Paul King",103,[35,12,10751],7.5,2800,"en",210,"","A polite bear takes odd jobs to buy a pop-up book for his aunt, gets framed for stealing it and wins over an entire prison.",[3,5]),
 (13,"The Thing","The Thing","1982","John Carpenter",109,[27,878,9648],8.0,7000,"en",190,"Man is the warmest place to hide.","An Antarctic research team takes in a shape-shifting creature that can imitate any of them. Trust collapses fast.",[16,2]),
 (14,"Cléo from 5 to 7","Cléo de 5 à 7","1962","Agnès Varda",90,[18],7.6,600,"fr",0,"","A singer wanders Paris in near real time while waiting for test results.",[4,15,18]),
]
PROVIDERS = ["Netflix","Amazon Prime Video","Canal+","MUBI","Disney Plus","Apple TV+","Max","Paramount Plus","Arte","France TV",
             "TF1+","M6+","Universciné","FilmoTV","LaCinetek","Shadowz","Rakuten TV","Tënk","Benshi","Crunchyroll",
             "ADN","Pluto TV","Molotov TV","YouTube Premium","Google Play Movies","Hayu","Midnight Pulp","Insomnia","Spamflix","Plex",
             "Cinémas à la demande","Outbuster","Sooner","BrutX","Filmin","Rakuten Viki","Bouygues VOD","Orange VOD","Free VOD","Lumni"]

def poster(f, w=300, h=450):
    hue = f[10]; im = Image.new("RGB", (w, h)); d = ImageDraw.Draw(im)
    for i in range(h): d.line([(0, i), (w, i)], fill=rgb(hue, .5, .12 + .22 * (1 - i / h)))
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).ellipse([w*.15, h*.12, w*1.05, h*.72], fill=255)
    im.paste(Image.new("RGB", (w, h), rgb(hue + 25, .6, .55)), (0, 0), m.filter(ImageFilter.GaussianBlur(26)))
    d = ImageDraw.Draw(im); words = f[1].upper().split(); lines = []; cur = ""
    for wd in words:
        if len(cur + " " + wd) > 11 and cur: lines.append(cur); cur = wd
        else: cur = (cur + " " + wd).strip()
    lines.append(cur); size = 44 if max(map(len, lines)) <= 8 else 33
    ft = font("DejaVuSansCondensed-Bold.ttf", size); y = h - 42 - len(lines) * (size + 3)
    for l in lines: d.text((22, y), l, font=ft, fill="white"); y += size + 3
    d.text((23, h - 34), f[4].upper(), font=font("DejaVuSans.ttf", 11), fill="white")
    return uri(im)
def backdrop(f):
    hue, w, h = f[10], 480, 270; im = Image.new("RGB", (w, h)); d = ImageDraw.Draw(im)
    for x in range(w): d.line([(x, 0), (x, h)], fill=rgb(hue + x / 30, .4, .18 + .25 * x / w))
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).ellipse([w*.45, -h*.2, w*1.1, h*.9], fill=200)
    im.paste(Image.new("RGB", (w, h), rgb(hue + 30, .55, .6)), (0, 0), m.filter(ImageFilter.GaussianBlur(40)))
    return uri(im, q=70)
def logo(i, name):
    im = Image.new("RGB", (64, 64), rgb(i * 47, .55, .38)); d = ImageDraw.Draw(im); ft = font("DejaVuSans-Bold.ttf", 30)
    ch = name[0].upper(); tw = d.textlength(ch, font=ft); d.text(((64 - tw) / 2, 12), ch, font=ft, fill="white")
    return uri(im, "PNG")

images = {}
films = []
for f in FILMS:
    images[f"/poster{f[0]}.jpg"] = poster(f); images[f"/back{f[0]}.jpg"] = backdrop(f)
    films.append(dict(id=f[0], title=f[1], original_title=f[2], release_date=f[3] + "-01-01", director=f[4], runtime=f[5], genre_ids=f[6],
                      vote_average=f[7], vote_count=f[8], original_language=f[9], tagline=f[11], overview=f[12], prov=f[13],
                      poster_path=f"/poster{f[0]}.jpg", backdrop_path=f"/back{f[0]}.jpg"))
provs = []
for i, n in enumerate(PROVIDERS, 1):
    images[f"/logo{i}.png"] = logo(i, n)
    provs.append(dict(provider_id=i, provider_name=n, logo_path=f"/logo{i}.png", display_priorities={"FR": i}))

import datetime as _dt
_t=_dt.date.today()
SEEN={str(i):(_t-_dt.timedelta(days=d)).isoformat() for i,d in [(7,1),(12,3),(11,9),(13,23),(14,76),(6,248),(4,0)]}
seed = {"seen": SEEN, "cfg": {"key": "preview", "region": "FR", "lang": "en-US"},
        "s": {"mood": ["thoughtful", "moved"], "who": "duo", "genres": [], "fame": 2, "era": [1920, 2026], "image": "any", "len": "any", "lang": "any", "plats": [1, 2, 3, 13], "added": [13, 18], "only": False},
        "lists": [{"id": "fav", "name": "Favorites", "films": [7, 5, 3]}, {"id": "l1", "name": "Date nights", "films": [8, 6, 2]}, {"id": "l2", "name": "Sunday afternoons", "films": [10, 4]}],
        "meta": {str(f["id"]): {"id": f["id"], "t": f["title"], "y": f["release_date"][:4], "poster": f["poster_path"], "d": f["director"]} for f in films if f["id"] in (7, 5, 3, 8, 6, 2, 10, 4, 11, 12, 13, 14)}}

MOCK = r"""<script>
/* Clap preview: answers TMDB requests with sample data. Not part of the live app. */
(function(){
const D=__DATA__;
window.__CLAP_IMG=(size,path)=>D.images[path]||"";
const KEY="clap.preview.v2";
try{if(!localStorage.getItem(KEY))localStorage.setItem(KEY,JSON.stringify(D.seed))}catch(e){}
const fold=t=>String(t||"").normalize("NFD").replace(/[̀-ͯ]/g,"").toLowerCase();
const item=f=>({id:f.id,title:f.title,original_title:f.original_title,release_date:f.release_date,poster_path:f.poster_path,backdrop_path:f.backdrop_path,overview:f.overview,genre_ids:f.genre_ids,vote_average:f.vote_average,vote_count:f.vote_count,original_language:f.original_language});
const pv=id=>D.provs.find(p=>p.provider_id===id);
function answer(u){
  const p=u.pathname.replace(/^\/3/,""),q=u.searchParams;
  if(p==="/watch/providers/movie")return{results:D.provs};
  if(p==="/search/keyword")return{results:[{id:10685,name:"black and white"}]};
  if(p==="/genre/movie/list")return{genres:[]};
  if(p==="/movie/now_playing"){if(Number(q.get("page")||1)>1)return{page:2,total_pages:1,total_results:9,results:[]};const t=new Date();
    return{page:1,total_pages:1,total_results:9,results:[2,1,9,3,11,12,10,5,8].map((i,k)=>{const d=new Date(t);d.setDate(t.getDate()-k*4-2);return {...item(D.films.find(f=>f.id===i)),release_date:d.toISOString().slice(0,10)}})}}
  if(p==="/trending/movie/week")return{page:1,total_pages:1,total_results:8,results:[5,1,7,11,3,2,9,12].map(i=>item(D.films.find(f=>f.id===i)))};
  if(p==="/search/movie"){const s=fold(q.get("query"));const r=D.films.filter(f=>fold(f.title).includes(s)||fold(f.original_title).includes(s));return{page:1,total_pages:1,total_results:r.length,results:r.map(item)}}
  if(p==="/discover/movie"){
    let r=D.films.slice();
    const g=(q.get("with_genres")||"").split("|").filter(Boolean).map(Number),no=(q.get("without_genres")||"").split(",").filter(Boolean).map(Number);
    if(g.length)r=r.filter(f=>f.genre_ids.some(x=>g.includes(x)));
    if(no.length)r=r.filter(f=>!f.genre_ids.some(x=>no.includes(x)));
    const wp=(q.get("with_watch_providers")||"").split("|").filter(Boolean).map(Number);
    if(wp.length)r=r.filter(f=>f.prov.some(x=>wp.includes(x)));
    const gte=q.get("primary_release_date.gte"),lte=q.get("primary_release_date.lte");
    if(gte)r=r.filter(f=>f.release_date>=gte);if(lte)r=r.filter(f=>f.release_date<=lte);
    const lang=q.get("with_original_language");if(lang)r=r.filter(f=>f.original_language===lang);
    const pgN=Number(q.get("page")||1);
    if(pgN>3)r=[];
    return{page:pgN,total_pages:3,total_results:r.length*3,results:r.map(f=>pgN>1?{...item(f),id:f.id+100*(pgN-1),vote_average:Math.max(5,f.vote_average-pgN*.6),vote_count:Math.round(f.vote_count/(pgN*2))}:item(f))};
  }
  const m=p.match(/^\/movie\/(\d+)$/);
  if(m){const f=D.films.find(x=>x.id===+m[1]%100);if(!f)return null;
    return{...item(f),id:+m[1],runtime:f.runtime,tagline:f.tagline,genres:f.genre_ids.map(id=>({id})),
      credits:{crew:[{job:"Director",name:f.director}],cast:[]},external_ids:{wikidata_id:"Q"+(1000+f.id)},
      "watch/providers":{results:{FR:{link:"https://www.themoviedb.org/movie/"+f.id+"/watch?locale=FR",flatrate:f.prov.map(pv),rent:[pv(6)],buy:[pv(6),pv(25)]}}}}}
  return{};
}
const real=window.fetch.bind(window);
window.fetch=async function(input,init){
  const url=String(input&&input.url||input);
  if(url.includes("api.themoviedb.org")){
    await new Promise(r=>setTimeout(r,220));
    const data=answer(new URL(url));
    return new Response(JSON.stringify(data||{status_message:"Not found"}),{status:data?200:404,headers:{"content-type":"application/json"}});
  }
  if(url.includes("query.wikidata.org")){
    await new Promise(r=>setTimeout(r,450));
    const q=decodeURIComponent(url),m=q.match(/wd:Q(\d+)/),f=m&&D.films.find(x=>x.id===+m[1]-1000);
    const FMT={1:"https://www.netflix.com/title/$1",2:"https://www.primevideo.com/detail/$1",4:"https://mubi.com/films/$1",5:"https://www.disneyplus.com/movies/wd/$1",6:"https://tv.apple.com/movie/$1",7:"https://play.max.com/movie/$1"};
    const bindings=f?f.prov.filter(pid=>FMT[pid]).map(pid=>({fmt:{type:"literal",value:FMT[pid]},v:{type:"literal",value:String(70000000+f.id*10+pid)}})):[];
    return new Response(JSON.stringify({head:{vars:["fmt","v"]},results:{bindings}}),{status:200,headers:{"content-type":"application/sparql-results+json"}});
  }
  if(url.includes("photon.komoot.io")){
    await new Promise(r=>setTimeout(r,200));
    const u=new URL(url),q=fold(u.searchParams.get("q")||"");
    const P=[["Paris",null,"Île-de-France",48.8566,2.3522],["Paris 11e Arrondissement","Paris","Île-de-France",48.859,2.38],["Montreuil",null,"Île-de-France",48.8638,2.4485],["Lyon",null,"Auvergne-Rhône-Alpes",45.764,4.8357],["Lille",null,"Hauts-de-France",50.6292,3.0573],["Bordeaux",null,"Nouvelle-Aquitaine",44.8378,-0.5792],["Marseille",null,"Provence-Alpes-Côte d'Azur",43.2965,5.3698],["Nantes",null,"Pays de la Loire",47.2184,-1.5536]];
    const feat=([n,c,st,la,lo])=>({type:"Feature",geometry:{type:"Point",coordinates:[lo,la]},properties:{name:n,city:c||n,state:st,country:"France",countrycode:"FR"}});
    const list=url.includes("/reverse")?[P[1]]:P.filter(x=>fold(x[0]).includes(q)||fold(x[0]).startsWith(q.slice(0,3)));
    return new Response(JSON.stringify({type:"FeatureCollection",features:list.slice(0,7).map(feat)}),{status:200,headers:{"content-type":"application/json"}});
  }
  if(url.includes("overpass-api.de")){
    await new Promise(r=>setTimeout(r,500));
    const q=decodeURIComponent(url),m=q.match(/around:(\d+),([-\d.]+),([-\d.]+)/);const R=+m[1],la=+m[2],lo=+m[3];
    const C=[["UGC Ciné Cité Les Halles","7 Place de la Rotonde","Paris",48.8617,2.347,"https://www.ugc.fr"],["MK2 Bastille","4 Boulevard Beaumarchais","Paris",48.853,2.37,"https://www.mk2.com"],["Le Grand Rex","1 Boulevard Poissonnière","Paris",48.8707,2.3478,"https://www.legrandrex.com"],["Le Louxor","170 Boulevard de Magenta","Paris",48.8838,2.3497,""],["Le Champo","51 Rue des Écoles","Paris",48.8504,2.3433,""],["Studio 28","10 Rue Tholozé","Paris",48.8868,2.333,""],["MK2 Quai de Seine","14 Quai de la Seine","Paris",48.8853,2.3712,"https://www.mk2.com"],["Pathé Wepler","140 Boulevard de Clichy","Paris",48.8836,2.3274,""],["Le Méliès","12 Place Jean Jaurès","Montreuil",48.8615,2.4418,""]];
    const dist=(a,b,c,d)=>{const r=x=>x*Math.PI/180,h=Math.sin(r(c-a)/2)**2+Math.cos(r(a))*Math.cos(r(c))*Math.sin(r(d-b)/2)**2;return 12742000*Math.asin(Math.sqrt(h))};
    let els=C.filter(c=>dist(la,lo,c[3],c[4])<=R).map((c,i)=>({type:"node",id:i+1,lat:c[3],lon:c[4],tags:{amenity:"cinema",name:c[0],"addr:street":c[1],"addr:city":c[2],...(c[5]?{website:c[5]}:{})}}));
    if(!els.length&&R>=5000)els=[0,1,2].map(i=>({type:"node",id:100+i,lat:la+0.004*(i+1),lon:lo-0.003*i,tags:{amenity:"cinema",name:["Cinéma Le Royal","Pathé Centre","Cinéma Les Arcades"][i],"addr:street":["Rue de la République","Place Bellecour","Cours Victor Hugo"][i]}}));
    return new Response(JSON.stringify({elements:els}),{status:200,headers:{"content-type":"application/json"}});
  }
  if(url.includes("version.json"))return new Response("{}",{status:404});
  return real(input,init);
};
})();
</script>
"""

html = APP.read_text()
head = html.split("<style>", 1)[0]
links = "\n".join(l for l in re.findall(r'<link rel="(?:preconnect|stylesheet)"[^>]*>', head))
body = html[html.index("<style>"):]
body = re.sub(r"</?(?:html|head|body)(?:\s[^>]*)?>", "", body)
body = body.replace('const KEY="cesoir.tmdb.v1";', 'const KEY="clap.preview.v2";', 1)
# Preview: show the update card a few seconds after opening (Refresh just closes it here)
body = body.replace('if(updateShown||location.protocol!=="https:")return;', 'if(updateShown)return;', 1)
body = body.replace('const r=await fetch("version.json?t="+Date.now(),{cache:"no-store"});if(!r.ok)return;\n    const j=await r.json();', 'const j={version:"preview-next"};', 1)
body = body.replace('$("#upd-go").onclick=()=>location.replace(location.pathname+"?v="+encodeURIComponent(ver));', '$("#upd-go").onclick=()=>$("#upd-x").click();', 1)

PAL_NAMES = {"brick":"Brick","oxblood":"Oxblood","terracotta":"Terracotta","blush":"Blush paper","champagne":"Champagne","mist":"Rose mist","iris":"Iris · Mauve","jade":"Jade · Sand"}
found = list(dict.fromkeys(re.findall(r'data-palette="([a-z]+)"', html)))
PAL = (["brick"] if "oxblood" in found else ["blush"] if ("champagne" in found or "mist" in found) else ["iris"] if "jade" in found else []) + found if found else []
switch = ('<span class="pv-sw" role="group" aria-label="Color option">' + "".join(f'<button type="button" data-pal="{p}" aria-pressed="{str(i==0).lower()}">{PAL_NAMES.get(p,p)}</button>' for i,p in enumerate(PAL)) + '</span>') if PAL else ""
band = f'<div class="pv-band" role="note"><span class="pv-t">Preview · {NOTE}</span>{switch}</div>'

body = body.replace('<div id="app">', '<div id="app">\n  ' + band, 1)
extra_css = ("#frame-warn{display:none!important}"
  ".pv-band{display:flex;flex-wrap:wrap;align-items:center;justify-content:center;gap:4px 10px;flex:none;padding:6px 12px;background:var(--secondary-container);color:var(--on-secondary-container);font-size:12px;font-weight:700;text-align:center;border-bottom:2px solid var(--outline)}"
  ".pv-t{display:inline-flex;align-items:center;gap:6px}"
  ".pv-sw{display:inline-flex;background:var(--surface-low);border:2px solid var(--outline);border-radius:999px;padding:2px}"
  ".pv-sw button{border:0;background:transparent;color:var(--on-surface);font-size:12px;font-weight:700;padding:4px 10px;border-radius:999px;min-height:28px}"
  ".pv-sw button[aria-pressed=true]{background:var(--primary-container);color:var(--on-primary-container)}\n")
body = body.replace("<style>", "<style>\n" + extra_css, 1)
data = json.dumps({"images": images, "films": films, "provs": provs, "seed": seed}, ensure_ascii=False)
script_at = body.index("<script>")
body = body[:script_at] + MOCK.replace("__DATA__", data) + body[script_at:]
if PAL:
    body += """<script>(function(){const set=p=>{document.documentElement.dataset.palette=p;document.querySelectorAll('.pv-sw button').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.pal===p)));try{localStorage.setItem('clap.preview.palette',p)}catch(e){}};const ok=[...document.querySelectorAll('.pv-sw button')].map(b=>b.dataset.pal);let p=ok[0];try{const q=localStorage.getItem('clap.preview.palette');if(ok.includes(q))p=q}catch(e){}set(p);document.querySelectorAll('.pv-sw button').forEach(b=>b.onclick=()=>set(b.dataset.pal));})();</script>"""
OUT.write_text('<title>Clap Preview</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n' + links + "\n" + body)
print(f"{OUT} {OUT.stat().st_size // 1024} KB")
