from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, Http404
from django.utils.crypto import get_random_string
from django.contrib.auth.decorators import login_required
from django.dispatch import Signal
from django.dispatch import receiver
from core.signals import signal_new_comment, signal_update_comment, signal_delete_comment, signal_vote
from core.constants import Constants
from comment.models import Thread, Comment, Vote, Site, Board
from django.core.exceptions import ObjectDoesNotExist
from django.utils.crypto import get_random_string
from django.utils import timezone
from core.constants import Constants
import datetime
import re
import logging
import mimetypes

logger = logging.getLogger(__name__)

"""
================================================================================================================================================================
COMMENT API ENDPOINTS
================================================================================================================================================================
"""

def new_comments_thread(site_id, board_id, thread_id):
	
	site = None
	try:
		site = Site.objects.get(display_id=site_id)
	except Exception as e:
		return None
		
	board = None
	try:
		board = Board.objects.get(display_id=board_id, site=site)
	except ObjectDoesNotExist:
		board = Board.objects.get(display_name='default', site=site)
		logger.info('using default board')
	except Exception as e:
		logger.warn(e)
		
	thread = None
	try:
		logger.info(site.display_id+thread_id)
		thread = Thread(owner=board.owner, display_id=site.display_id+thread_id, site_id=site.display_id, board=board)
		thread.save()
	except Exception as e:
		logger.info(e)
		logger.info(site.display_id+thread_id)
		

def get_comments(request, site_id, board_id, thread_id):
	logger.info("api_comments")
	
	thread = None
	try:
		thread = Thread.objects.get(display_id=site_id+thread_id, site_id=site_id)
	except ObjectDoesNotExist:
		logger.info("New Comments Thread")
		thread = new_comments_thread(site_id, board_id, thread_id)
	except Exception as e:
		logger.warn(e)
		
	comments = None
	try:
		comments = Comment.objects.filter(thread=thread, state=Constants.STATE_VISIBLE)
	except Exception as e:
		logger.warn(e)
		
	commentsArray=[]	
	for c in comments:
		parent = c.parent if c.parent is not None else None
		
		created_by_current_user = False
		if request.user.is_authenticated and request.user.profile == c.creator:
			created_by_current_user = True
		
		user_has_upvoted = False
		if c.up_vote_count > 0 and request.user.is_authenticated:
			try:
				Vote.objects.get(comment=c, voter=request.user.profile)
				user_has_upvoted = True
			except ObjectDoesNotExist:
				user_has_upvoted = False
			except Exception as e:
				logger.warn(e)
				
		modified = None
		if c.modified:
			modified = str(c.modified)
			
		comment = { "id": c.comment_id, "parent": parent, "created": str(c.date_created), "modified": modified, "content": c.content, "pings": [], "creator": c.creator.display_id, "fullname": c.creator.display_name, "profile_picture_url": "https://viima-app.s3.amazonaws.com/media/public/defaults/user-icon.png", "created_by_admin": False, "created_by_current_user": created_by_current_user, "upvote_count": c.up_vote_count, "user_has_upvoted": user_has_upvoted, "is_new": False }
		if c.file_url:
			comment['file_url'] = c.file_url
			comment['file_mime_type'] = c.file_mime_type
		commentsArray.append(comment)
		
	return JsonResponse(commentsArray, safe=False)
	
@login_required	
def post_comment(request, site_id, board_id, thread_id):
	data = { 'site_id':site_id, 'thread_id': thread_id, 'id': get_random_string(length=32), 'parent': request.POST.get('commentData[parent]'), 'content': request.POST.get('commentData[content]'), 'author': request.user, 'created': request.POST.get('commentData[created]'), 'modified': request.POST.get('commentData[modified]') }
	
	file_url = None
	file_mime_type = None
	try:
		file_url = re.search("(?P<url>https?://[^\s]+)", data['content']).group("url")
		if file_url:
			file_mime_type = mimetypes.guess_type(file_url)
			data['file_url'] = file_url
			data['file_mime_type'] = file_mime_type[0]
	except Exception as e:
		logger.warn(e)
		
	signal_new_comment.send_robust(sender=1, data=data)
	parent = None
	if data["parent"]:
		parent = data["parent"]
		
	comment = { "id": data['id'], "parent": parent, "created": data["created"], "modified": data["modified"], "content": data["content"], "pings": [], "creator": request.user.profile.display_id, "fullname": request.user.profile.display_name, "profile_picture_url": "https://viima-app.s3.amazonaws.com/media/public/defaults/user-icon.png", "created_by_admin": False, "created_by_current_user": True, "upvote_count": 0, "user_has_upvoted": False, "is_new": False }
	if file_mime_type:
		comment['file_mime_type'] = file_mime_type[0]
		comment['file_url'] = file_url
	return JsonResponse(comment)
	
@login_required	
def put_comment(request, site_id,  board_id, thread_id):
	data = { 'site_id':site_id, 'thread_id': thread_id, 'id': request.POST.get('commentData[id]'), 'parent': request.POST.get('commentData[parent]'), 'content': request.POST.get('commentData[content]'), 'author': request.user }
	signal_update_comment.send_robust(sender=1, data=data)
	return JsonResponse({'success': True})
	
@login_required	
def delete_comment(request, site_id,  board_id, thread_id):
	data = { 'site_id':site_id, 'thread_id': thread_id, 'id': request.POST.get('commentData[id]'), 'author': request.user }
	signal_delete_comment.send_robust(sender=1, data=data)
	return JsonResponse({'success': True})
	
@login_required	
def upvote_comment(request, site_id,  board_id, thread_id):
	data = { 'site_id':site_id, 'thread_id': thread_id, 'id': request.POST.get('commentData[id]'), 'author': request.user }
	signal_vote.send_robust(sender=1, data=data)
	return JsonResponse({'success': True})

"""
================================================================================================================================================================
COMMENT API RECIEVERS
================================================================================================================================================================
"""

@receiver(signal_new_comment)
def on_new_comment(sender, data, **kwargs):
	thread = None
	try:
		thread = Thread.objects.get(display_id=data['site_id']+data['thread_id'])
	except Exception as e:
		logger.warn(e)
		
	# If this comment has a parent make sure it is a valid one	
	parent_id = None
	if data['parent']:
		try:
			parent_id=data['parent']
			Comment.objects.get(comment_id=parent_id)
		except ObjectDoesNotExist:
			parent_id = None
		except Exception as e:
			parent_id = None
			logger.warn(e)
	else:
		parent_id = None
		
	comment = Comment(comment_id=data["id"], thread=thread, parent=parent_id, content=data['content'], creator=data['author'].profile)
	
	try:
		comment.file_mime_type = data['file_mime_type']
		comment.file_url = data['file_url']
	except:
		logger.info('saving comment without media')
			
	try:
		comment.save()
	except Exception as e:
		logger.warn(e)
		
    
@receiver(signal_update_comment)
def on_update_comment(sender, data, **kwargs):
    logger.info("signal_update_comment")
    
    comment = None
    try:
    	comment = Comment.objects.get( comment_id=data['id'], creator=data['author'].profile )
    except Exception as e:
    	logger.warn(e)
    
    if comment:
    	try:
    		comment.content = data['content']
    		comment.modified = datetime.datetime.now(tz=timezone.utc)
    		comment.save()
    	except Exception as e:
    		logger.warn(e)
    
    	
@receiver(signal_delete_comment)
def on_delete_comment(sender, data, **kwargs):
    logger.info("signal_delete_comment")
    
    comment = None
    try:
    	comment = Comment.objects.get( comment_id=data['id'], creator=data['author'].profile )
    except Exception as e:
    	logger.warn(e)
    
    if comment:
    	try:
    		comment.state = Constants.STATE_DELETED
    		comment.save()
    	except Exception as e:
    		logger.warn(e)
    
    
@receiver(signal_vote)
def on_vote_comment(sender, data, **kwargs):
    logger.info("signal_vote")
    comment_id = data['id']
    vote_down = False
    comment = None
    try:
    	comment = Comment.objects.get(comment_id=comment_id)
    except Exception as e:
    	logger.warn(e)
    	
    try:
    	vote = Vote.objects.get(comment=comment, voter=data['author'].profile)
    	vote.delete()
    	vote_down = True
    except ObjectDoesNotExist:
    	vote_down = False
    	try:
    		vote = Vote(comment=comment, voter=data['author'].profile)
    		vote.save()
    	except:
    		logger.warn(e)
    	
    try:
    	if vote_down:
    		comment.up_vote_count = comment.up_vote_count - 1
    	else:
    		comment.up_vote_count = comment.up_vote_count + 1
    	comment.save()
    except:
    	logger.warn(e)
    	
    
    
    
    