from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path

from api.views import get_recipe_short_link

urlpatterns = [
    path('api/', include('api.urls')),
    path('admin/', admin.site.urls),
    re_path(
        r'^s/(?P<short_link>[а-яёА-ЯЁa-z0-9-]+)/$', get_recipe_short_link,
        name='short_link'
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
