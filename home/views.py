import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import (
    AppointmentRequestForm,
    CareerForm,
    GalleryImageForm,
    LoginForm,
    ManagedFileForm,
    SERVICE_CHOICES,
)
from .models import Career, GalleryImage, ManagedFile

logger = logging.getLogger(__name__)


def index(request):
    featured_gallery = GalleryImage.objects.filter(is_active=True, is_featured=True)[:6]
    return render(request, 'home/index.html', {
        'featured_gallery': featured_gallery,
        'appointment_form': AppointmentRequestForm(),
    })


@require_POST
def book_appointment(request):
    form = AppointmentRequestForm(request.POST)
    if not form.is_valid():
        messages.error(request, 'Please check the form and try again.')
        return redirect(f"{reverse('index')}#book")

    data = form.cleaned_data
    service_label = dict(SERVICE_CHOICES).get(data['service'], data['service'])
    notify_to = getattr(settings, 'CONTACT_NOTIFY_EMAIL', 'info@stanthonyhcabossi.org')
    subject = f"Appointment request — {data['full_name']} ({service_label})"
    body = (
        f"New appointment request from the website\n"
        f"{'=' * 40}\n\n"
        f"Name:    {data['full_name']}\n"
        f"Phone:   {data['phone']}\n"
        f"Email:   {data['email'] or '—'}\n"
        f"Service: {service_label}\n"
        f"Date:    {data['preferred_date'].strftime('%d %b %Y')}\n\n"
        f"Notes:\n{data['message'] or '—'}\n"
    )

    email = EmailMessage(
        subject=subject,
        body=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[notify_to],
        reply_to=[data['email']] if data['email'] else None,
    )

    try:
        email.send(fail_silently=False)
    except Exception:
        logger.exception('Failed to send appointment email')
        messages.error(
            request,
            'We could not send your request right now. Please call 0739 983 657.',
        )
        return redirect(f"{reverse('index')}#book")

    messages.success(
        request,
        'Thank you — your appointment request was sent. We will confirm by phone.',
    )
    return redirect(f"{reverse('index')}#book")


def about(request):
    gallery_preview = GalleryImage.objects.filter(is_active=True)[:4]
    return render(request, 'home/about.html', {
        'gallery_preview': gallery_preview,
    })


def gallery(request):
    images = GalleryImage.objects.filter(is_active=True)
    categories = GalleryImage.Category.choices
    return render(request, 'home/gallery.html', {
        'images': images,
        'categories': categories,
    })


def careers(request):
    open_positions = Career.objects.filter(is_active=True)
    return render(request, 'home/careers.html', {
        'open_positions': open_positions,
    })


def career_detail(request, slug):
    career = get_object_or_404(Career, slug=slug, is_active=True)
    return render(request, 'home/career_detail.html', {
        'career': career,
    })


def login_view(request):
    if request.user.is_authenticated:
        return redirect('manage_dashboard')

    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        next_url = request.GET.get('next')
        if next_url and url_has_allowed_host_and_scheme(
            next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            return redirect(next_url)
        return redirect('manage_dashboard')

    return render(request, 'accounts/login.html', {
        'form': form,
    })


@require_POST
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been signed out.')
    return redirect('index')


@login_required
def manage_dashboard(request):
    return render(request, 'manage/dashboard.html', {
        'gallery_count': GalleryImage.objects.count(),
        'gallery_active': GalleryImage.objects.filter(is_active=True).count(),
        'file_count': ManagedFile.objects.count(),
        'file_active': ManagedFile.objects.filter(is_active=True).count(),
        'career_count': Career.objects.count(),
        'career_active': Career.objects.filter(is_active=True).count(),
        'recent_gallery': GalleryImage.objects.all()[:4],
        'recent_files': ManagedFile.objects.all()[:4],
        'recent_careers': Career.objects.all()[:4],
    })


@login_required
def manage_gallery_list(request):
    images = GalleryImage.objects.all()
    return render(request, 'manage/gallery_list.html', {
        'images': images,
    })


@login_required
def manage_gallery_upload(request):
    form = GalleryImageForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Gallery image uploaded.')
        return redirect('manage_gallery_list')
    return render(request, 'manage/gallery_form.html', {
        'form': form,
        'page_title': 'Upload gallery image',
        'submit_label': 'Upload image',
    })


@login_required
def manage_gallery_edit(request, pk):
    image = get_object_or_404(GalleryImage, pk=pk)
    form = GalleryImageForm(request.POST or None, request.FILES or None, instance=image)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Gallery image updated.')
        return redirect('manage_gallery_list')
    return render(request, 'manage/gallery_form.html', {
        'form': form,
        'image': image,
        'page_title': 'Edit gallery image',
        'submit_label': 'Save changes',
    })


@login_required
def manage_gallery_delete(request, pk):
    image = get_object_or_404(GalleryImage, pk=pk)
    if request.method == 'POST':
        title = image.title
        if image.image:
            image.image.delete(save=False)
        image.delete()
        messages.success(request, f'“{title}” deleted.')
        return redirect('manage_gallery_list')
    return render(request, 'manage/gallery_confirm_delete.html', {
        'image': image,
    })


@login_required
def manage_files_list(request):
    files = ManagedFile.objects.select_related('uploaded_by').all()
    return render(request, 'manage/files_list.html', {
        'files': files,
    })


@login_required
def manage_files_upload(request):
    form = ManagedFileForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        managed = form.save(commit=False)
        managed.uploaded_by = request.user
        managed.save()
        messages.success(request, 'File uploaded.')
        return redirect('manage_files_list')
    return render(request, 'manage/files_form.html', {
        'form': form,
        'page_title': 'Upload file',
        'submit_label': 'Upload file',
    })


@login_required
def manage_files_edit(request, pk):
    managed = get_object_or_404(ManagedFile, pk=pk)
    form = ManagedFileForm(request.POST or None, request.FILES or None, instance=managed)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'File updated.')
        return redirect('manage_files_list')
    return render(request, 'manage/files_form.html', {
        'form': form,
        'managed': managed,
        'page_title': 'Edit file',
        'submit_label': 'Save changes',
    })


@login_required
def manage_files_delete(request, pk):
    managed = get_object_or_404(ManagedFile, pk=pk)
    if request.method == 'POST':
        title = managed.title
        if managed.file:
            managed.file.delete(save=False)
        managed.delete()
        messages.success(request, f'“{title}” deleted.')
        return redirect('manage_files_list')
    return render(request, 'manage/files_confirm_delete.html', {
        'managed': managed,
    })


@login_required
def manage_careers_list(request):
    careers_list = Career.objects.all()
    return render(request, 'manage/careers_list.html', {
        'careers_list': careers_list,
    })


@login_required
def manage_careers_create(request):
    form = CareerForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Career posting created.')
        return redirect('manage_careers_list')
    return render(request, 'manage/careers_form.html', {
        'form': form,
        'page_title': 'Add career posting',
        'submit_label': 'Publish posting',
    })


@login_required
def manage_careers_edit(request, pk):
    career = get_object_or_404(Career, pk=pk)
    form = CareerForm(request.POST or None, instance=career)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Career posting updated.')
        return redirect('manage_careers_list')
    return render(request, 'manage/careers_form.html', {
        'form': form,
        'career': career,
        'page_title': 'Edit career posting',
        'submit_label': 'Save changes',
    })


@login_required
def manage_careers_delete(request, pk):
    career = get_object_or_404(Career, pk=pk)
    if request.method == 'POST':
        title = career.title
        career.delete()
        messages.success(request, f'“{title}” deleted.')
        return redirect('manage_careers_list')
    return render(request, 'manage/careers_confirm_delete.html', {
        'career': career,
    })
