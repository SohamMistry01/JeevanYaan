from django.shortcuts import render, redirect
from django.contrib import messages
from .models import UserProfile
from .forms import UserProfileForm

def my_profile_view(request):
    # 1. Ensure user is logged in
    if not request.user.is_authenticated:
        return redirect('login')
        
    # 2. Fetch or create the user's profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # 3. Handle Form Submission
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been successfully updated!")
            return redirect('my_profile')
        else:
            messages.error(request, "There was an error updating your profile. Please check the fields below.")
    else:
        # GET Request: Load the form with existing data
        form = UserProfileForm(instance=profile)
        
    context = {
        'form': form
    }
    
    return render(request, 'my_profile.html', context)