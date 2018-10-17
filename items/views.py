from django.shortcuts import render, redirect
from items.models import Item, FavoriteItem
from .forms import UserRegisterForm, UserLoginForm
from django.contrib.auth import login, logout, authenticate
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.models import User
import requests

# Create your views here.
def item_favorite(request, item_id):

	item_obj= Item.objects.get(id=item_id)
	fav_obj, created = FavoriteItem.objects.get_or_create(item=item_obj, user=request.user)
	if created:
		action = 'favorite_item'
	else :
		fav_obj.delete()
		action = 'unfavorite_item'

	response= {
		'action':action,

	}
	return JsonResponse(response, safe=False)

def favorite_items(request):
	my_fav = []
	items= Item.objects.all()
	query = request.GET.get('q')
	if query:
		items=Item.objects.filter(
			Q(name__icontains=query)|
			Q(description__icontains=query)
			).distinct()
	if not request.user.is_anonymous:
		fave_items = request.user.favoriteitem_set.all()
	for item in items:
		for fav in fave_items:
			if item.id == fav.item_id:
				my_fav.append(fav.item)
	

	context={
		   "my_fav":my_fav,
		}

	return render(request, 'fav_list.html', context)

def item_list(request):
	if request.user.is_anonymous:
		return redirect("user-login")
	items = Item.objects.all()
	query = request.GET.get("q")
	if query:
		items = items.filter(
			Q(name__icontains=query)|
			Q(description__icontains=query)
			).distinct()

	my_fav = []
	for fav in FavoriteItem.objects.filter(user=request.user):
		my_fav.append(fav.item.id)

	context = {
			"items": items,
			"my_fav": my_fav,
		}
	return render(request, 'item_list.html', context)

def item_detail(request, item_id):
	context = {
		"item": Item.objects.get(id=item_id)
	}
	return render(request, 'item_detail.html', context)

def user_register(request):
	register_form = UserRegisterForm()
	if request.method == "POST":
		register_form = UserRegisterForm(request.POST)
		if register_form.is_valid():
			user = register_form.save(commit=False)
			user.set_password(user.password)
			user.save()
			login(request, user)
			return redirect('item-list')
	context = {
		"register_form": register_form
	}
	return render(request, 'user_register.html', context)

def user_login(request):
	login_form = UserLoginForm()
	if request.method == "POST":
		login_form = UserLoginForm(request.POST)
		if login_form.is_valid():
			username = login_form.cleaned_data['username']
			password = login_form.cleaned_data['password']
			authenticated_user = authenticate(username=username, password=password)
			if authenticated_user:
				login(request, authenticated_user)
				return redirect('item-list')
	context = {
		"login_form": login_form
	}
	return render(request, 'user_login.html', context)

def user_logout(request):
	logout(request)

	return redirect('item-list')