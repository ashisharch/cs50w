from django.contrib import admin

from auctions.models import User, Listing, Bid, Category, Comment, Watchlist

# Register your models here.

class ListingAdmin(admin.ModelAdmin):
    list_dispaly = ("title", "starting_bid", "active")

admin.site.register(User)
admin.site.register(Listing, ListingAdmin)
admin.site.register(Bid)
admin.site.register(Category)
admin.site.register(Comment)
admin.site.register(Watchlist)
