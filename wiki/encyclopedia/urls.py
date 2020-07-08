from django.urls import path, re_path

from . import views

app_name = "encyclopedia"
urlpatterns = [
    path("", views.index, name="index"),
    path("search", views.search, name="u_search"),
    path("create", views.create, name="u_create"),
    path("edit", views.edit, name="u_edit"),
    path("save", views.save, name="u_save"),
    path("random_entry", views.random_entry, name="u_random"), 
    path("<str:entry_name>", views.url_entry, name="u_entry"),
]
