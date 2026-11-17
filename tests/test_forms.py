import json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import manage
from build import load
class FormTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);(self.root/'content').mkdir()
  for name in ['events','results','photos','venues']:(self.root/'content'/f'{name}.json').write_text(json.dumps(load(name)))
  self.p1=patch.object(manage,'ROOT',self.root);self.p1.start()
  self.p2=patch.object(manage,'load',lambda n:json.loads((self.root/'content'/f'{n}.json').read_text()));self.p2.start()
 def tearDown(self):self.p2.stop();self.p1.stop();self.tmp.cleanup()
 def test_add_edit_and_access(self):
  manage.run('event',dict(operation='Add',event_id='2027-01-12-test',title='Test event',date='2027-01-12',start_time='19:00',end_time='21:00',saved_venue='basic-city',ticket_url='https://www.tickettailor.com/events/test',status='scheduled'))
  manage.run('event',dict(operation='Edit',event_id='2027-01-12-test',status='sold_out'))
  manage.run('access',dict(event_id='2027-01-12-test',written_instructions='confirmed'))
  e=manage.load('events')[-1]
  self.assertEqual(e['status'],'sold_out');self.assertIn('212 W',e['address']);self.assertEqual(e['access']['written_instructions'],'confirmed');self.assertNotIn('visual_signals',e['access'])
 def test_bad_form_does_not_write(self):
  before=(self.root/'content/events.json').read_bytes()
  with self.assertRaises(ValueError):manage.run('event',dict(operation='Add',event_id='bad'))
  self.assertEqual(before,(self.root/'content/events.json').read_bytes())
 def test_results_and_photo(self):
  manage.run('results',dict(date='2027-01-12',time_1='30m 01s',time_2='40m 02s',time_3='50m 03s'))
  manage.run('photo',dict(path='pics/gallery/1.jpg',description='A puzzle box and a glass.',results_date='2027-01-12',place='1'))
  self.assertEqual(manage.load('results')[-1]['entries'][0]['photo'],'pics/gallery/1.jpg')
 def test_photo_requires_alt(self):
  with self.assertRaises(ValueError):manage.run('photo',dict(path='pics/gallery/1.jpg'))
if __name__=='__main__':unittest.main()
