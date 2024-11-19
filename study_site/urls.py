from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('', views.login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('courses/', views.course_list, name='course_list'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('course/add/', views.add_course, name='add_course'),
    path('course/<int:course_id>/lessons/add/', views.add_lesson, name='add_lesson'),
    path('lesson/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    path('grade-answer/<int:answer_id>/', views.grade_answer, name='grade_answer'),
    path('profile/', views.profile_view, name='profile'),
    path('create_team/', views.create_team, name='create_team'),
    path('create_match/', views.create_match, name='create_match'),
    path('team_list/', views.team_list, name='team_list'),
    path('team/<int:team_id>/', views.team_detail, name='team_detail'),
    path('match_list/', views.match_list, name='match_list'),
    path('contact/', views.contact_view, name='contact')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)