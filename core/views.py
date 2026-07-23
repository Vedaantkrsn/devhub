from django.shortcuts import render,redirect
from django.contrib.auth import login
from .forms import SignUpForm, AuthenticationForm
from .models import Profile

# Create your views here.
def register(request):
    if request.method=="POST":
        form=SignUpForm(request.POST)
        if form.is_valid():
            new_user=form.save()
            Profile.objects.create(user=new_user)
            login(request,new_user)
            return redirect("home")
    else:
        form=SignUpForm()
    return render(request,"core/register.html", {"form":form})

def home(request):
    return render(request, "core/home.html")

def user_login(request):
    if request.method=="POST":
            form=AuthenticationForm(request, data=request.POST)
            if form.is_valid():
                user=form.get_user()
                
                login(request,user)
                return redirect("home")
    else:
        form=AuthenticationForm(request)
    return render(request,"core/user_login.html", {"form":form})