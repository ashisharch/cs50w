from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass

#User: id, name, fk-bid, fk-comment, fk-listing
#Bid: id, current-bid, fk-user, fk-listing,
#Listing: id, title, description, category, photo, starting-bid, status, fk-watchlist, fk-bid, fk-comment, fk-user
#Watchlist: id, fk-user, fk-listing
#Comment: id, content, fk-user, fk-listing
#Category: id, name, fk-listing

class Category(models.Model):
    name = models.CharField(max_length=30)
    def __str__(self):
        return f"{self.name}"

#TODO - update cascade model for winner bid, category
class Listing(models.Model):
    title = models.CharField(max_length=30)
    description = models.TextField(max_length=200)
    photo_url = models.URLField(null=True, blank=True)
    starting_bid = models.PositiveIntegerField()
    bid_increment = models.PositiveIntegerField(default=1)
    current_bid = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)
    created = models.DateField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True, related_name="listings")
    by_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="my_listings")
    def __str__(self):
        return f"{self.id}: {self.title} / {self.photo_url} / {self.starting_bid} / {self.active}"

class Bid(models.Model):
    bid_value = models.PositiveIntegerField()
    winning_bid = models.BooleanField(default=False)
    by_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids_made")
    for_listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids_received")
    def __str__(self):
        return f"BidID={self.id}: BidValue={self.bid_value}: ListingID={self.for_listing.id}: WinningBid={self.winning_bid}"

class Watchlist(models.Model):
    name = models.CharField(max_length=30, default="")
    listings = models.ManyToManyField(Listing, blank=True, related_name="being_watched")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist")
    def __str__(self):
        return f"{self.id}: {self.name} {self.listings}"

class Comment(models.Model):
    content = models.TextField(max_length=200)
    by_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments_made")
    for_listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    def __str__(self):
        return f"{self.id}: {self.content}"
