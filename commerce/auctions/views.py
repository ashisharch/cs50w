from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseBadRequest, HttpResponseRedirect, Http404
from django.shortcuts import render, redirect
from django.urls import reverse
from django.forms import ModelForm
from django.db.models import Max
from django.views.decorators.http import *
from django.contrib.auth.decorators import login_required
from django.contrib.sessions.models import Session
from django.contrib import messages
from .models import *

# Create the form based on the model already defined
class NewListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ['id', 'title', 'description', 'starting_bid', 'photo_url', 'category']

# Create the form based on the model already defined
class NewWatchlistForm(ModelForm):
    class Meta:
        model = Watchlist
        fields = ['name','user']

def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.filter(active=True).all(),
        "closed_listings": Listing.objects.filter(active=False).all()
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


# Render the listing details
def listing_detail(request, listing_id):
    #l = listing_id
    l = Listing.objects.get(id=listing_id)
    #get next valid bid from utility function
    return render(request, "auctions/listing_detail.html", {
        "listing": l,
        "next_bid": get_next_bid(l),
    })


# Create a new listing
@login_required(login_url='/login')
def create_listing(request):
    path = request.META['PATH_INFO']
    if request.method == "GET":
        return render(request, "auctions/create_listing.html" , {
            "create_form": NewListingForm(),
        })
    elif request.method == "POST":
        saved_list_id = save_listing(request, "create_new")
        return HttpResponseRedirect(reverse("auctions:u_listing_detail", kwargs={'listing_id':saved_list_id}))


#TODO - see if we can disable the starting-bid field in edit form.
# Render the listing form with existing listing
@login_required(login_url='/login')
def manage_listing(request, listing_id):
    path = request.META['PATH_INFO']
    l = Listing.objects.get(id=listing_id)

    #Only allow editing of existing entries. Lets render the form on GET
    if request.method == "GET": #and "manage" in path
        is_editable = '' #Empty string means field is editable

        # if listing is not active, make form readonly
        if not l.active:
            is_editable = "disabled"

        # only allow the owner of user to edit an entry if entry is active
        if int(l.by_user.id) == int(request.session.get('_auth_user_id')):

            return render(request, "auctions/manage_listing.html" , {
                "listing" : l,
                "create_form": NewListingForm(instance=l),
            })
        else:
            return render(request, "auctions/error.html", {
                "error_message": "You cannot edit listings owned by someone else"
            })

    elif request.method == "POST" and "manage" in path:
        save_listing(request, "edit_existing", l)
        return HttpResponseRedirect(reverse("auctions:u_listing_detail", kwargs={'listing_id':listing_id}))


    else:
        return render(request, "auctions/error.html", {
            "error_message": "You can only create uniquely new entries or edit existing entries"
        })


#Close the listing, make the highest bidder the winner.
@login_required(login_url='/login')
def close_listing(request, listing_id):
    l = Listing.objects.get(id=listing_id)
    winning_bid = None

    # Set active status to false to close listing.
    if request.method == "POST" :
        l.active = False
        pass
        l.save()

        #Proceed further only if there are bids on this listing
        if l.bids_received.count() > 0:
            # Get max bid from all the bids on this listing
            max_bid_value = l.bids_received.aggregate(max_bid = Max("bid_value"))
            max_bid = max_bid_value['max_bid'] #This is the actual bid value

            #Use the max_bid value to find the winning bid
            winning_bid = l.bids_received.all().filter(bid_value=max_bid).first()

            #Update the bid to be the winning bid.
            Bid.objects.filter(id=winning_bid.id).update(
                winning_bid = True,
            )

    return HttpResponseRedirect(reverse("auctions:u_listing_detail", kwargs={'listing_id':listing_id}))


# Save listing changes when changes are posted from the form.
@login_required(login_url='/login')
def save_listing(request, action, listing=None):
    u = User.objects.get(pk=int(request.session.get('_auth_user_id')))

    if request.method == "POST":
        l = listing
        form = NewListingForm(request.POST)
        saved_listing_id = None

        if form.is_valid():
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            starting_bid = form.cleaned_data["starting_bid"]
            photo_url = form.cleaned_data["photo_url"]
            category = form.cleaned_data["category"]
            by_user = u

            #if new listing, just save object and redirect
            if action == "create_new":
                saved_listing = Listing.objects.create (
                    title = title,
                    description = description,
                    starting_bid = starting_bid,
                    photo_url = photo_url,
                    category = category,
                    by_user = u )
                saved_listing_id = saved_listing.id
            #else existing listing, update object based on id
            elif action == "edit_existing":
                listing_id = l.id

                #Update returns the number of rows updated, which is useless to us for now
                Listing.objects.filter(id=listing_id).update(
                    title = title,
                    description = description,
                    photo_url = photo_url,
                    category = category,
                )
                saved_listing_id = listing_id

            #return value expected from this view
            return saved_listing_id

        else:
            return render(request, "auctions/manage_listing.html", {
                "error_message": "The form is not valid yet. Go back and edit values"
            })
    else:
        return render(request, "auctions/error.html", {
            "error_message": "This page is not meant to be accessed directly."
        })


#Add a bid to a listing
@login_required(login_url='/login')
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
        #Save bid if bid greater than current bid
        else:
            if bid_value > l.current_bid:
                Bid.objects.create(by_user=u, for_listing=l, bid_value=bid_value)

        #Upate current bid to the bid value just saved.
        l.current_bid = bid_value
        l.save()

        messages.success(request, 'Bid was successfully added')
        return redirect("auctions:u_listing_detail", listing_id=l.id)

    else:
        return render(request, "auctions/listing_detail.html", {
            "listing": l,
        })

#Create a watchlist
@login_required(login_url='/login')
def watchlist(request):
    u = User.objects.get(pk=int(request.session.get('_auth_user_id')))
    form = NewWatchlistForm(request.POST)
    #if the user had no watchlist, capture the
    listing_to_add = request.GET.get('p', '')

    #Show the list of watchlists if user visiting page
    if request.method == "GET":
        return render(request, "auctions/watchlist.html", {
            "watchlist": u.watchlist.all(),
            "create_form": form
        })
    elif request.method == "POST":
        if form.is_valid():
            name = form.cleaned_data["name"]
            user = form.cleaned_data["user"]
            form.save()
            return redirect("auctions:u_watchlist")
        else:
            return render(request, "auctions/watchlist.html", {
                "error_message": "The form is not valid yet. Go back and edit values"
            })

    return render(request, "auctions/watchlist.html", {
        "message": "You Posted to watchlist"
    })


#Add listing to watchlist and redirect user back to watchlist
@login_required(login_url='/login')
def add_to_watchlist(request, listing_id):
    if request.method == "POST":
        l = Listing.objects.get(pk=listing_id)
        u = User.objects.get(pk=request.POST.get("user"))

        #Add item to watchlist if watchlist exist
        if "watchlist" in request.POST:
            w = Watchlist.objects.get(pk=request.POST.get("watchlist"))
            w.listings.add(l)
            w.user = u
            w.save()
        #If no watchlist exists, create a default one and add listing to that watchlist
        elif "watchlist" not in request.POST:
            default_watchlist = Watchlist.objects.create(name=u.username+"_watchlist", user=u)
            default_watchlist.listings.add(l)
            default_watchlist.save()

    return redirect("auctions:u_watchlist")


#Remove a listing from a watchlist
@login_required(login_url='/login')
def unwatch_listing(request, watchlist_id, listing_id):
    try:
        w = Watchlist.objects.get(pk=watchlist_id)
        l = Listing.objects.get(pk=listing_id)
    except:
        return redirect("auctions:u_watchlist")

    w.listings.remove(l)
    w.save()
    return redirect("auctions:u_watchlist")

#Delete a watchlist
@login_required(login_url='/login')
def delete_watchlist(request, watchlist_id):
    try:
        w = Watchlist.objects.get(pk=watchlist_id)
        w.delete()
    except:
        return redirect("auctions:u_watchlist")
    return redirect("auctions:u_watchlist")


#Add comment to listing and redirect user back to listing
@login_required(login_url='/login')
def add_comment(request, listing_id):
    l = Listing.objects.get(pk=listing_id)

    if request.method == "POST":
        text = request.POST.get("comment_body")
        l = Listing.objects.get(pk=listing_id)
        u = User.objects.get(pk=int(request.session.get('_auth_user_id')))
        Comment.objects.create(by_user=u, for_listing=l, content=text)
        return redirect("auctions:u_listing_detail", listing_id=l.id)
    else:
        return redirect("auctions:u_listing_detail", listing_id=listing_id)


def categories(request):
    return render(request, "auctions/categories.html", {
        "categories": Category.objects.all(),
        "uncategorized" : Listing.objects.filter(category=None)
    })

#========================Utility Function================
#Determine next bid, given a listing object
def get_next_bid(Listing):
    next_bid= ''
    l = Listing

    # If first bid, return the starting bid as next bid
    if l.bids_received.count() == 0:
        next_bid = l.starting_bid
    #else return the current bid + incremental bid value
    else:
        next_bid = l.current_bid + l.bid_increment

    return next_bid
