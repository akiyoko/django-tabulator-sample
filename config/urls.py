from django.contrib import admin
from django.urls import include, path

from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/prices/'), name='home'),
    path('prices/', include('prices.urls')),
]
