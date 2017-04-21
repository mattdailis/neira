from django.shortcuts import render
from django.views import generic

# Create your views here.

from neira.models import Boat

class IndexView(generic.ListView):
    template_name = 'neira/index.html'
    context_object_name = 'boats'
    def get_queryset(self):
        return Boat.objects #.order_by('')[:5]

