"""Validated, atomic content edits from GitHub workflow inputs. Never executes input."""
import json, os, re, sys
from datetime import datetime
from pathlib import Path
from build import ROOT, ACCESS, load, validate

def run(kind,values):
 events,results,photos=load('events'),load('results'),load('photos')
 def value(k):return str(values.get(k,'')).strip()
 def need(k):
  v=value(k)
  if not v:raise ValueError(f'{k.replace("_"," ")} is required')
  return v
 def find_event():
  target=need('event_id');e=next((e for e in events if e['id']==target),None)
  if not e:raise ValueError(f'No event matches {target}. Copy its ID from the event page URL.')
  return e
 if kind=='event':
  target=need('event_id');existing=next((e for e in events if e['id']==target),None)
  action=need('operation')
  if action=='Add' and existing:raise ValueError('That event ID already exists. Choose Edit or use a new ID.')
  if action=='Edit' and not existing:raise ValueError('Event not found. Choose Add to create it.')
  e=existing or dict(id=target,title='',venue='',address='',price='',description='Race to complete a 500-piece puzzle in 90 minutes. Bring a team of up to 4, or sign up solo and we’ll match you up. Winners get prizes, and every team keeps their puzzle.',status='scheduled',access={})
  for k in ['title','venue','address','price','ticket_url','description']:
   if value(k):e[k]='' if value(k)=='CLEAR' else value(k)
  if value('saved_venue') not in ('','Keep current / custom'):
   v=load('venues')[value('saved_venue')];e['venue']=v['name'];e['address']=v['address'];e['venue_id']=value('saved_venue')
  if value('status') not in ('','Keep current'):e['status']=value('status')
  day=value('date') or e.get('start','').split('T')[0]
  for key in ['start','end']:
   t=value(key+'_time') or e.get(key,'T').split('T')[-1]
   if not day or not t:raise ValueError('Date, start time, and end time are required for a new event')
   e[key]=day+'T'+t
  if not existing:events.append(e)
  changed='events';payload=events
 elif kind=='access':
  e=find_event();a=e.setdefault('access',{})
  for key in ACCESS:
   if value(key) not in ('','Keep current'):a[key]=value(key)
  if value('notes'):a['notes']='' if value('notes')=='CLEAR' else value('notes')
  changed='events';payload=events
 elif kind=='results':
  day=need('date');datetime.strptime(day,'%Y-%m-%d')
  item={'date':day,'title':'Competition results','entries':[]}
  old=next((r for r in results if r['date']==day),None)
  for place in (1,2,3):
   t=need(f'time_{place}');previous=next((v for v in old['entries'] if v['place']==place),{}) if old else {}
   item['entries'].append({'place':place,'team':value(f'team_{place}'),'time':t,'photo':previous.get('photo',''),'alt':previous.get('alt','')})
  if old:results.remove(old)
  results.append(item);changed='results';payload=results
 elif kind=='photo':
  path=need('path');alt=need('description');caption=value('caption');event_id=value('event_id')
  if event_id and event_id not in {e['id'] for e in events}:raise ValueError('Event ID does not exist')
  if value('results_date'):
   r=next((r for r in results if r['date']==value('results_date')),None)
   if not r:raise ValueError('Publish results for that date first')
   place=int(need('place'));entry=next((v for v in r['entries'] if v['place']==place),None)
   if not entry:raise ValueError('Placement not found')
   entry.update(photo=path,alt=alt);changed='results';payload=results
  else:
   entry=next((p for p in photos if p['path']==path),None)
   if not entry:entry={'id':'photo-'+__import__('hashlib').sha256(path.encode()).hexdigest()[:12]};photos.append(entry)
   entry.update(path=path,alt=alt,caption=caption,event_id=event_id);changed='photos';payload=photos
 else:raise ValueError('Unknown publishing task')
 validate(events,results,photos)
 dest=ROOT/'content'/f'{changed}.json';temp=dest.with_suffix('.tmp')
 temp.write_text(json.dumps(payload,indent=2,ensure_ascii=False)+'\n');temp.replace(dest)
 print(f'Saved {kind}. Content validated successfully.')
 if os.getenv('GITHUB_STEP_SUMMARY'):
  with open(os.environ['GITHUB_STEP_SUMMARY'],'a') as f:f.write(f'## Content saved\n\nThe {kind} update passed validation. The next job builds and publishes the website.\n')
if __name__=='__main__':
 try:run(sys.argv[1],json.loads(os.environ['FORM_INPUTS']))
 except (ValueError,KeyError,TypeError) as e:print(f'Could not publish: {e}',file=sys.stderr);sys.exit(1)
