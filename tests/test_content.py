import copy, sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from build import validate,load,stamp,local
class ContentTests(unittest.TestCase):
 def setUp(self):self.events=load('events');self.results=load('results');self.photos=load('photos')
 def check(self):validate(self.events,self.results,self.photos)
 def test_current_content(self):self.check()
 def test_duplicate_id(self):
  self.events.append(copy.deepcopy(self.events[0]))
  with self.assertRaises(ValueError):self.check()
 def test_end_before_start(self):
  self.events[0]['end']=self.events[0]['start']
  with self.assertRaises(ValueError):self.check()
 def test_bad_ticket_scheme(self):
  self.events[0]['ticket_url']='javascript:alert(1)'
  with self.assertRaises(ValueError):self.check()
 def test_unverified_access_value(self):
  self.events[0]['access']={'visible_timer':'probably'}
  with self.assertRaises(ValueError):self.check()
 def test_missing_alt(self):
  self.photos[0]['alt']=' '
  with self.assertRaises(ValueError):self.check()
 def test_traversal(self):
  with self.assertRaises(ValueError):local('../outside.jpg')
 def test_dst_gap(self):
  with self.assertRaises(ValueError):stamp('2027-03-14T02:30')
 def test_dst_ambiguity(self):
  with self.assertRaises(ValueError):stamp('2027-11-07T01:30')
 def test_winter_summer_offsets(self):
  self.assertEqual(stamp('2027-01-15T19:00').strftime('%z'),'-0500')
  self.assertEqual(stamp('2027-07-15T19:00').strftime('%z'),'-0400')
if __name__=='__main__':unittest.main()
