from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Count
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from .models import *
from .forms import *

def lead_capture_list(request):

    leads = LeadCapture.objects.all().order_by('-created_at')

    # Filter by status if provided
    status = request.GET.get('status')
    if status:
        leads = leads.filter(initial_status=status)

    # Search by Assigned Staff
    assigned_to = request.GET.get('assigned_to')
    if assigned_to:
        leads = leads.filter(assigned_to=assigned_to)

    # Filtered by Functionality
    search_query = request.GET.get('search')
    if search_query:
        leads = leads.filter(
            Q(lead_name__icontains=search_query)|
            Q(email__icontains = search_query)|
            Q(phone_no__icontains=search_query)
        )

    # Get recent Leads for Today
    today = timezone.now().date()
    recent_leads = LeadCapture.objects.filter(enquiry_date=today).order_by('-created_at')[:10]

    # Get Status Counts
    status_counts = LeadCapture.objects.values('initial_status').annotate(count=Count('id'))

    # Context
    context = {
        'leads': leads,
        'recent_leads': recent_leads,
        'status_counts': status_counts,
        'search_query': search_query
    }

    return render(request, 'leads/lead_list.html', context)

# Get Lead in Leads and Their Information
def lead_capture_details(request, id):

    lead = get_object_or_404(LeadCapture, id=id)

    context = {
        'lead':lead
    }
    return render(request, 'leads/lead_details.html', context)

#Create Leads
@require_http_methods(["GET", "POST"])
def lead_capture_create(request):
    if request.method == 'POST':
        form = LeadCaptureForm(request.POST)
        if form.is_valid():
            lead = form.save(commit=False)
            lead_count = LeadCapture.objects.count()+1
            lead.lead_id = f'LID-{lead_count:04d}'
            lead.save()
            messages.success(request, f'Lead{lead.lead_name} created successfully!')
            return redirect('lead_capture_details')
    else:
        form = LeadCaptureForm()

    context = {
        'form': form,
        'page_title':'New Lead Entry',
    }

    return render(request, 'leads/lead_list.html', context)

# Update leads
@require_http_methods(['GET','POST'])
def lead_capture_update(request, id):
    lead = get_object_or_404(LeadCapture, id=id)

    if request.method == 'POST':
        form = LeadCaptureForm(request.POST, instance=lead)
        if form.is_valid():
            form.save()
            messages.success(request, f'Lead {lead.lead_name} updated successfully!')
            return redirect('lead_capture_details', id=lead.id)
    else:
        form = LeadCaptureForm(instance=lead)
        
        context = {
            'form':form,
            'lead':lead,
            'pade_title':f'Edit Lead - {lead.lead_name}',
        }
    return render(request, 'leads/lead_form.html', context)

# Deleting Lead
@require_http_methods(['POST'])
def lead_capture_delete(request, id):
    lead = get_object_or_404(LeadCapture, id=id)
    lead_name = lead.lead_name
    lead.delete()
    messages.success(request, f'Lead {lead.lead_name} Deleted Successfully!')
    return redirect('lead_capture_list')

# PipeLine View
def lead_pipeline_view(request):

    leads_by_status = {}
    status_choices = LeadCapture.STATUS_CHOICES

    for status_value, status_label in status_choices:
        leads_by_status[status_label] = LeadCapture.objects.filter(initial_status=status_value)
   
    # Get funnel Data
    total_leads = LeadCapture.objects.count()
    funnel_data = []

    for status_value, status_label in status_choices:
        count = LeadCapture.objects.filter(initial_status=status_value).count()
        percentage = (count / total_leads * 100) if total_leads > 0 else 0
        funnel_data.append({
            'status': status_label,
            'count': count,
            'percentage': round(percentage, 1)
        })

        context = {
            'leads_by_status': leads_by_status,
            'funnel_data':funnel_data,
            'total_leads':total_leads,
        }

        return render(request, 'leads/pipeline_view.html', context)

# Lead Conversion 
def lead_conversion_report(request):
    total_leads = LeadCapture.objects.count()
    enrolled_leads = LeadCapture.objects.filter(initial_status='enrolled').count()
    lost_leads = LeadCapture.objects.filter(initial_status='lost').count()

    conversion_rate = (enrolled_leads / total_leads *100) if total_leads > 0 else 0

    # Source performance
    source_performance = []
    for source_value, source_label in LeadCapture.SOURCE_CHOICES:
        total = LeadCapture.objects.filter(lead_source=source_value).count()
        enrolled = LeadCapture.objects.filter(
            lead_source = source_value,
            initial_status = 'enrolled',
        ).count()
        rate = (enrolled / total * 100) if total > 0 else 0

        source_performance.append({
        'source' : source_label,
        'total': total,
        'enrolled':enrolled,
        'rate':round(rate,1), 
        })

    context = {
        'total_leads':total_leads,
        'enrolled_leads':enrolled_leads,
        'lost_leads':lost_leads,
        'conversion_rate':conversion_rate,
        'source_performance':source_performance,
    }

    return render(request, 'leads/conversion_report.html',context)



def followup_shedule(request):
    today = timezone.now().date()
    week_end = today + timedelta(days=7)

    base_queryset = LeadCapture.objects.exclude(
        initial_status__in=['enrolled', 'lost']
    )

    # Overdue (strictly less than today)
    overdue = base_queryset.filter(next_followup_date__lt=today)

    # Today only
    today_followups = base_queryset.filter(next_followup_date=today)

    # This week (EXCLUDE today)
    week_followups = base_queryset.filter(
        next_followup_date__gt=today,
        next_followup_date__lte=week_end
    )

    context = {
        'overdue': overdue,
        'today_followups': today_followups,
        'week_followups': week_followups,
        'due_today': today_followups.count(),
        'overdue_count': overdue.count(),
        'this_week': week_followups.count(),
        'completed_today': LeadCapture.objects.filter(
            updated_at__date=today,
            initial_status__in=['enrolled', 'lost']
        ).count(),
    }

    return render(request, 'leads/followup_schedule.html', context)

# Call-log View
def call_log_view(request):
    if request.method == 'POST':
        form = CallLogForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('call_logs')  
    else:
        form = CallLogForm()

    logs = CallLog.objects.all().order_by('-created_at')

    return render(request, 'leads/call_logs.html', {
        'form': form,
        'logs': logs
    })

def delete_call_log(request, id):
    
    log = get_object_or_404(CallLog, id=id)
    log.delete()
    return redirect('call_logs')
