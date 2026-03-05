from django.shortcuts import redirect
from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('', lambda request: redirect('login')),  # Default → Login page
    path('login/', views.login_user, name='login'),
    path('register/', views.register_user, name='register'),
    path('logout/', views.logout_user, name='logout'),

    # Home Dashboard
    path('home/', views.home_new, name='home'),          # New clean homepage
    path('companion/', views.home_companion, name='companion'), # Old iframe page

    # Tools
    path('tools/career-planner/', views.career_planner_view, name='career_planner'),
    path('tools/mental-health-analyzer/', views.mental_health_analyzer_view, name='mental_health_analyzer'),
    path('tools/quiz-maker/', views.quiz_maker_view, name='quiz_maker'),
    path('tools/research-agent/', views.research_agent_view, name='research_agent'),
    path('tools/resume-scanner/', views.resume_scanner_view, name='resume_scanner'),
    path('tools/roadmap-generator/', views.roadmap_creator_view, name='roadmap_creator'),
    path('tools/notes-assistant/', views.notes_assistant_view, name='notes_assistant'),
    path('tools/news-portal/', views.news_portal_view, name='news_portal'),

    # Streamlit app redirects
    path('career-path/', lambda r: redirect('http://localhost:8501')),
    path('roadmap-generator/', lambda r: redirect('http://localhost:8502')),
    path('notes-assistant/', lambda r: redirect('http://localhost:8503')),
    path('quiz-maker/', lambda r: redirect('http://localhost:8504')),
    path('research-agent/', lambda r: redirect('http://localhost:8505')),
    path('news-portal/', lambda r: redirect('http://localhost:8506')),
    path('resource-generator/', lambda r: redirect('http://localhost:8507')),
    path('mental-health-analyzer/', lambda r: redirect('http://localhost:8508')),
]
