from django import forms
from comment.models import Site
from core.constants import Constants

class ContactForm(forms.Form):
    from_email = forms.EmailField(required=True)
    subject = forms.CharField(required=True)
    message = forms.CharField(widget=forms.Textarea, required=True)
    
    
class SiteForm(forms.Form):
	site_name = forms.CharField(required=True)
	site_url = forms.URLField(required=True)
	

class BoardForm(forms.Form):
	board_name = forms.CharField(required=True)
		
	def __init__(self, request, *args, **kwargs):
		self.request = kwargs.pop('request', None)
		super(BoardForm, self).__init__(*args, **kwargs)
		self.fields['site_id'] = forms.ChoiceField(
			choices=[(o.display_id, str(o.display_name)) for o in Site.objects.filter(owner=request.user.profile, state=Constants.STATE_VISIBLE) ]
		)
