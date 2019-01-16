from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from commentfreely import settings
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from django.conf import settings
from django.contrib.auth import login, logout
from django.utils.formats import date_format
import boto3
import requests
import json
import random
import logging
from comment.models import Site, Board, Comment
from core.forms import ContactForm, SiteForm, BoardForm
from core.constants import Constants

# Create the logger.
logger = logging.getLogger(__name__)

# BEGIN Dashboard views

@login_required
def dashboard(request):
	logger.info("dashboard")
	user_sites = Site.objects.filter(owner=request.user.profile, state=Constants.STATE_VISIBLE)
	user_boards = Board.objects.filter(owner=request.user.profile)
	return render(request, 'core/dashboard.html', {'user_sites': user_sites, 'user_boards': user_boards})
	
@login_required	
def new_site(request):
	user_sites = Site.objects.filter(owner=request.user.profile, state=Constants.STATE_VISIBLE)
	form = None
	if request.method == 'GET':
		form = SiteForm()
	else:
		form = SiteForm(request.POST)
		if form.is_valid() and len(list(user_sites)) < 1:
			logger.info(request.POST)
			site_name = form.cleaned_data['site_name']
			site_url = form.cleaned_data['site_url']
			site = Site(owner=request.user.profile, display_name=site_name, site_url=site_url, display_id=get_random_string(length=12))
			site.save()
			board = Board(site=site, owner=request.user.profile, display_name='default', display_id=get_random_string(length=12))
			board.save()
			return HttpResponseRedirect("/dashboard/")
		else:
			logger.info("not valid")
		
	return render(request, 'core/new_site.html', {'form': form, 'user_sites': user_sites})
	
@login_required	
def new_board(request):
	user_boards = Board.objects.filter(owner=request.user.profile)
	try:
		site_id = request.GET.get('site_id')
	except Exception as e:
		return HttpResponseRedirect("/dashboard/")
	
	form = None
	if request.method == 'GET':
		form = BoardForm(request)
	else:
		form = BoardForm(request, request.POST)
		if form.is_valid():
			logger.info(request.POST)
			board_name = form.cleaned_data['board_name']
			site_id = form.cleaned_data['site_id']
			site = Site.objects.get(display_id=site_id, owner=request.user.profile)
			board = Board(owner=request.user.profile, display_name=board_name, display_id=get_random_string(length=12), site=site)
			board.save()
			return HttpResponseRedirect("/dashboard/")
		else:
			logger.info("not valid")
		
	return render(request, 'core/new_board.html', {'form': form, 'user_boards': user_boards})
	
	
@login_required  
def comments(request):
	return render(request, 'core/comments.html')
        
@login_required        
def moderation(request):
	return render(request, 'core/moderation.html')

@login_required
def users(request):
	return render(request, 'core/users.html')

@login_required
def reports(request):
	return render(request, 'core/reports.html')
	
def demo(request):
	return render(request, 'core/demo.html')
        
@login_required
def code(request):
	logger.info("code")
	site = None
	try:
		site = Site.objects.get(owner=request.user.profile, state=Constants.STATE_VISIBLE)
	except:
		return HttpResponseRedirect("/dashboard/")
	try:
		board = Board.objects.get(owner=request.user.profile, state=Constants.STATE_VISIBLE, display_name='default')
	except:
		return HttpResponseRedirect("/dashboard/")
		
	return render(request, "core/code.html", {"site_id": site.display_id, "board_id": board.display_id})


@login_required       
def settings(request):
	return render(request, 'core/settings.html')
    
        
# END Dashboard views


@login_required
def get_user_boards(request):
	user_boards = Board.objects.filter(owner=request.user.profile, state=Constants.STATE_VISIBLE)
	user_boards_json = []
	for board in user_boards:
		user_board_json = {"id":board.display_id, "name":board.display_name, "owner_id":board.owner.display_id}
		user_boards_json.append(user_board_json)
	return JsonResponse({'data': user_boards_json})
	
	
@login_required
def delete_user_board(request):
	return JsonResponse({'success': True})
	
	
@login_required	
def get_user_sites(request):
	user_sites = Site.objects.filter(owner=request.user.profile, state=Constants.STATE_VISIBLE)
	user_sites_json = []
	for site in user_sites:
		user_site_json = {"id":site.display_id, "name":site.display_name, "url":site.site_url}
		user_sites_json.append(user_site_json)
	return JsonResponse({'data': user_sites_json})
	

@login_required	
def delete_user_site(request):
	logger.info(request.POST.get('display_id'))
	site = Site.objects.get(display_id = request.POST.get('display_id'), owner = request.user.profile)
	site.state = Constants.STATE_TRASH
	Board.objects.filter(site=site, state=Constants.STATE_VISIBLE).update(state=Constants.STATE_TRASH)
	site.save()
	return JsonResponse({'success': True})
	

@login_required
def get_site_comments(request):
	logger.info('get_site_comments')
	return JsonResponse({'success': True})
	
	
@login_required
def get_my_comments(request):
	logger.info('get_my_comments')
	my_comments = Comment.objects.filter(creator=request.user.profile, state=Constants.STATE_VISIBLE)
	my_comments_json = []
	for comment in my_comments:
		my_comment_json = {"date":date_format(comment.date_created, "SHORT_DATETIME_FORMAT"), "name":comment.content}
		my_comments_json.append(my_comment_json)
	
	return JsonResponse({'data': my_comments_json})
	
	
@login_required
def get_site_users(request):
	logger.info('get_site_users')
	active_site = Site.objects.get(owner=request.user.profile, state=Constants.STATE_VISIBLE)
	return JsonResponse({'success': True})
	



    