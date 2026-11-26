from django.contrib import admin

from .models import Career, GalleryImage, ManagedFile


@admin.register(Career)
class CareerAdmin(admin.ModelAdmin):
    list_display = ('title', 'department', 'employment_type', 'is_active', 'posted_at', 'closing_date')
    list_filter = ('is_active', 'department', 'employment_type')
    search_fields = ('title', 'summary', 'description')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('posted_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'department', 'employment_type', 'location', 'is_active'),
        }),
        ('Job Details', {
            'fields': ('summary', 'description', 'responsibilities', 'requirements'),
        }),
        ('Application', {
            'fields': ('application_email', 'closing_date'),
        }),
        ('Timestamps', {
            'fields': ('posted_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'is_featured', 'is_active', 'sort_order', 'created_at')
    list_filter = ('category', 'is_featured', 'is_active')
    search_fields = ('title', 'caption')
    list_editable = ('is_featured', 'is_active', 'sort_order')


@admin.register(ManagedFile)
class ManagedFileAdmin(admin.ModelAdmin):
    list_display = ('title', 'kind', 'is_active', 'uploaded_by', 'created_at')
    list_filter = ('kind', 'is_active')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at')
