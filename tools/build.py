"""Build crawlable HTML and optimized images. No JavaScript needed for core content."""
from pathlib import Path
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from html import escape
from urllib.parse import urlparse
import argparse, hashlib, json, re, shutil
from PIL import Image, ImageOps

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'_site'
TZ=ZoneInfo('America/New_York')
ACCESS={'written_instructions':'Written competition instructions','visual_signals':'Visual start and finish signals','visible_timer':'Visible countdown timer','step_free':'Step-free entrance','accessible_restroom':'Accessible restroom','hearing_loop':'Hearing loop or assistive listening system'}
STATES={'confirmed':'Confirmed','unavailable':'Not available','not_confirmed':'Not yet confirmed'}
def esc(v): return escape(str(v),quote=True)
def load(name): return json.loads((ROOT/'content'/f'{name}.json').read_text())
def local(v):
 if not v or Path(v).is_absolute() or '..' in Path(v).parts: raise ValueError('Use a repository-relative file path without ..')
 p=(ROOT/v).resolve()
 if not p.is_relative_to(ROOT) or not p.is_file(): raise ValueError(f'File not found: {v}')
 return p
def stamp(s):
 d=datetime.fromisoformat(s)
 if d.tzinfo is not None: raise ValueError('Enter local Richmond time without a UTC offset')
 aware=d.replace(tzinfo=TZ)
 if aware.astimezone(timezone.utc).astimezone(TZ).replace(tzinfo=None)!=d: raise ValueError('Time falls in the daylight-saving clock change; choose another time')
 if aware.utcoffset()!=d.replace(tzinfo=TZ,fold=1).utcoffset(): raise ValueError('Time is ambiguous during the daylight-saving clock change')
 return aware

def validate(events,results,photos):
 ids=set()
 for e in events:
  if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',e['id']) or e['id'] in ids: raise ValueError('Event ID must be unique, lowercase and hyphenated')
  ids.add(e['id'])
  for key in ['title','venue','description']:
   if not e.get(key,'').strip(): raise ValueError(f'{e["id"]}: {key} is required')
  if stamp(e['end'])<=stamp(e['start']): raise ValueError('Event end must be after start')
  u=urlparse(e['ticket_url'])
  if u.scheme!='https' or u.hostname not in ('www.tickettailor.com','tickettailor.com'): raise ValueError('Use an https://www.tickettailor.com ticket URL')
  if e['status'] not in ['scheduled','sold_out','canceled','postponed']: raise ValueError('Invalid event status')
  for k,v in e.get('access',{}).items():
   if k in ACCESS and v not in STATES: raise ValueError('Invalid accessibility status')
 for r in results:
  datetime.strptime(r['date'],'%Y-%m-%d')
  for item in r['entries']:
   if not re.fullmatch(r'\d{1,3}m (?:[0-5]?\d)s',item['time']): raise ValueError('Results times must look like 38m 53s')
   if item.get('photo'): local(item['photo'])
 seen=set()
 for p in photos:
  if p['id'] in seen: raise ValueError('Duplicate photo ID')
  seen.add(p['id']);local(p['path'])
  if not p.get('alt','').strip(): raise ValueError('Every photo needs an image description')
  if p.get('event_id') and p['event_id'] not in ids: raise ValueError('Photo event ID does not exist')

def build(now=None):
 global cfg,base,images
 cfg=load('site');base=cfg['url'].rstrip('/');images={}
 if urlparse(base).scheme!='https': raise ValueError('Site URL must use HTTPS')
 events=load('events');results=load('results');photos=load('photos');validate(events,results,photos)
 now=stamp(now) if now else datetime.now(TZ)
 if OUT.exists(): shutil.rmtree(OUT)
 (OUT/'assets').mkdir(parents=True)
 for f in ['favicon.ico','CNAME','timer.html']:
  if (ROOT/f).exists(): shutil.copy2(ROOT/f,OUT/f)
 for f in ['style.css','script.js']: shutil.copy2(ROOT/'src'/f,OUT/f)
 (OUT/'.nojekyll').touch()
 def image_data(path):
  if path in images:return images[path]
  source=local(path)
  with Image.open(source) as raw:
   im=ImageOps.exif_transpose(raw).convert('RGB');sizes=[]
   for width in [480,960,1600]:
    resized=im.copy();resized.thumbnail((width,width));digest=hashlib.sha256(source.read_bytes()).hexdigest()[:12]
    name=f'assets/{digest}-{width}.webp';resized.save(OUT/name,'WEBP',quality=80,method=6);sizes.append((name,resized.width,resized.height))
  images[path]=sizes;return sizes
 def img(path,alt,hero=False):
  sizes=image_data(path);name,w,h=sizes[1]
  srcset=', '.join(f'{prefix}{n} {width}w' for n,width,height in {s[1]:s for s in sizes}.values())
  return f'<img src="{prefix}{name}" srcset="{srcset}" sizes="(max-width: 700px) 100vw, 50vw" width="{w}" height="{h}" alt="{esc(alt)}" {"fetchpriority=\"high\"" if hero else "loading=\"lazy\""} decoding="async">'
 def photo(p):
  image=image_data(p['path'])[-1][0]
  return f'<figure><a class="photo-link" href="{prefix}{image}" data-photo data-caption="{esc(p.get("caption", ""))}">{img(p["path"],p["alt"])}<span class="sr-only">Open full-size photo</span></a>{"<figcaption>"+esc(p["caption"])+"</figcaption>" if p.get("caption") else ""}</figure>'
 def date(d):return stamp(d).strftime('%A, %B %-d, %Y')
 def clock(d):return stamp(d).strftime('%-I:%M %p')
 def event_card(e):
  d=stamp(e['start']); status={'scheduled':'Registration open','sold_out':'Sold out','canceled':'Canceled','postponed':'Postponed'}[e['status']]
  if stamp(e['end'])<now:status='Past event'
  return f'<article class="event-card"><div class="date-tile" aria-hidden="true"><span>{d.strftime("%b")}</span><strong>{d.day}</strong><span>{d.strftime("%a")}</span></div><div><p class="eyebrow">{esc(status)}</p><h3><a href="{prefix}events/{e["id"]}/">{esc(e["title"])}</a></h3><p><time datetime="{d.isoformat()}">{esc(date(e["start"]))}</time><br>{clock(e["start"])}–{clock(e["end"])} Eastern<br>{esc(e["venue"])}</p><p class="price">{esc(e.get("price") or "See registration for ticket prices")}</p><a class="button secondary" href="{prefix}events/{e["id"]}/">Event details<span class="sr-only">: {esc(e["title"])} on {d.strftime("%B %-d")}</span></a></div></article>'
 def result_block(r):
  cards=''
  for v in r['entries']:
   title=f'{v["place"]}{ {1:"st",2:"nd",3:"rd"}.get(v["place"],"th")} place'
   picture=photo({'path':v['photo'],'alt':v.get('alt') or title+' team photo','caption':''}) if v.get('photo') else ''
   minutes,seconds=re.fullmatch(r'(\d+)m (\d+)s',v['time']).groups()
   cards+=f'<article class="result-card">{picture}<div class="card-copy"><h3>{esc(title)}</h3>{"<p>"+esc(v["team"])+"</p>" if v.get("team") else ""}<p class="result-time">{minutes} minutes, {seconds} seconds</p></div></article>'
  return f'<section class="result-set"><h2>{datetime.strptime(r["date"],"%Y-%m-%d").strftime("%B %-d, %Y")}</h2><div class="results-grid">{cards}</div></section>'
 def page(path,title,desc,body,schema=None,share=None):
  nonlocal prefix
  url=base+'/'+path;logo=image_data(cfg['logo'])[0][0];social=base+'/'+image_data(share or 'pics/gallery/2.jpg')[1][0]
  schema_html='<script type="application/ld+json">'+json.dumps(schema,ensure_ascii=False).replace('<','\\u003c')+'</script>' if schema else ''
  text=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)}</title><meta name="description" content="{esc(desc)}"><link rel="canonical" href="{esc(url)}"><meta property="og:type" content="website"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{esc(url)}"><meta property="og:image" content="{esc(social)}"><meta property="og:image:alt" content="RVA Puzzle League event photograph"><meta name="twitter:card" content="summary_large_image"><meta name="theme-color" content="#244f50"><link rel="icon" href="{prefix}favicon.ico"><link rel="stylesheet" href="{prefix}style.css">{schema_html}<script src="{prefix}script.js" defer></script></head><body>
<a class="skip-link" href="#main">Skip to main content</a><header class="site-header"><div class="container nav-row"><a class="brand" href="{prefix}index.html"><img src="{prefix}{logo}" alt="" width="48" height="48"><span>RVA Puzzle League<small>Richmond, Virginia</small></span></a><button class="menu-toggle" type="button" aria-expanded="false" aria-controls="navigation" hidden>Menu</button><nav id="navigation" aria-label="Main navigation"><a href="{prefix}index.html#events">Events</a><a href="{prefix}results/">Results</a><a href="{prefix}photos/">Photos</a><a href="{prefix}accessibility/">Accessibility</a><a href="mailto:{cfg['email']}">Contact</a></nav></div></header>
<main id="main" tabindex="-1">{body}</main><footer><div class="container footer-row"><div><strong>Good company. Great puzzles.</strong><p>RVA Puzzle League · Richmond, Virginia</p></div><div><a href="mailto:{cfg['email']}">{cfg['email']}</a><br><a href="{cfg['instagram']}">Find us on Instagram</a><br><a href="{prefix}accessibility/">Accessibility &amp; access requests</a></div></div></footer>
<dialog id="photo-dialog" aria-labelledby="photo-title"><div class="dialog-bar"><h2 id="photo-title">Event photo</h2><button type="button" id="close-photo">Close photo</button></div><img id="expanded-photo" alt=""><p id="photo-caption"></p></dialog></body></html>'''
  target=OUT/(path+'index.html' if path.endswith('/') or not path else path);target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text)
  pages.append(url)
 prefix='';pages=[]
 upcoming=sorted([e for e in events if stamp(e['end'])>=now],key=lambda e:e['start'])
 first=next((e for e in upcoming if e['status']=='scheduled'),None)
 hero_photo=img('pics/gallery/2.jpg','Teams puzzling together at a Richmond brewery.',True)
 next_text=f'<p class="next-event">Next up · {stamp(first["start"]).strftime("%b %-d")} · {clock(first["start"])}<br>{esc(first["venue"])}</p>' if first else '<p class="next-event">Find your next puzzle night below.</p>'
 latest=''.join(result_block(r) for r in sorted(results,key=lambda r:r['date'],reverse=True)[:1])
 body=f'''<section class="hero"><div class="container hero-grid"><div><p class="eyebrow">Richmond’s speed puzzling community</p><h1>Ready, Set,<br><span>Puzzle.</span></h1><p class="hero-copy">Bring your friends. Meet your next teammates.<br>Race the clock, and keep the puzzle.</p><a class="button" href="#events">Find your next event</a>{next_text}</div><figure class="hero-photo">{hero_photo}<figcaption>A little competition. A lot of connection.</figcaption></figure></div></section>
<section id="events" class="section"><div class="container"><div class="section-heading"><div><p class="eyebrow">Make a date with your team</p><h2>Upcoming competitions</h2></div><a href="events/">All events &amp; past dates</a></div><div class="events-grid">{''.join(event_card(e) for e in upcoming) or '<p>New dates are on the way. Email us for event information.</p>'}</div></div></section>
<section id="how-it-works" class="section tinted"><div class="container"><p class="eyebrow">First time? You’re in the right place.</p><h2>One puzzle. Your people. 90 minutes.</h2><div class="steps"><div><strong>01 / Get a team together</strong><p>Bring up to four puzzlers, or sign up solo and we’ll match you with a team.</p></div><div><strong>02 / Race the clock</strong><p>Work together on a 500-piece puzzle. You have 90 minutes to finish.</p></div><div><strong>03 / Take the fun home</strong><p>Winners get prizes, and every team keeps their puzzle.</p></div></div><a class="text-link" href="accessibility/">Plan your visit: accessibility and communication</a></div></section>
<section id="results" class="section"><div class="container"><div class="section-heading"><div><p class="eyebrow">A round of applause</p><h2>Latest results</h2></div><a href="results/">All results</a></div>{latest}</div></section>
<section id="gallery" class="section tinted"><div class="container"><div class="section-heading"><h2>Around the puzzle table</h2><a href="photos/">All photos</a></div><div class="gallery-grid">{''.join(photo(p) for p in photos[:4])}</div></div></section>
<section class="section"><div class="container narrow"><h2>A few things to know</h2><details><summary>Can I come on my own?</summary><p>Yes. Sign up solo and we’ll match you with a team. Check the event’s ticket options before booking.</p></details><details><summary>Do I need to be an expert?</summary><p>You don’t need a previous competition result to join. Come ready to work together and enjoy the challenge.</p></details><details><summary>What does registration include?</summary><p>A 500-piece puzzle for your team to keep and a 90-minute competition. Check Ticket Tailor for the current price, ticket options, and booking terms.</p></details><details><summary>How can I ask about accessibility?</summary><p>Email <a href="mailto:{cfg['email']}">{cfg['email']}</a>. Ask about written instructions, visual timing, venue access, or another arrangement. Event pages show what has been confirmed; you do not need to share a diagnosis.</p></details><details><summary>Are there age restrictions?</summary><p>Check the event’s registration details or email us before booking. Venue and event policies may vary.</p></details></div></section>'''
 page('','RVA Puzzle League | Richmond Speed Puzzling Events','Join Richmond speed puzzling events: 500-piece puzzles, teams of up to four, solo signup, and 90 minutes of friendly competition.',body,{'@context':'https://schema.org','@type':'Organization','name':cfg['name'],'url':base,'email':cfg['email'],'sameAs':[cfg['instagram']]})
 prefix='../'
 page('events/','Puzzle Events in Richmond | RVA Puzzle League','Upcoming and past RVA Puzzle League competitions in Richmond, Virginia. Find event details, registration links, and access information.',f'<section class="section"><div class="container"><p class="eyebrow">Find your next puzzle night</p><h1>Events in Richmond</h1><h2>Upcoming events</h2><div class="events-grid">'+(''.join(event_card(e) for e in upcoming) or '<p>New dates are on the way.</p>')+'</div><h2 class="archive-title">Past events</h2><div class="events-grid">'+(''.join(event_card(e) for e in sorted(events,key=lambda e:e['start'],reverse=True) if stamp(e['end'])<now) or '<p>Past listings will appear here after each event.</p>')+'</div></div></section>')
 page('results/','Competition Results | RVA Puzzle League','Finishing times and winning teams from RVA Puzzle League speed puzzling events.', '<section class="section"><div class="container"><p class="eyebrow">The finish line</p><h1>Competition results</h1>'+''.join(result_block(r) for r in sorted(results,key=lambda r:r['date'],reverse=True))+'</div></section>')
 page('photos/','Event Photos | RVA Puzzle League','A look around the tables at RVA Puzzle League competitions in Richmond.', '<section class="section"><div class="container"><p class="eyebrow">Our community</p><h1>Around the puzzle table</h1><p>Select a photo to view it at full size.</p><div class="gallery-grid">'+''.join(photo(p) for p in photos)+'</div></div></section>')
 page('accessibility/','Accessibility & Communication | RVA Puzzle League','Written event information, text-based contact, and confirmed access arrangements for RVA Puzzle League events.',f'''<section class="section"><div class="container narrow"><p class="eyebrow">Plan a visit that works for you</p><h1>Accessibility &amp; communication</h1><p class="lead">You should be able to find event information and ask questions without making a phone call.</p><h2>Deaf and hard-of-hearing participants</h2><p>Each event page lists the status of written instructions, visual start and finish signals, a visible timer, and assistive listening equipment. “Not yet confirmed” means we have not verified that arrangement for that event.</p><p>Please check before booking if an arrangement is essential to your participation. A venue’s equipment and the way a competition is run can vary.</p><h2>Ask in writing</h2><p>Email <a href="mailto:{cfg['email']}">{cfg['email']}</a> with the event date and what would help you participate. You do not need to share a diagnosis. Contact us before booking if you need confirmation of an arrangement.</p><h2>Venue access</h2><p>Check each event’s information for step-free entry, accessible restrooms, and notes about the venue. Unconfirmed information is labeled rather than assumed.</p><h2>Using this website</h2><p>Event information and results are available as text. Navigation and photo controls support keyboard use. Photos have text descriptions. Registration takes place on Ticket Tailor, a separate website.</p><h2>Report a barrier</h2><p>If a page, photo description, or registration step is difficult to use, email us with the page address and a short description. This website is being improved; we do not claim that every third-party page has been independently verified for accessibility.</p></div></section>''')
 prefix='../../'
 for e in events:
  past=stamp(e['end'])<now; access=e.get('access',{})
  rows=''.join(f'<div><dt>{label}</dt><dd>{STATES[access.get(key,"not_confirmed")]}</dd></div>' for key,label in ACCESS.items())
  status={'scheduled':'Upcoming event','sold_out':'Sold out','canceled':'Canceled','postponed':'Postponed'}[e['status']]
  cta=f'<a class="button" href="{esc(e["ticket_url"])}">Register on Ticket Tailor<span class="sr-only"> for {esc(e["title"])}</span></a>' if not past and e['status']=='scheduled' else f'<p class="notice">{"This event has ended." if past else esc(status)+". Email us for updates."}</p>'
  calendar=f'<a class="text-link" href="event.ics" download>Add to calendar (.ics)</a>' if not past and e['status'] in ['scheduled','sold_out'] else ''
  body=f'''<section class="section"><div class="container narrow"><a href="../">All events</a><p class="eyebrow">{"Past event" if past else status}</p><h1>{esc(e['title'])}</h1><p class="lead"><time datetime="{stamp(e['start']).isoformat()}">{date(e['start'])}</time><br>{clock(e['start'])}–{clock(e['end'])} Eastern</p><p><strong>{esc(e['venue'])}</strong><br>{esc(e.get('address') or 'Contact the host to confirm the venue address before travelling.')}</p><p>{esc(e['description'])}</p><p class="price">{esc(e.get('price') or 'See Ticket Tailor for current prices and ticket options.')}</p><div class="actions">{cta}{calendar}</div><p>Ticket options and booking terms are available on Ticket Tailor. Questions? <a href="mailto:{cfg['email']}">Email the host</a>.</p><h2>Accessibility at this event</h2><p>These are event-specific arrangements. Unconfirmed details are not a guarantee of availability.</p><dl class="access-list">{rows}</dl>{'<p>'+esc(access['notes'])+'</p>' if access.get('notes') else ''}<p>For a written response about an access need, email <a href="mailto:{cfg['email']}">{cfg['email']}</a>. You do not need to disclose a diagnosis.</p><a href="../../accessibility/">More about accessibility and communication</a></div></section>'''
  event_photos=[p for p in photos if p.get('event_id')==e['id']]
  if event_photos:body+='<section class="section"><div class="container"><h2>Photos from this event</h2><div class="gallery-grid">'+''.join(photo(p) for p in event_photos)+'</div></div></section>'
  # Full venue addresses are deliberately required before advertising Event rich-result data.
  schema=None
  if e.get('address'):
   schema={'@context':'https://schema.org','@type':'Event','name':e['title'],'startDate':stamp(e['start']).isoformat(),'endDate':stamp(e['end']).isoformat(),'description':e['description'],'eventAttendanceMode':'https://schema.org/OfflineEventAttendanceMode','eventStatus':'https://schema.org/'+{'scheduled':'EventScheduled','sold_out':'EventScheduled','canceled':'EventCancelled','postponed':'EventPostponed'}[e['status']],'location':{'@type':'Place','name':e['venue'],'address':e['address']},'organizer':{'@type':'Organization','name':cfg['name'],'url':base},'url':base+'/events/'+e['id']+'/','image':[base+'/'+image_data('pics/gallery/2.jpg')[1][0]]}
  page(f'events/{e["id"]}/',e['title']+' · '+stamp(e['start']).strftime('%b %-d, %Y')+' | RVA Puzzle League',e['description'],body,schema)
  def ical(s):return s.replace('\\','\\\\').replace('\n','\\n').replace(',','\\,').replace(';','\\;')
  lines=['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//RVA Puzzle League//Events//EN','BEGIN:VEVENT','UID:'+e['id']+'@rvapuzzleleague.com','DTSTAMP:'+now.astimezone(timezone.utc).strftime('%Y%m%dT%H%M%SZ'),'DTSTART:'+stamp(e['start']).astimezone(timezone.utc).strftime('%Y%m%dT%H%M%SZ'),'DTEND:'+stamp(e['end']).astimezone(timezone.utc).strftime('%Y%m%dT%H%M%SZ'),'SUMMARY:'+ical(e['title']),'LOCATION:'+ical(e['venue']+' '+e.get('address','')),'DESCRIPTION:'+ical(e['description']),'URL:'+base+'/events/'+e['id']+'/','STATUS:'+('CANCELLED' if e['status']=='canceled' else 'TENTATIVE' if e['status']=='postponed' else 'CONFIRMED'),'END:VEVENT','END:VCALENDAR']
  folded=[]
  for line in lines:
   current=''
   for char in line:
    if len((current+char).encode())>73:folded.append(current);current=' '
    current+=char
   folded.append(current)
  (OUT/'events'/e['id']/'event.ics').write_bytes(('\r\n'.join(folded)+'\r\n').encode())
 prefix=base+'/'
 page('404.html','Page not found | RVA Puzzle League','Find upcoming Richmond puzzle events.','<section class="section"><div class="container"><h1>This piece is missing.</h1><p>That page could not be found.</p><a class="button" href="'+base+'/">Back to upcoming events</a></div></section>')
 (OUT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+esc(u)+'</loc></url>' for u in pages if not u.endswith('404.html'))+'</urlset>')
 (OUT/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: '+base+'/sitemap.xml\n')
 print(f'Built {len(pages)} pages and {len(images)} optimized image sets in {OUT}')
 if any(not e.get('address') for e in events):print('NOTE: Add full venue addresses to enable Event structured data on those pages.')

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--now');args=parser.parse_args();build(args.now)
