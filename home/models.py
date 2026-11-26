from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Career(models.Model):
    class EmploymentType(models.TextChoices):
        FULL_TIME = 'full_time', 'Full Time'
        PART_TIME = 'part_time', 'Part Time'
        CONTRACT = 'contract', 'Contract'
        INTERNSHIP = 'internship', 'Internship'

    class Department(models.TextChoices):
        MEDICAL = 'medical', 'Medical'
        NURSING = 'nursing', 'Nursing'
        PHARMACY = 'pharmacy', 'Pharmacy'
        LABORATORY = 'laboratory', 'Laboratory'
        ADMINISTRATION = 'administration', 'Administration'
        SUPPORT = 'support', 'Support Services'

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    department = models.CharField(max_length=30, choices=Department.choices)
    employment_type = models.CharField(
        max_length=20,
        choices=EmploymentType.choices,
        default=EmploymentType.FULL_TIME,
    )
    location = models.CharField(max_length=120, default='Abossi, Trans Mara East, Narok County')
    summary = models.TextField(
        help_text='Brief overview shown on the careers listing page.',
    )
    description = models.TextField(
        help_text='Full role description and context.',
    )
    responsibilities = models.TextField(
        help_text='Enter each responsibility on a new line.',
    )
    requirements = models.TextField(
        help_text='Enter each requirement on a new line.',
    )
    application_email = models.EmailField(
        blank=True,
        help_text='Leave blank to use the default careers email.',
    )
    is_active = models.BooleanField(default=True)
    posted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    closing_date = models.DateField(
        null=True,
        blank=True,
        help_text='Optional application deadline.',
    )

    class Meta:
        ordering = ['-posted_at']
        verbose_name_plural = 'careers'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Career.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('career_detail', kwargs={'slug': self.slug})

    @property
    def responsibilities_list(self):
        return [line.strip() for line in self.responsibilities.splitlines() if line.strip()]

    @property
    def requirements_list(self):
        return [line.strip() for line in self.requirements.splitlines() if line.strip()]

    @property
    def apply_email(self):
        return self.application_email or 'St.anthonysabossi.hc@gmail.com'


class GalleryImage(models.Model):
    class Category(models.TextChoices):
        FACILITY = 'facility', 'Facility'
        STAFF = 'staff', 'Staff & Team'
        EVENTS = 'events', 'Events & Outreach'
        COMMUNITY = 'community', 'Community'
        SERVICES = 'services', 'Services'

    title = models.CharField(max_length=200)
    caption = models.CharField(max_length=300, blank=True)
    image = models.ImageField(upload_to='gallery/')
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.FACILITY,
    )
    is_featured = models.BooleanField(
        default=False,
        help_text='Show on the landing page gallery preview.',
    )
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sort_order', '-created_at']
        verbose_name = 'gallery image'
        verbose_name_plural = 'gallery images'

    def __str__(self):
        return self.title


class ManagedFile(models.Model):
    class FileKind(models.TextChoices):
        DOCUMENT = 'document', 'Document'
        IMAGE = 'image', 'Image'
        OTHER = 'other', 'Other'

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='uploads/%Y/%m/')
    kind = models.CharField(
        max_length=20,
        choices=FileKind.choices,
        default=FileKind.DOCUMENT,
    )
    is_active = models.BooleanField(default=True)
    uploaded_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_files',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'managed file'
        verbose_name_plural = 'managed files'

    def __str__(self):
        return self.title

    @property
    def filename(self):
        return self.file.name.rsplit('/', 1)[-1] if self.file else ''

