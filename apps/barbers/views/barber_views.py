from django.shortcuts import render
from django.views import View

from ..services import BarberService


class BarberListView(View):
    template_name = "barbers/list.html"

    def get(self, request):
        barbers = BarberService().list_active_barbers()
        return render(request, self.template_name, {"barbers": barbers})


class BarberDetailView(View):
    template_name = "barbers/detail.html"

    def get(self, request, pk):
        barber = BarberService().get_barber(pk)
        return render(request, self.template_name, {"barber": barber})
