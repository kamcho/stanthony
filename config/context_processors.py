from django.conf import settings


def site_maps(request):
    return {
        'google_maps_embed_url': getattr(settings, 'GOOGLE_MAPS_EMBED_URL', ''),
        'google_maps_link_url': getattr(settings, 'GOOGLE_MAPS_LINK_URL', ''),
    }
