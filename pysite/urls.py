from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView

from website.views.api import human as api_human
from website.views.api import land as api_land
from website.views.api import nft as api_nft
from website.views.api import version as api_version
from website.admin import admin_site
 
admin.autodiscover()

urlpatterns = [
    path('land/search_proximity/', api_land.search_proximity),

    path('human/generate_nonce/', api_human.generate_nonce),
    path('human/auth_by_nonce/', api_human.auth_by_nonce),
    path('human/invalidate_auth/', api_human.invalidate_auth),
    path('human/is_unique/', api_human.is_unique),
    path('human/desc/', api_human.desc),

    path('nft/bulk_list/', api_nft.bulk_list),
    path('nft/list/', api_nft.list_),
    path('nft/create/', api_nft.create),
    path('nft/resync/', api_nft.resync),
    path('nft/search_proximity/', api_nft.search_proximity),

    path('version/compat/', api_version.compat),
    path('version/current/', api_version.current),

    # Render into the app
    path('', TemplateView.as_view(template_name='index.html')),
    path('map', TemplateView.as_view(template_name='index.html')),
    path('how_to_buy', TemplateView.as_view(template_name='index.html')),
    path('contact', TemplateView.as_view(template_name='index.html')),
    path('profile', TemplateView.as_view(template_name='index.html')),

    path('admin/', admin_site.urls),
]
