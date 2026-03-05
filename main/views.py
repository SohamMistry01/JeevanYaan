from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserProfile, ModulesControl, UserModuleUsage
from .forms import RegistrationForm
from main.utils.career_planner import get_career_plan
from main.utils.mental_health_analyzer import get_mental_health_analysis
from main.utils.quiz_maker import generate_quiz_data, generate_explanations
from main.utils.research_agent import get_research_summary
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from main.utils.resume_scanner import analyze_resume
from main.utils.roadmap_creator import get_roadmap
from django.http import HttpResponse
from main.utils.pdf_generator import create_pdf_bytes
from main.utils.news_portal import get_top_news, NewsRequest
from main.utils.notes_assistant import run_notes_pipeline, process_uploaded_files
from main.utils.rate_limiter import check_and_get_limit
from django.utils import timezone
from django.contrib.auth.models import Group
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# --- NEW: Load Environment Variables ---
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

# -------------------
# REGISTER USER (Using RegistrationForm)
# -------------------
def register_user(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # hash password
            user.save()
            messages.success(request, "Registration successful! Please login.")
            return redirect('login')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})


# -------------------
# LOGIN USER
# -------------------
def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name}!")
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login')
    return render(request, 'login.html')


# -------------------
# HOME PAGE
# -------------------
def home_new(request):
    # 1. Authentication Check
    if not request.user.is_authenticated:
        return redirect('login')
        
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    
    # 2. Generate Thought of the Day
    thought_of_the_day = "The best way to predict the future is to create it." # Fallback thought
    try:
        if groq_api_key:
            # Use the model from your code
            llm = ChatGroq(model="moonshotai/kimi-k2-instruct") 
            result = llm.invoke(
                "Generate a random thought of the day on a career or health topic. Just include the thought in your response and nothing else."
            )
            thought_of_the_day = result.content
        else:
            print("GROQ_API_KEY not found. Using default thought.")
    except Exception as e:
        # If the API call fails for any reason, we'll just use the fallback thought
        print(f"Error generating thought of the day: {e}")
    
    # 3. Calculate Dynamic Daily Limits
    tools = [
        'career_planner', 
        'roadmap_creator', 
        'notes_assistant', 
        'quiz_maker', 
        'research_agent', 
        'news_portal', 
        'resume_scanner', 
        'mental_health_analyzer'
    ]
    
    # Default all limits to 'Unlimited'
    limits = {tool: 'Unlimited' for tool in tools}
    
    # Fetch user groups
    user_groups = request.user.groups.all()
    
    # Fallback to default group if user has no assigned role
    if not user_groups.exists():
        default_group, _ = Group.objects.get_or_create(name='External Users')
        request.user.groups.add(default_group)
        user_groups = [default_group]

    today = timezone.now().date()

    for tool in tools:
        # Check if there is a limit defined in ModulesControl for this tool and user's role(s)
        tool_limits = ModulesControl.objects.filter(name_of_module=tool, role__in=user_groups)
        
        if tool_limits.exists():
            # Get the highest limit available to the user (if they belong to multiple groups)
            max_limit = max([limit.daily_limit for limit in tool_limits])
            
            # Fetch today's usage count for this tool
            usage_record = UserModuleUsage.objects.filter(
                user=request.user, 
                module_name=tool, 
                date=today
            ).first()
            
            used = usage_record.usage_count if usage_record else 0
            
            # Calculate remaining (ensure it doesn't drop below 0)
            remaining = max(0, max_limit - used)
            
            # Update the dictionary with the numerical remaining value
            limits[tool] = remaining

    # 4. Pass the data into the context
    context = {
        'profile': profile,
        'thought_of_the_day': thought_of_the_day,
        'limits': limits  # Passes the dynamic limits dictionary to the template
    }
    
    return render(request, 'home.html', context)

def home_companion(request):
    if not request.user.is_authenticated:
        return redirect('login')
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'companion.html', {'profile': profile})

# -------------------
# LOGOUT
# -------------------
def logout_user(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('login')

# -------------------
# TOOL: CAREER PLANNER
# -------------------
def career_planner_view(request):
    result = None
    if request.method == 'POST':
        can_use, limit_context = check_and_get_limit(request.user, 'career_planner')
        if not can_use:
            # limit_context contains the error message
            messages.error(request, limit_context)
            # Redirect back to the same page so they see the error
            return redirect('career_planner')
        if 'download_pdf' in request.POST:
            content = request.POST.get('pdf_content', '')
            if content:
                try:
                    pdf_bytes = create_pdf_bytes(content)
                    response = HttpResponse(pdf_bytes, content_type='application/pdf')
                    # 'attachment' forces download; remove it to view in browser
                    response['Content-Disposition'] = 'attachment; filename="career_plan.pdf"'
                    return response
                except Exception as e:
                    # In production, handle gracefully. For now, print error.
                    print(f"PDF Error: {e}")

        name = request.POST.get('name')
        career = request.POST.get('career')
        education = request.POST.get('education')
        year = request.POST.get('year')
        skills = request.POST.get('skills')

        if all([name, career, education, year, skills]):
            # Call the utility function
            result = get_career_plan(name, career, education, year, skills)
            if limit_context is not None: # None means unlimited
                limit_context.usage_count += 1
                limit_context.save()
        else:
            # You can add django messages here for validation errors
            pass

    return render(request, 'tools/career_planner.html', {'result': result})

# -------------------
# TOOL: MENTAL HEALTH ANALYZER
# -------------------
def mental_health_analyzer_view(request):
    result = None
    
    # Pre-defined options for dropdowns
    options = {
        'genders': ['Female', 'Male', 'Non-binary', 'Prefer not to say'],
        'occupations': ['Engineering', 'Education', 'Finance', 'IT', 'Sales', 'Healthcare', 'Other'],
        'countries': ['USA', 'Canada', 'UK', 'Australia', 'Germany', 'India', 'Other'],
        'stress_levels': ['Low', 'Medium', 'High'],
        'diet_qualities': ['Healthy', 'Average', 'Unhealthy'],
        'smoking_habits': ['Non-Smoker', 'Regular Smoker', 'Heavy Smoker'],
        'alcohol_consumptions': ['Non-Drinker', 'Regular Drinker', 'Heavy Drinker']
    }

    # 1. Set default values for the first time the page loads
    user_data = {
        'age': 30, 'work_hours': 40, 'social_media': 2.0, 'sleep_hours': 7.0, 'physical_activity': 3,
        'gender': '', 'occupation': '', 'country': '', 'stress_level': '', 
        'diet_quality': '', 'smoking_habit': '', 'alcohol_consumption': ''
    }

    if request.method == 'POST':
        can_use, limit_context = check_and_get_limit(request.user, 'mental_health_analyzer')
        if not can_use:
            messages.error(request, limit_context)
            return redirect('mental_health_analyzer')
        
        if 'download_pdf' in request.POST:
            content = request.POST.get('pdf_content', '')
            if content:
                try:
                    pdf_bytes = create_pdf_bytes(content)
                    response = HttpResponse(pdf_bytes, content_type='application/pdf')
                    response['Content-Disposition'] = 'attachment; filename="mental_health_analysis.pdf"'
                    return response
                except Exception as e:
                    print(f"PDF Error: {e}")

        try:
            # 2. Capture the exact values submitted by the user
            user_data = {
                'age': request.POST.get('age', 30),
                'work_hours': request.POST.get('work_hours', 40),
                'social_media': request.POST.get('social_media', 2.0),
                'gender': request.POST.get('gender'),
                'occupation': request.POST.get('occupation'),
                'country': request.POST.get('country'),
                'sleep_hours': request.POST.get('sleep_hours', 7.0),
                'physical_activity': request.POST.get('physical_activity', 3),
                'stress_level': request.POST.get('stress_level'),
                'diet_quality': request.POST.get('diet_quality'),
                'smoking_habit': request.POST.get('smoking_habit'),
                'alcohol_consumption': request.POST.get('alcohol_consumption')
            }
            
            # Format data for the ML model
            data = {
                'Age': int(user_data['age']),
                'Gender': user_data['gender'],
                'Occupation': user_data['occupation'],
                'Country': user_data['country'],
                'Stress_Level': user_data['stress_level'],
                'Sleep_Hours': float(user_data['sleep_hours']),
                'Work_Hours': int(user_data['work_hours']),
                'Physical_Activity_Hours': int(user_data['physical_activity']),
                'Social_Media_Usage': float(user_data['social_media']),
                'Diet_Quality': user_data['diet_quality'],
                'Smoking_Habit': user_data['smoking_habit'],
                'Alcohol_Consumption': user_data['alcohol_consumption']
            }
            
            result = get_mental_health_analysis(data)
            
            if limit_context is not None:
                limit_context.usage_count += 1
                limit_context.save()
            
        except ValueError as e:
            pass

    context = {
        'result': result,
        'user_data': user_data,  # 3. Pass user data to the template
        **options
    }
    return render(request, 'tools/mental_health_analyzer.html', context)

# -------------------
# TOOL: QUIZ MAKER
# -------------------
def quiz_maker_view(request):
    # Initialize session keys if they don't exist
    if 'quiz_stage' not in request.session:
        request.session['quiz_stage'] = 'config' # config, taking, results
    
    context = {}

    if request.method == 'POST':
        can_use, limit_context = check_and_get_limit(request.user, 'quiz_maker')
        if not can_use:
            # limit_context contains the error message
            messages.error(request, limit_context)
            # Redirect back to the same page so they see the error
            return redirect('quiz_maker')

        if 'download_pdf' in request.POST:
            content = request.POST.get('pdf_content', '')
            if content:
                try:
                    pdf_bytes = create_pdf_bytes(content)
                    response = HttpResponse(pdf_bytes, content_type='application/pdf')
                    # 'attachment' forces download; remove it to view in browser
                    response['Content-Disposition'] = 'attachment; filename="quiz_result.pdf"'
                    return response
                except Exception as e:
                    # In production, handle gracefully. For now, print error.
                    print(f"PDF Error: {e}")

        action = request.POST.get('action')

        # --- ACTION: GENERATE QUIZ ---
        if action == 'generate':
            subject = request.POST.get('subject')
            topic = request.POST.get('topic')
            subtopic = request.POST.get('subtopic')
            difficulty = request.POST.get('difficulty')
            num_questions = int(request.POST.get('num_questions', 5))

            if subject and topic:
                quiz_data = generate_quiz_data(subject, topic, subtopic, difficulty, num_questions)
                if quiz_data:
                    # Store data in session to persist across requests
                    request.session['quiz_data'] = quiz_data
                    request.session['quiz_meta'] = {'topic': topic, 'difficulty': difficulty}
                    request.session['quiz_stage'] = 'taking'
                    return redirect('quiz_maker') # Redirect to avoid form resubmission issues

        # --- ACTION: SUBMIT ANSWERS ---
        elif action == 'submit':
            quiz_data = request.session.get('quiz_data', [])
            user_answers = {}
            score = 0
            incorrect_questions = []

            for i, q in enumerate(quiz_data):
                # Get the selected option (e.g., 'Option A Text')
                selected_option_text = request.POST.get(f'q_{i}') 
                user_answers[i] = selected_option_text
                
                correct_option_key = q['answer'] # 'A', 'B', etc.
                correct_option_text = q['options'].get(correct_option_key)

                if selected_option_text == correct_option_text:
                    score += 1
                else:
                    incorrect_questions.append({
                        "question_text": q['question'],
                        "user_answer": selected_option_text if selected_option_text else "No Answer",
                        "correct_answer": correct_option_text
                    })

            # Generate explanations if there are errors
            difficulty = request.session.get('quiz_meta', {}).get('difficulty', 'Beginner')
            explanations = generate_explanations(incorrect_questions, difficulty)

            # Save results to session
            request.session['quiz_results'] = {
                'score': score,
                'total': len(quiz_data),
                'percentage': (score / len(quiz_data)) * 100 if quiz_data else 0,
                'user_answers': user_answers,
                'incorrect_questions': incorrect_questions,
                'explanations': explanations
            }
            request.session['quiz_stage'] = 'results'
            if limit_context is not None: # None means unlimited
                limit_context.usage_count += 1
                limit_context.save()
            return redirect('quiz_maker')

        # --- ACTION: NEW QUIZ ---
        elif action == 'reset':
            # Clear specific session keys
            keys_to_delete = ['quiz_data', 'quiz_meta', 'quiz_results', 'quiz_stage']
            for key in keys_to_delete:
                if key in request.session:
                    del request.session[key]
            if limit_context is not None: # None means unlimited
                limit_context.usage_count += 1
                limit_context.save()
            return redirect('quiz_maker')

    # --- PREPARE CONTEXT BASED ON STAGE ---
    context['stage'] = request.session.get('quiz_stage', 'config')
    
    if context['stage'] == 'taking':
        context['quiz_data'] = request.session.get('quiz_data')
        context['meta'] = request.session.get('quiz_meta')
        
    elif context['stage'] == 'results':
        context['quiz_data'] = request.session.get('quiz_data')
        context['results'] = request.session.get('quiz_results')

    return render(request, 'tools/quiz_maker.html', context)

# -------------------
# TOOL: RESEARCH AGENT
# -------------------
def research_agent_view(request):
    result = None
    if request.method == 'POST':
        can_use, limit_context = check_and_get_limit(request.user, 'research_agent')
        if not can_use:
            # limit_context contains the error message
            messages.error(request, limit_context)
            # Redirect back to the same page so they see the error
            return redirect('research_agent')
        if 'download_pdf' in request.POST:
            content = request.POST.get('pdf_content', '')
            if content:
                try:
                    pdf_bytes = create_pdf_bytes(content)
                    response = HttpResponse(pdf_bytes, content_type='application/pdf')
                    # 'attachment' forces download; remove it to view in browser
                    response['Content-Disposition'] = 'attachment; filename="research_report.pdf"'
                    return response
                except Exception as e:
                    # In production, handle gracefully. For now, print error.
                    print(f"PDF Error: {e}")

        topic = request.POST.get('topic')
        if topic:
            result = get_research_summary(topic)
            if limit_context is not None: # None means unlimited
                limit_context.usage_count += 1
                limit_context.save()
    
    return render(request, 'tools/research_agent.html', {'result': result})

# -------------------
# TOOL: RESUME SCANNER
# -------------------
def resume_scanner_view(request):
    result = None
    
    if request.method == 'POST':
        can_use, limit_context = check_and_get_limit(request.user, 'resume_scanner')
        if not can_use:
            # limit_context contains the error message
            messages.error(request, limit_context)
            # Redirect back to the same page so they see the error
            return redirect('resume_scanner')

        if 'download_pdf' in request.POST:
            content = request.POST.get('pdf_content', '')
            if content:
                try:
                    pdf_bytes = create_pdf_bytes(content)
                    response = HttpResponse(pdf_bytes, content_type='application/pdf')
                    # 'attachment' forces download; remove it to view in browser
                    response['Content-Disposition'] = 'attachment; filename="resume_report.pdf"'
                    return response
                except Exception as e:
                    # In production, handle gracefully. For now, print error.
                    print(f"PDF Error: {e}")

        name = request.POST.get('name')
        uploaded_file = request.FILES.get('resume_file')

        if name and uploaded_file:
            # 1. Save file temporarily
            fs = FileSystemStorage()
            # Ensure the filename is safe and unique
            filename = fs.save(uploaded_file.name, uploaded_file)
            file_path = fs.path(filename)

            try:
                # 2. Process the file
                result = analyze_resume(name, file_path)
                if limit_context is not None: # None means unlimited
                    limit_context.usage_count += 1
                    limit_context.save()
            except Exception as e:
                result = f"Error processing file: {e}"
            finally:
                # 3. Cleanup: Delete the file after processing
                if os.path.exists(file_path):
                    os.remove(file_path)
        else:
            # You might want to handle missing fields with a message
            pass

    return render(request, 'tools/resume_scanner.html', {'result': result})

# -------------------
# TOOL: ROADMAP GENERATOR
# -------------------
def roadmap_creator_view(request):
    result = None
    domain = ""
    
    if request.method == 'POST':
        can_use, limit_context = check_and_get_limit(request.user, 'roadmap_creator')
        if not can_use:
            # limit_context contains the error message
            messages.error(request, limit_context)
            # Redirect back to the same page so they see the error
            return redirect('roadmap_creator')
        
        if 'download_pdf' in request.POST:
            content = request.POST.get('pdf_content', '')
            if content:
                try:
                    pdf_bytes = create_pdf_bytes(content)
                    response = HttpResponse(pdf_bytes, content_type='application/pdf')
                    # 'attachment' forces download; remove it to view in browser
                    response['Content-Disposition'] = 'attachment; filename="roadmap.pdf"'
                    return response
                except Exception as e:
                    # In production, handle gracefully. For now, print error.
                    print(f"PDF Error: {e}")

        domain = request.POST.get('domain')
        if domain:
            result = get_roadmap(domain)
            if limit_context is not None: # None means unlimited
                if result and not result.startswith("Error") and not result.startswith("An error occurred"):
                    limit_context.usage_count += 1
                    limit_context.save()
    
    return render(request, 'tools/roadmap_creator.html', {'result': result, 'domain': domain})

# -------------------
# TOOL: NOTES ASSISTANT
# -------------------
def notes_assistant_view(request):
    result = None
    user_intent = "summary"
    custom_instruction = ""

    if request.method == 'POST':
        can_use, limit_context = check_and_get_limit(request.user, 'notes_assistant')
        if not can_use:
            # limit_context contains the error message
            messages.error(request, limit_context)
            # Redirect back to the same page so they see the error
            return redirect('notes_assistant')
        # --- Handle PDF Download ---
        if 'download_pdf' in request.POST:
            content = request.POST.get('pdf_content', '')
            if content:
                try:
                    pdf_bytes = create_pdf_bytes(content)
                    response = HttpResponse(pdf_bytes, content_type='application/pdf')
                    response['Content-Disposition'] = 'attachment; filename="notes_assistant_report.pdf"'
                    return response
                except Exception as e:
                    print(f"PDF Error: {e}")

        # --- Handle Processing ---
        else:
            uploaded_files = request.FILES.getlist('files')
            user_intent = request.POST.get('user_intent', 'summary')
            custom_instruction = request.POST.get('custom_instruction', '')

            if not uploaded_files:
                result = "Please upload at least one file."
            elif len(uploaded_files) > 5:
                result = "⚠️ You can upload a maximum of 5 files at a time."
            else:
                try:
                    # Extract text from files
                    file_contents = process_uploaded_files(uploaded_files)
                    
                    if not file_contents:
                        result = "⚠️ Could not extract text from the uploaded files. Please check if they are valid .txt, .pdf, or .docx files."
                    else:
                        # Run the LangGraph Pipeline
                        result = run_notes_pipeline(file_contents, user_intent, custom_instruction)
                        if limit_context is not None: # None means unlimited
                            limit_context.usage_count += 1
                            limit_context.save()
                except Exception as e:
                    result = f"An error occurred during processing: {str(e)}"

    return render(request, 'tools/notes_assistant.html', {
        'result': result,
        'user_intent': user_intent,
        'custom_instruction': custom_instruction
    })

# -------------------
# TOOL: NEWS PORTAL 
# -------------------
def news_portal_view(request):
    result = None
    markdown_content = ""
    
    # Pre-defined options for the form
    categories = ["technology", "business", "science", "health", "sports", "politics", "general"]
    time_filters = ["daily", "weekly", "monthly"]
    
    if request.method == 'POST':
        can_use, limit_context = check_and_get_limit(request.user, 'news_portal')
        if not can_use:
            # limit_context contains the error message
            messages.error(request, limit_context)
            # Redirect back to the same page so they see the error
            return redirect('news_portal')

        # Handle PDF Download
        if 'download_pdf' in request.POST:
            content = request.POST.get('pdf_content', '')
            if content:
                try:
                    pdf_bytes = create_pdf_bytes(content)
                    response = HttpResponse(pdf_bytes, content_type='application/pdf')
                    response['Content-Disposition'] = 'attachment; filename="news_report.pdf"'
                    return response
                except Exception as e:
                    print(f"PDF Error: {e}")
                    messages.error(request, "Failed to generate PDF.")
                    return redirect('news_portal')
        
        # Handle News Generation
        try:
            category = request.POST.get('category')
            time_filter = request.POST.get('time_filter')
            limit = int(request.POST.get('limit', 5))
            
            if category and time_filter:
                req = NewsRequest(
                    category=category,
                    time_filter=time_filter,
                    limit=limit
                )
                
                # Fetch News
                response_dict = get_top_news(req)
                
                if "error" in response_dict:
                    result = {"error": response_dict["error"]}
                else:
                    result = response_dict["data"]
                    markdown_content = response_dict["markdown"]
                    if limit_context is not None: # None means unlimited
                        limit_context.usage_count += 1
                        limit_context.save()

        except Exception as e:
            result = {"error": f"An unexpected error occurred: {str(e)}"}

    context = {
        'result': result,
        'pdf_content': markdown_content,
        'categories': categories,
        'time_filters': time_filters
    }
    return render(request, 'tools/news_portal.html', context)



