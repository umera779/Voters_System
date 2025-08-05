from django.contrib import admin

# Register your models here.
from . models import Candidate, Department, Position,Vote, Election
admin.site.register(Candidate)
admin.site.register(Department)
admin.site.register(Position)
admin.site.register(Vote) 
admin.site.register(Election)