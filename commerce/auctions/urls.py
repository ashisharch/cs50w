from django.urls import path

from . import views

app_name = "auctions"
urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("listing/<int:listing_id>", views.listing_detail, name="u_listing_detail"),
    path("listing/create", views.create_listing, name="u_create_listing"),
    path("listing/<int:listing_id>/manage", views.manage_listing, name="u_manage_listing"),
    path("listing/<int:listing_id>/close", views.close_listing, name="u_close_listing"),
    path("watchlist", views.watchlist, name="u_watchlist"),
    path("watchlist/<int:watchlist_id>/unwatch_listing/<int:listing_id>", views.unwatch_listing, name="u_unwatch_listing"),
    path("watchlist/delete/<int:watchlist_id>", views.delete_watchlist, name="u_delete_watchlist"),
    path("add_bid", views.add_bid, name="u_add_bid"),
    path("listing/<int:listing_id>/add_comment", views.add_comment, name="u_add_comment"),
    path("listing/<int:listing_id>/add_to_watchlist", views.add_to_watchlist, name="u_add_to_watchlist"),
    path("categories", views.categories, name="u_categories"),
]

#    path("save", views.save_listing, name="u_save_listing"),
