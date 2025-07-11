from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    # path('dashboard/', views.dashboard),
    path('login', views.login_view, name='login'),
    path('register', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('vote/', views.voting_casting, name='voting_casting'),


    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('manage/candidates/', views.admin_candidates, name='admin_candidates'),
    path('manage/candidates/', views.admin_candidates, name='admin_candidates'),
    path('manage/candidates/add/', views.add_candidate, name='add_candidate'),
    path('manage/candidates/edit/<int:pk>/', views.edit_candidate, name='edit_candidate'),
    path('manage/candidates/delete/<int:pk>/', views.delete_candidate, name='delete_candidate'),
    path('public-results/', views.public_results, name='public_results'),

    ]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
