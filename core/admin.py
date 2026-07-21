from django.contrib import admin
from .models import Skill,Profile,Project,Comment,Like,Bookmark

# Register your models here.
admin.site.register(Skill)
admin.site.register(Profile)
admin.site.register(Project)
admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(Bookmark)