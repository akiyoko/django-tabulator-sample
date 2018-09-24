from django.urls import path
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView

from . import views

CACHE_TIMEOUT = 60 * 60 * 3  # 3 hours

app_name = 'prices'
urlpatterns = [
    path('', TemplateView.as_view(
        template_name='prices/index.html'), name='index'),
    # path('history_ajax/', cache_page(CACHE_TIMEOUT)(views.history_ajax), name='history_ajax'),
    path('history_ajax/', views.history_ajax, name='history_ajax'),
]
