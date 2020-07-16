from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.forms import ModelForm
from django.db.models import Max
from django.views.decorators.http import *

from .models import *

#    print(f"debug-text {variable}")

# Create the form based on the model already defined
class NewListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ['id', 'title', 'description', 'starting_bid', 'category']

# Create the form based on the model already defined
class NewWatchlistForm(ModelForm):
    class Meta:
        model = Watchlist
        fields = ['name','user']

def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.all()
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            request.session["uid"]=user.id
            return HttpResponseRedirect(reverse("auctions:index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("auctions:index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("auctions:index"))
    else:
        return render(request, "auctions/register.html")


def listing_detail(request, listing_id):
    #l = listing_id
    l = Listing.objects.get(id=listing_id)

    #get next valid bid from utility function
    return render(request, "auctions/listing_detail.html", {
        "listing": l,
        "next_bid": get_next_bid(l),
    })


def manage_listing(request, listing_id=''):
    path = request.META['PATH_INFO']

    if request.method == "GET" and "create" in path:
        return render(request, "auctions/manage_listing.html" , {
            "create_form": NewListingForm(),
            "action": "create"
        })
    #Only allow editing of existing entries
    elif "manage" in path:
        l = Listing.objects.get(id=listing_id)
        is_editable = ''

        # if listing is not active, make form readonly
        if not l.active:
            is_editable = "disabled"

        if l.by_user.id == request.session["uid"]:
            return render(request, "auctions/manage_listing.html" , {
                "create_form": NewListingForm(instance=l),
                "action": "manage",
                "is_editable": is_editable,
                "listing_id" : l.id
            })
        else:
            return render(request, "auctions/error.html", {
                "error_message": "You cannot edit listings owned by someone else"
            })

    #"edit_form": NewListingForm(instance=l),
    else:
        return render(request, "auctions/error.html", {
            "error_message": "You can only create uniquely new entries or edit existing entries"
        })


def close_listing(request, listing_id):
    l = Listing.objects.get(id=listing_id)

    if request.method == "POST":
        l.active = False
        l.save()

    return render(request, "auctions/listing_detail.html", {
        "listing": l,
        "next_bid": get_next_bid(l),
    })


# Save listing changes.
def save_listing(request):
    u = User.objects.get(pk=int(request.session["uid"]))
    #l = ''
    listing_id = None

    if request.method == "POST":
        referer = request.META['HTTP_REFERER']
        form = NewListingForm(request.POST)
        listing_id = form.data["listing_id"]

        if form.is_valid():
            print(f"form cleaned data: {form.cleaned_data}")
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            starting_bid = form.cleaned_data["starting_bid"]
            category = form.cleaned_data["category"]
            by_user = u

            #if new listing, just save object and redirect
            #else existing listing, update object based on id

            saved_listing, created = Listing.objects.update_or_create(
                title = title,
                defaults = {
                    'title' : title,
                    'description' : description,
                    'category' : category,
                }
            )

            return HttpResponseRedirect(reverse("auctions:u_listing_detail", kwargs={'listing_id':saved_listing.id}))
        else:
            return render(request, "auctions/manage_listing.html", {
                "error_message": "The form is not valid yet. Go back and edit values"
            })
    else:
        return render(request, "auctions/error.html", {
            "error_message": "This page is not meant to be accessed directly."
        })



def add_bid(request):
    l = Listing.objects.get(pk=request.POST.get("listing"))
    u = User.objects.get(pk=request.POST.get("user"))
    bid_value = ''
    next_bid = ''
    request.session["msg"]=''

    if request.method == "POST":
        bid_value = int(request.POST.get("bid"))
        # If first bid and greater than starting bid, save bid
        if l.bids_received.count() == 0 and bid_value >= int(l.starting_bid):
            Bid.objects.create(by_user=u, for_listing=l, bid_value=bid_value)
        else:
            all_bids = l.bids_received.aggregate(Max("bid_value"))
            max_bid = int(all_bids[next(iter(all_bids))])
            if bid_value > max_bid:
                Bid.objects.create(by_user=u, for_listing=l, bid_value=bid_value)

        l.current_bid = bid_value
        l.save()
        request.session["msg"] = "Bid successfully added"
        print(f"current bid = {l.current_bid}")
        return redirect("auctions:u_listing_detail", listing_id=l.id)

#        return render(request, "auctions/listing_detail.html", {
#            "listing": l,
#            "next_bid" : get_next_bid(l),
#            "message": "Bid successfully added"
#        })

    else:
        return render(request, "auctions/listing_detail.html", {
            "listing": l,
        })

def watchlist(request):
    u = User.objects.get(pk=int(request.session["uid"]))
    form = NewWatchlistForm(request.POST)

    #Show the list of watchlists if user visiting page
    if request.method == "GET":
        return render(request, "auctions/watchlist.html", {
            "watchlist": u.watchlist.all(),
            "create_form": form
        })
    #Save the newly addd
    elif request.method == "POST":
        referer = request.META['HTTP_REFERER']
        print(f"referer: {referer}")

        if form.is_valid():
            name = form.cleaned_data["name"]
            user = form.cleaned_data["user"]

            form.save()
            return redirect("auctions:u_watchlist")
        else:
            return render(request, "auctions/watchlist.html", {
                "error_message": "The form is not valid yet. Go back and edit values"
            })

    print(f"In post")
    return render(request, "auctions/watchlist.html", {
        "message": "You Posted to watchlist"
    })

def unwatch_listing(request, watchlist_id, listing_id):
    w = Watchlist.objects.get(pk=watchlist_id)
    l = Listing.objects.get(pk=listing_id)
    w.listings.remove(l)
    w.save()
    return redirect("auctions:u_watchlist")

def delete_watchlist(request, watchlist_id):
    w = Watchlist.objects.get(pk=watchlist_id)
    w.delete()
    return redirect("auctions:u_watchlist")

#Add listing to watchlist and redirect user back to watchlist
def add_to_watchlist(request):
    if request.method == "POST":
        l = Listing.objects.get(pk=request.POST.get("listing"))
        u = User.objects.get(pk=request.POST.get("user"))

        #Add item to watchlist only if watchlist exist
        if "watchlist" in request.POST:
            w = Watchlist.objects.get(pk=request.POST.get("watchlist"))
            w.listings.add(l)
            w.user = u
            w.save()

    return redirect("auctions:u_watchlist")

#Add comment to listing and redirect user back to listing
def add_comment(request, listing_id):
    if request.method == "POST":
        text = request.POST.get("comment_body")
        l = Listing.objects.get(pk=listing_id)
        u = User.objects.get(pk=int(request.session["uid"]))
        Comment.objects.create(by_user=u, for_listing=l, content=text)
        return redirect("auctions:u_listing_detail", listing_id=l.id)
    else:
        return redirect("auctions:u_listing_detail", listing_id=listing_id)



#========================Utility Function================
#Determine next bid, given a listing object
def get_next_bid(Listing):
    next_bid= ''
    l = Listing

    # If first bid, return the starting bid as next bid
    if l.bids_received.count() == 0:
        next_bid = l.starting_bid
    #else return the max current bid + incremental bid value
    else:
        #max_bid = l.bids_received.aggregate(Max("bid_value"))
        #next_bid = int(max_bid[next(iter(max_bid))]) + l.bid_increment
        next_bid = l.current_bid + l.bid_increment

    return next_bid
