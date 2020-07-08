import markdown2
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django import forms
from . import util
import random


class NewSearchForm(forms.Form):
    query = forms.CharField(label="search string")

class NewCreateEditForm(forms.Form):
    entry_title = forms.CharField(label="entry title")
    entry_body  = forms.CharField(widget=forms.Textarea(attrs={'style': 'height: 200px;', 'title': 'Entry Body'}))


def index(request):
    # Get the URL parameter that was submitted from search form
    # search_term = request.GET.get('search_string', '')
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
    })


def url_entry(request, entry_name):
    file_text = util.get_entry(entry_name)

    if file_text is not None:
        file_text = markdown2.markdown(file_text)
        return render(request, "encyclopedia/entry.html", {
            "entry_name" : entry_name,
            "entry_text" : file_text,
            "entries": util.list_entries(),
        })
    else:
        return render(request, "encyclopedia/error.html", {
            "error_message": "This entry does not exist"
        })


def search(request):
    entry_list = util.list_entries()
    matching_items = 0
    if request.method == "POST":
        form = NewSearchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data["query"]

            # get list of machting entries from the list, case insesitive search
            matching_items = [s for s in entry_list if query.lower() in s.lower()]

            #If query matches a value in the list, redirect user to entry page
            if query.lower() in map(str.lower, entry_list):
                return HttpResponseRedirect(reverse("encyclopedia:u_entry", kwargs={'entry_name':query}))
            #else find all matching entries and present the list to user on a search page
            elif len(matching_items) > 0:
                return render(request, "encyclopedia/search.html" , {
                    "search_term" : query,
                    "matching_items": matching_items,
                })
            else:
                return render(request, "encyclopedia/search.html" , {
                    "message": "No matches found. Please refine your search",
                })
        else:
            return render(request, "encyclopedia/search.html" , {
                "message": "asdfasfsafsfasdf",
            })
    else:
        return render(request, "encyclopedia/search.html" , {
            "message" : "Please use the search form to find relevant pages by title",
        })

#This view gets the entry name to be edited, gets the details of that entry and pre-populates the forms
#with the entry values
def edit(request):
    entry_name = request.GET.get('p', '')
    if request.method == "GET" and entry_name is not '' and entry_name in util.list_entries():
        file_text = util.get_entry(entry_name)
        return render(request, "encyclopedia/edit.html", {
            "edit_form": NewCreateEditForm(initial={"entry_title":entry_name, "entry_body":file_text}),
        })
    else:
        return render(request, "encyclopedia/error.html", {
            "error_message": "This entry does not exist or you got here in error."
        })

#This view renders an empty create form
def create(request):
    return render(request, "encyclopedia/create.html" , {
        "create_form": NewCreateEditForm(),
    })

#Save entry into storage.
def save(request):
    if request.method == "POST":
        referer = request.META['HTTP_REFERER']
        form = NewCreateEditForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["entry_title"]
            body = form.cleaned_data["entry_body"]
            #Only be able to create new entries that do not exist
            if ("create" in referer) and (title not in util.list_entries()):
                util.save_entry(title, body)
                return HttpResponseRedirect(reverse("encyclopedia:u_entry", kwargs={'entry_name':title}))
            #Only allow editing of existing entries
            elif ("edit" in referer) and (title in util.list_entries()):
                util.save_entry(title, body)
                return HttpResponseRedirect(reverse("encyclopedia:u_entry", kwargs={'entry_name':title}))
            else:
                return render(request, "encyclopedia/error.html", {
                    "error_message": "You can only create uniquely new entries or edit existing entries"
                })
        else:
            return render(request, "encyclopedia/error.html", {
                "error_message": "The form is not valid yet. Go back and edit values"
            })
    else:
        return render(request, "encyclopedia/error.html", {
            "error_message": "This page is not meant to be accessed directly."
        })


def random_entry(request):
    entries = util.list_entries()
    random_entry = entries[random.randint(0,len(entries)-1)]
    return HttpResponseRedirect(reverse("encyclopedia:u_entry", kwargs={'entry_name':random_entry}))
