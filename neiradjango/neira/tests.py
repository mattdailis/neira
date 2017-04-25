from django.test import TestCase

from neira.models import *

# Create your tests here.

from neiraschools import match_school

class TestMatchSchool(TestCase):
    
    def setUp(self):
        School.objects.create(name="Dexter")
        School.objects.create(name="Exeter")
        School.objects.create(name="Hopkins")

    def test_same_name(self):
        self.assertEqual(match_school("Hopkins")[0], School.objects.get(name="Hopkins"))
        
    def test_boat_num(self):
        (school, num) = match_school("St. Mark's (2)")
        self.assertEqual(num, 2)

        (school, num) = match_school("St. Mark's (3)")
        self.assertEqual(num, 3)

        (school, num) = match_school("St. Mark's (4)")
        self.assertEqual(num, 4)

