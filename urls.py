from django.urls import path
from . import views

app_name = 'course_app'

urlpatterns = [
    # Course URLs
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    
    # Exam URLs - BOTH REQUIRED
    path('lesson/<int:lesson_id>/exam/', views.start_exam, name='start_exam'),
    path('lesson/<int:lesson_id>/submit/', views.submit, name='submit'),  # Required
    path('lesson/<int:lesson_id>/result/', views.show_exam_result, name='show_exam_result'),  # Required
    
    # Additional URLs
    path('lesson/<int:lesson_id>/stats/', views.exam_statistics, name='exam_statistics'),
    path('', views.course_detail, {'course_id': 1}, name='home'),
]
