from django.db import models
from core.models import Profile
from core.constants import Constants

# Create your models here.
# Later this will require splitting off so don't add too many dependencies on core

class Site(models.Model):
	
	class Meta:
		app_label = 'comment'
		
	def __unicode__(self):
		return self.display_id
	
	owner = models.ForeignKey(Profile, on_delete=models.CASCADE)	
	display_id = models.CharField(max_length=12)
	display_name = models.CharField(max_length=48)
	site_url = models.CharField(max_length=255)
	date_created = models.DateTimeField(auto_now_add=True)
	last_updated = models.DateTimeField(auto_now=True)
	state = models.IntegerField(choices=Constants.CONTENT_STATES, default=Constants.STATE_VISIBLE, db_index=True)


class Board(models.Model):
	
	class Meta:
		app_label = 'comment'
		
	def __unicode__(self):
		return self.display_id
		
	site = models.ForeignKey(Site, on_delete=models.CASCADE)
	owner = models.ForeignKey(Profile, on_delete=models.CASCADE)
	display_id = models.CharField(max_length=12, unique=True)
	display_name = models.CharField(max_length=48)
	date_created = models.DateTimeField(auto_now_add=True)
	last_updated = models.DateTimeField(auto_now=True)
	state = models.IntegerField(choices=Constants.CONTENT_STATES, default=Constants.STATE_VISIBLE, db_index=True)


class Thread(models.Model):
	
	class Meta:
		app_label = 'comment'
		
	def __unicode__(self):
		return self.display_id
	
	board = models.ForeignKey(Board, on_delete=models.CASCADE)	
	owner = models.ForeignKey(Profile, on_delete=models.CASCADE)
	site_id = models.CharField(max_length=12)
	display_id = models.CharField(max_length=24, unique=True)
	date_created = models.DateTimeField(auto_now_add=True)
	last_updated = models.DateTimeField(auto_now=True)
	
	
	
class Comment(models.Model):
	
	class Meta:
		app_label = 'comment'
		
	def __unicode__(self):
		return self.display_id
	
	comment_id = models.CharField(max_length=32, unique=True)
	thread = models.ForeignKey(Thread, on_delete=models.CASCADE)
	parent = models.CharField(max_length=32, null=True)
	date_created = models.DateTimeField(auto_now_add=True)
	last_updated = models.DateTimeField(auto_now=True)
	modified = models.DateTimeField(null=True)
	content = models.CharField(max_length=500, null=True)
	creator = models.ForeignKey(Profile, on_delete=models.CASCADE)
	up_vote_count = models.IntegerField(default=0)
	state = models.IntegerField(choices=Constants.CONTENT_STATES, default=Constants.STATE_VISIBLE, db_index=True)
	file_mime_type = models.CharField(max_length=32, null=True)
	file_url = models.CharField(max_length=255, null=True)
	
	# state
	
	
class Vote(models.Model):
	
	class Meta:
		app_label = 'comment'
		
	def __unicode__(self):
		return self.display_id
		
	comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
	voter = models.ForeignKey(Profile, on_delete=models.CASCADE)
	date_created = models.DateTimeField(auto_now_add=True)
	last_updated = models.DateTimeField(auto_now=True)