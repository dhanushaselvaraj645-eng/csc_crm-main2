from django import forms
from .models import *

class LeadCaptureForm(forms.ModelForm):

    class Meta:
        model = LeadCapture
        fields = '__all__'

# Call-log form
class CallLogForm(forms.ModelForm):
    class Meta:
        model = CallLog
        fields = '__all__'