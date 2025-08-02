from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='progress-home'),
    path('lesson/<int:lesson_id>/complete/', views.update_lesson_progress, name='complete_lesson'),
    path('api/course/<int:course_id>/', views.progress_api, name='progress_api'),
]
   