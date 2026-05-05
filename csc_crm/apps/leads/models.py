from django.db import models
from django.contrib.auth.models import User

# Lead Model
class LeadCapture(models.Model):

    COURSE_CHOICES  = [
        ('python', 'Python Full Stack'),
        ('java', 'Java Full Stack'),
        ('front_end','Front End'),
        ('back_end', 'Back End'),
        ('data_science', 'Data Science'),
        ('ai', 'Artificial Intelligence')
    ]

    SOURCE_CHOICES = [
        ('walk_in', 'Walk-in'),
        ('referral', 'Referral'),
        ('social_media', 'Social Media'),
        ('advertisement', 'Advertisement'),
        ('phone_enquiry', 'Phone Enquiry'),
        ('website', 'Website'),
    ]

    STATUS_CHOICES = [
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('interested', 'Interested'),
        ('demo_scheduled', 'Deme Scheduled'),
        ('enrolled', 'Enrolled'),
        ('lost', 'Lost')
    ]

    lead_id = models.CharField(max_length=10, unique=True)
    lead_name = models.CharField(max_length=100,)
    email = models.EmailField(blank=True, null=True, unique=True)
    phone_no = models.CharField(unique=True, max_length=12)
    course_interested = models.CharField(max_length=100)
    lead_source = models.CharField(max_length=100, choices=SOURCE_CHOICES)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)    
    initial_notes = models.TextField(null=True, blank=True)
    enquiry_date = models.DateField()
    next_followup_date = models.DateField()
    initial_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    
    def __str__(self):
        return self.lead_name


    
# Call-Log model
class CallLog(models.Model):
    LEAD_STATUS_CHOICES = [
        ('Interested', 'Interested'),
        ('Not Reachable', 'Not Reachable'),
        ('Demo Scheduled', 'Demo Scheduled'),
        ('Not Interested', 'Not Interested'),
    ]
    def __str__(self):
        return self.lead_name

    lead_name = models.CharField(max_length=100,null=True, blank= True)


    call_date = models.DateField(max_length=100,null=True, blank= True)
    call_time = models.TimeField(max_length=100,null=True, blank= True)

    duration = models.IntegerField(null=True, blank= True)  

    call_outcome = models.CharField(max_length=50, choices=LEAD_STATUS_CHOICES)

    notes = models.TextField(blank=True, null=True)

    next_followup_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)



