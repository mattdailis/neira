from django.test import TestCase

from neira.models import *

# Create your tests here.

from neiraschools import match_boat

def match_default(school_name):
    return match_boat(school_name, size="four", team="boys", boatNum=1)

class TestMatchBoat(TestCase):
    
    def setUp(self):
        School.objects.create(name="Dexter")
        School.objects.create(name="Exeter")
        School.objects.create(name="Hopkins")
        School.objects.create(name="St. Marks")

    def test_same_name(self):
        self.assertEqual(match_default("Hopkins").school, School.objects.get(name="Hopkins"))
        
    def test_boat_num_parens(self):
        boat = match_default("St. Mark's (2)")
        self.assertEqual(boat.level, 2)

        boat = match_default("St. Mark's (3)")
        self.assertEqual(boat.level, 3)

        boat = match_default("St. Mark's (4)")
        self.assertEqual(boat.level, 4)

    def test_boat_num_XV(self):

        boat = match_default("Choate 1V")
        self.assertEqual(boat.level, 1)

        boat = match_default("Choate 2V")
        self.assertEqual(boat.level, 2)

    def test_same_object_twice(self):
        self.assertEqual(match_default("Abcdef"), match_default("Abcdef"))


