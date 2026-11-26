from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import Career, GalleryImage, ManagedFile


SERVICE_CHOICES = [
    ('outpatient', 'Out-patient'),
    ('inpatient', 'In-patient'),
    ('maternity', 'Maternity & MCH'),
    ('laboratory', 'Laboratory'),
    ('xray', 'X-ray'),
    ('ultrasound', 'Ultra-sound'),
    ('ccc', 'CCC (HIV/AIDS Care)'),
    ('pmtct', 'PMTCT'),
    ('hts', 'PITC / HTS'),
    ('referral', 'Referral'),
    ('morgue', 'Morgue Services'),
]


class AppointmentRequestForm(forms.Form):
    full_name = forms.CharField(max_length=120)
    phone = forms.CharField(max_length=40)
    email = forms.EmailField(required=False)
    service = forms.ChoiceField(choices=SERVICE_CHOICES)
    message = forms.CharField(required=False, widget=forms.Textarea)


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'field-control',
            'placeholder': 'Username',
            'autocomplete': 'username',
            'autofocus': True,
        }),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'field-control',
            'placeholder': 'Password',
            'autocomplete': 'current-password',
        }),
    )


class GalleryImageForm(forms.ModelForm):
    class Meta:
        model = GalleryImage
        fields = (
            'title',
            'caption',
            'image',
            'category',
            'is_featured',
            'is_active',
            'sort_order',
        )
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'field-control',
                'placeholder': 'Image title',
            }),
            'caption': forms.TextInput(attrs={
                'class': 'field-control',
                'placeholder': 'Optional caption',
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'field-control field-control--file',
                'accept': 'image/*',
            }),
            'category': forms.Select(attrs={'class': 'field-control'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'field-check'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'field-check'}),
            'sort_order': forms.NumberInput(attrs={
                'class': 'field-control',
                'min': 0,
            }),
        }


class ManagedFileForm(forms.ModelForm):
    class Meta:
        model = ManagedFile
        fields = ('title', 'description', 'file', 'kind', 'is_active')
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'field-control',
                'placeholder': 'File title',
            }),
            'description': forms.Textarea(attrs={
                'class': 'field-control',
                'rows': 3,
                'placeholder': 'Optional description',
            }),
            'file': forms.ClearableFileInput(attrs={
                'class': 'field-control field-control--file',
            }),
            'kind': forms.Select(attrs={'class': 'field-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'field-check'}),
        }


class CareerForm(forms.ModelForm):
    class Meta:
        model = Career
        fields = (
            'title',
            'department',
            'employment_type',
            'location',
            'summary',
            'description',
            'responsibilities',
            'requirements',
            'application_email',
            'closing_date',
            'is_active',
        )
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'field-control',
                'placeholder': 'Job title',
            }),
            'department': forms.Select(attrs={'class': 'field-control'}),
            'employment_type': forms.Select(attrs={'class': 'field-control'}),
            'location': forms.TextInput(attrs={
                'class': 'field-control',
                'placeholder': 'Abossi, Trans Mara East, Narok County',
            }),
            'summary': forms.Textarea(attrs={
                'class': 'field-control',
                'rows': 3,
                'placeholder': 'Short overview for the careers listing',
            }),
            'description': forms.Textarea(attrs={
                'class': 'field-control',
                'rows': 5,
                'placeholder': 'Full role description',
            }),
            'responsibilities': forms.Textarea(attrs={
                'class': 'field-control',
                'rows': 6,
                'placeholder': 'One responsibility per line',
            }),
            'requirements': forms.Textarea(attrs={
                'class': 'field-control',
                'rows': 6,
                'placeholder': 'One requirement per line',
            }),
            'application_email': forms.EmailInput(attrs={
                'class': 'field-control',
                'placeholder': 'Leave blank for default email',
            }),
            'closing_date': forms.DateInput(attrs={
                'class': 'field-control',
                'type': 'date',
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'field-check'}),
        }
