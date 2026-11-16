"""Catch broken generated local links/assets, duplicate IDs, and missing alt attributes."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse,unquote
from build import OUT
class Page(HTMLParser):
 def __init__(self):super().__init__();self.ids=[];self.refs=[];self.errors=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id' in a:self.ids.append(a['id'])
  if tag=='img' and 'alt' not in a:self.errors.append('Image missing alt')
  if tag=='img' and not all(k in a for k in ['width','height']) and a.get('id')!='expanded-photo':self.errors.append('Image missing dimensions')
  if tag in ['a','link','script','img']:
   u=a.get('href') or a.get('src')
   if u:self.refs.append(u)
pages={}
for path in OUT.rglob('*.html'):
 if path.name=='timer.html':continue # Existing standalone host tool retained, not certified by this check.
 p=Page();p.feed(path.read_text());pages[path.resolve()]=p
errors=[]
for path,p in pages.items():
 if len(p.ids)!=len(set(p.ids)):errors.append(f'{path}: duplicate IDs')
 errors += [f'{path}: {e}' for e in p.errors]
 for ref in p.refs:
  u=urlparse(ref)
  if u.scheme or u.netloc:continue
  target=(path.parent/unquote(u.path)).resolve() if u.path else path
  if target.is_dir():target=target/'index.html'
  if not target.exists():errors.append(f'{path}: missing {ref}')
  elif u.fragment and target in pages and u.fragment not in pages[target].ids:errors.append(f'{path}: missing anchor {ref}')
if errors:raise SystemExit('\n'.join(errors))
print(f'Checked local links, anchors, IDs, and image attributes across {len(pages)} generated pages.')
