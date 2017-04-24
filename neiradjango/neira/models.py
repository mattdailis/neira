from __future__ import unicode_literals

from django.db import models


# Create your models here.


class School(models.Model):

    SPLIT_MARKER = ",;,"  # For keeping a list of names as a single string

    """ Fields: """
    name = models.CharField(max_length=20)
    alternate_names = models.TextField(max_length=200)
    # alias_for = models.ForeignKey('self', on_delete=models.CASCADE)


    def __str__(self):
        return self.name

    def add_alias(self, other_school):
        other_school.merge_into(self)
        self.save()

    def merge_into(self, other_school):
        """ Update the given school with all of my names,
         set all my boats to point to the other school,
         and delete myself """
        other_school.add_alternate_names(self.names())
        for boat in self.boat_set.all():
            boat.school = other_school
            boat.save()
        self.delete()

    def add_alternate_names(self, alternate_names):
        names = self.names()
        for alternate_name in alternate_names:
            names.add(alternate_name)
        self.alternate_names = self.SPLIT_MARKER.join(names)
        self.save()

    def names(self):
        """ Return all the strings that have been used to denote this school """
        return set(self.alternate_names.split(self.SPLIT_MARKER)).union(set([self.name])).difference(set(['']))


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
