from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth import login
from .forms import SignUpForm, AuthenticationForm, ProjectForm, ProfileForm
from .models import Profile, Project, Like, Bookmark
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.db.models import Exists,OuterRef

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
    projects=Project.objects.all().order_by("-published_at")
    if request.user.is_authenticated:
        projects=projects.annotate(
            is_liked=Exists(
                Like.objects.filter(
                    project=OuterRef("pk"),
                    user=request.user.profile,
                )
            )
        )

    return render(request, "core/home.html", {"projects":projects})

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

@login_required
def new_project(request):
    if request.method=="POST":
        form=ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.author = request.user.profile
            project.save()
            form.save_m2m()
            return redirect("home")
    else:
        form=ProjectForm()
    return render(request, "core/new_project.html", {"form":form})

@login_required
def project_detail(request, pk):
    project=get_object_or_404(Project, pk=pk)
    return render(request, "core/project_detail.html", {"project":project})

@login_required
def project_edit(request, pk):
    project=get_object_or_404(Project,pk=pk)
    if request.user.profile != project.author:
        raise PermissionDenied
    if request.method == "POST":
        form=ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            form.save()
            return redirect("project_detail", pk=project.pk)
    else:
        form=ProjectForm(instance=project)
    return render(request, "core/project_edit.html", {"form":form, "project":project})

@login_required
def project_delete(request,pk):
    project=get_object_or_404(Project,pk=pk)
    if request.user.profile != project.author:
        raise PermissionDenied
    if request.method=="POST":
        project.delete()
        return redirect("home")
    
    return render(request, "core/project_delete.html", {"project":project})

@login_required
def profile_edit(request):
    if request.method == "POST":
        form=ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect("home")
    else:
        form=ProfileForm(instance=request.user.profile)
    return render(request, "core/profile_edit.html", {"form":form})

def profile_page(request, username):
    user = get_object_or_404(User, username=username)
    profile = user.profile

    return render(request, "core/profile_page.html", {"profile": profile,})

@login_required
@require_POST
def like(request,pk):
    project=get_object_or_404(Project,pk=pk)
    user=request.user.profile
    like, created = Like.objects.get_or_create(user=user,project=project)
    if not created:
        like.delete()
    return JsonResponse({
        "liked": created,
        "likes_count": project.likes.count(),
    })

@login_required
@require_POST
def bookmark(request,pk):
    project=get_object_or_404(Project,pk=pk)
    user=request.user.profile
    bookmark, created=Bookmark.objects.get_or_create(user=user,project=project)
    if not created:
        bookmark.delete()
    return JsonResponse({
        "bookmarked": created,
        "bookmarks_count":project.bookmarks.count(),
    })