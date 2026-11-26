from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('book/', views.book_appointment, name='book_appointment'),
    path('about/', views.about, name='about'),
    path('gallery/', views.gallery, name='gallery'),
    path('careers/', views.careers, name='careers'),
    path('careers/<slug:slug>/', views.career_detail, name='career_detail'),

    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('manage/', views.manage_dashboard, name='manage_dashboard'),
    path('manage/gallery/', views.manage_gallery_list, name='manage_gallery_list'),
    path('manage/gallery/upload/', views.manage_gallery_upload, name='manage_gallery_upload'),
    path('manage/gallery/<int:pk>/edit/', views.manage_gallery_edit, name='manage_gallery_edit'),
    path('manage/gallery/<int:pk>/delete/', views.manage_gallery_delete, name='manage_gallery_delete'),
    path('manage/files/', views.manage_files_list, name='manage_files_list'),
    path('manage/files/upload/', views.manage_files_upload, name='manage_files_upload'),
    path('manage/files/<int:pk>/edit/', views.manage_files_edit, name='manage_files_edit'),
    path('manage/files/<int:pk>/delete/', views.manage_files_delete, name='manage_files_delete'),
    path('manage/careers/', views.manage_careers_list, name='manage_careers_list'),
    path('manage/careers/add/', views.manage_careers_create, name='manage_careers_create'),
    path('manage/careers/<int:pk>/edit/', views.manage_careers_edit, name='manage_careers_edit'),
    path('manage/careers/<int:pk>/delete/', views.manage_careers_delete, name='manage_careers_delete'),
]
