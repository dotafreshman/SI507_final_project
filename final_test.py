import unittest
from final import *

class TestSource(unittest.TestCase):
    def test_source_access(self):
        final_list,city_list=web_scrape()
        self.assertEqual(len(final_list[1]),7)
        self.assertIn({'id': '103698', 'date': 'February 3, 2014', 'state': 'IN', 'city': 'Franklin', 'address': '2100 block of Bridlewood Dr', 'kill': '3', 'injure': '2'}
,final_list)
        self.assertEqual(len(city_list[1]),3)
        self.assertIn({'city': 'Spanish Fork', 'lat': 40.114955, 'lng': -111.654923},city_list)
        self.assertIsInstance(final_list[1],dict)

class TestStore(unittest.TestCase):
    def test_store(self):
        conn=sqlite3.connect(DBNAME)
        c=conn.cursor()
        result=c.execute('select state from address')
        lis=result.fetchall()
        self.assertIn(('LA',),lis)
        self.assertEqual(len(lis),269)
        result=c.execute('select city from city')
        lis=result.fetchall()
        self.assertIn(('Miami',),lis)
        self.assertEqual(len(lis),165)
        result=c.execute('select date from crime')
        lis=result.fetchall()
        self.assertIn(('December 7, 2014',),lis)
        conn.close()

class TestProcess(unittest.TestCase):
    def test_process(self):
        lat_list,lng_list=plot1_map('MI',True)
        self.assertEqual(len(lat_list),len(lng_list))
        a=['CA','TX,','KS']
        lis=plot2_box(a,True)
        self.assertIn(lis[0],a)
        lis=plot3_line('September',True)
        self.assertEqual(15,len(lis))
        lis=plot4_bar('21',True)
        self.assertEqual(len(lis),21)
        self.assertIn('CA',lis)
unittest.main()