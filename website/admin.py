from django.contrib import admin

# Register your models here.
class MyAdminSite( admin.AdminSite ):
      # Text to put at the end of each page's <title>.
    site_title = 'Terabit admin'

    # Text to put in each page's <h1>.
    site_header = 'Terabit'

    # Text to put at the top of the admin index page.
    index_title = 'Terabit admin'
admin_site = MyAdminSite()

from website.models import Human, Nft, Land

admin_site.register( Human, Human.customAdmin())
admin_site.register( Nft, Nft.customAdmin())
admin_site.register( Land, Land.customAdmin())
