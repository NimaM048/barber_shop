from django.shortcuts import render
from django.views import View

from apps.core.services import SeoService
from apps.core.services.page_content_service import PageContentService

from ..services import BarberService


class BarberListView(View):
    template_name = "barbers/list.html"

    def get(self, request):
        seo = SeoService()
        page_content = PageContentService().get("barbers")
        barbers = BarberService().list_active_barbers()
        return render(
            request,
            self.template_name,
            {
                "barbers": barbers,
                "page_content": page_content,
                "page_seo": seo.barbers_meta(),
            },
        )


class BarberDetailView(View):
    template_name = "barbers/detail.html"

    def get(self, request, pk):
        barber = BarberService().get_barber(pk)
        return render(request, self.template_name, {"barber": barber})
