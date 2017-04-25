from __future__ import unicode_literals

from django.db import models


# Create your models here.

class SchoolManager(models.Manager):
    def get_queryset(self):
        return super(SchoolManager, self).get_queryset().filter(alias=None)

    # def get(self, **kwargs):
    #     schools = super(SchoolManager, self).get_queryset().filter(kwargs)

    # def filter(self, f):
    #     super(SchoolManager, self).get_queryset().filter(kwargs)
    #

class School(models.Model):

    SPLIT_MARKER = ",;,"  # For keeping a list of names as a single string

    """ Fields: """
    name = models.CharField(max_length=20)
    alternate_names = models.TextField(max_length=200)
    alias = models.ForeignKey('self', on_delete=models.CASCADE, default=None, null=True)
    objects = models.Manager()
    primaries = SchoolManager()

    def __str__(self):
        return self.name

    def add_alias(self, other_school):
        other_school.merge_into(self)
        self.save()

    def boats(self):
        return self.get_primary()._boats()

    def names(self):
        return self.get_primary()._names()

    def merge_into(self, other_school):
        if self.alias is None:
            self.alias = other_school
            self.save()
        else:
            self.alias.merge_into(other_school)

    def add_alternate_names(self, alternate_names):
        names = self.names()
        for alternate_name in alternate_names:
            names.add(alternate_name)
        self.alternate_names = self.SPLIT_MARKER.join(names)
        self.save()

    def _boats(self):
        return reduce(lambda a, b: a.union(b._boats()), self.school_set.all(), self.boat_set.all())

    def _names(self):
        """ Return all the strings that have been used to denote this school """
        my_names = set(self.alternate_names.split(self.SPLIT_MARKER)).union(set([self.name])).difference(set(['']))
        return reduce(lambda a, b: a.union(b._names()), self.school_set.all(), my_names)

    def primary_name(self):
        return self.get_primary().name

    def get_primary(self):
        if self.alias is None:
            return self
        else:
            return self.alias.get_primary()

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
        return " ".join([self.school.name, self.team, str(self.level), self.size])


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
