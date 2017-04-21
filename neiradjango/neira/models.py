from __future__ import unicode_literals

from django.db import models

# Create your models here.

class School(models.Model):
    name = models.CharField(max_length=20)

class Boat(models.Model):
    size = (("four", "four"),
            ("eight", "eight"))
    level = models.IntegerField(default=1)
    school = models.ForeignKey(School, on_delete=models.CASCADE) 

class Heat(models.Model):
    date = models.DateTimeField()
    comment = models.TextField(default="")
    url = models.URLField(default="#")

class Result(models.Model):
    raw_boat = models.CharField(max_length=50, default="")
    raw_time = models.CharField(max_length=50, default="")
    boat = models.ForeignKey(Boat, on_delete=models.CASCADE)
    time = models.TimeField()
    heat = models.ForeignKey(Heat, on_delete=models.CASCADE)
