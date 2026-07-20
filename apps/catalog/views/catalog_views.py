from django.shortcuts import render
from django.views import View

from ..services import CatalogService


class ServiceListView(View):
    template_name = "catalog/list.html"

    def get(self, request):
        services = CatalogService().list_active_services()
        return render(request, self.template_name, {"services": services})
