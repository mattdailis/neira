from __future__ import unicode_literals

from django.db import models

# Create your models here.

class School(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name

class Boat(models.Model):
    BOAT_SIZES = (("four", "four"), ("eight", "eight"))
    size = models.CharField(
            max_length=5, 
            choices=BOAT_SIZES,
            default="four"
    )
    level = models.IntegerField(default=1)
    school = models.ForeignKey(School, on_delete=models.CASCADE) 
    team = models.CharField(
            max_length=1,
            choices=(("b", "boys"), ("g", "girls"), ("n", "novice")))

    def __str__(self):
        return "Boat from " + self.school.name

class Heat(models.Model):
    date = models.DateField()
    comment = models.TextField(default="")
    url = models.URLField(default="#")

    def __str__(self):
        return "Heat " + str(self.date)

class Result(models.Model):
    raw_boat = models.CharField(max_length=50, default="")
    raw_time = models.CharField(max_length=50, default="")
    boat = models.ForeignKey(Boat, on_delete=models.CASCADE)
    time = models.DurationField()
    heat = models.ForeignKey(Heat, on_delete=models.CASCADE)

    def __str__(self):
        return self.raw_boat + str(self.heat.date)
