from django.urls import path
from django.views.generic import RedirectView

from YouTubeDownloader.views import download_video

urlpatterns = [
    path('', download_video),
    path('<string>', RedirectView.as_view(url='/'))  # Exceptions handling
]