from django.db import models, IntegrityError
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.crypto import get_random_string

class Profile(models.Model):
	
	class Meta:
		app_label = 'core'
		
	def __unicode__(self):
		return self.display_id
		
	user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
	display_name = models.CharField(max_length=24)
	display_id = models.CharField(max_length=12, unique=True)
	date_created = models.DateTimeField(auto_now_add=True)
	last_updated = models.DateTimeField(auto_now=True)

	
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
	if created:
		Profile.objects.create(user=instance, display_id=get_random_string(length=12), display_name=instance.username)