from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required 
from .models import Candidate, Position, Vote
from django.http import JsonResponse
from django import forms
from .models import Department, Candidate, Position, Vote, Election
from django.contrib.auth.decorators import user_passes_test

# Create your views here.


from django.utils import timezone
from .models import Election
from django.utils import timezone

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['dept']

class PositionForm(forms.ModelForm):
    class Meta:
        model = Position
        fields = ['title']

class CandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ['name', 'candidate_position', 'votes', 'department', 'image']

class VoteForm(forms.ModelForm):
    class Meta:
        model = Vote
        fields = ['user', 'position', 'candidate']

class ElectionForm(forms.ModelForm):
    class Meta:
        model = Election
        fields = ['is_active', 'start_time', 'end_time', 'duration_minutes']

@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):
    departments = Department.objects.all()
    positions = Position.objects.all()
    candidates = Candidate.objects.all()
    votes = Vote.objects.all()
    elections = Election.objects.all()

    dept_form = DepartmentForm(request.POST or None)
    pos_form = PositionForm(request.POST or None)
    cand_form = CandidateForm(request.POST or None, request.FILES or None)
    vote_form = VoteForm(request.POST or None)
    election_form = ElectionForm(request.POST or None)

    # Handle deletion
    if request.method == 'POST':
        if 'delete_department' in request.POST:
            Department.objects.filter(id=request.POST.get('delete_department')).delete()
            return redirect('admin_dashboard')
        elif 'delete_position' in request.POST:
            Position.objects.filter(id=request.POST.get('delete_position')).delete()
            return redirect('admin_dashboard')
        elif 'delete_candidate' in request.POST:
            Candidate.objects.filter(id=request.POST.get('delete_candidate')).delete()
            return redirect('admin_dashboard')
        elif 'delete_vote' in request.POST:
            Vote.objects.filter(id=request.POST.get('delete_vote')).delete()
            return redirect('admin_dashboard')
        elif 'delete_election' in request.POST:
            Election.objects.filter(id=request.POST.get('delete_election')).delete()
            return redirect('admin_dashboard')
        # Only process the form that was submitted
        elif 'add_department' in request.POST and dept_form.is_valid():
            dept_form.save()
            return redirect('admin_dashboard')
        elif 'add_position' in request.POST and pos_form.is_valid():
            pos_form.save()
            return redirect('admin_dashboard')
        elif 'add_candidate' in request.POST and cand_form.is_valid():
            cand_form.save()
            return redirect('admin_dashboard')
        elif 'add_vote' in request.POST and vote_form.is_valid():
            vote_form.save()
            return redirect('admin_dashboard')
        elif 'add_election' in request.POST and election_form.is_valid():
            election_form.save()
            return redirect('admin_dashboard')

    context = {
        'departments': departments,
        'positions': positions,
        'candidates': candidates,
        'votes': votes,
        'elections': elections,
        'dept_form': dept_form,
        'pos_form': pos_form,
        'cand_form': cand_form,
        'vote_form': vote_form,
        'election_form': election_form,
    }
    return render(request, 'admin_dashboard.html', context)

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Position, Candidate

@login_required
def dashboard(request):
    is_admin = request.user.is_superuser or request.user.is_staff
    election = Election.objects.first()
    timer = election.time_left() if election and election.is_active else 0
    can_vote = election and election.is_active and timer > 0    
    positions = Position.objects.all()
    position_candidates = [
        (pos, Candidate.objects.filter(candidate_position=pos))
        for pos in positions
    ]
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = []
        for pos, candidates in position_candidates:
            data.append({
                'position': pos.title,
                'candidates': [
                    {
                        'name': c.name,
                        'department': str(c.department),
                        'votes': c.votes or 0,
                        'image': c.image.url if c.image else None  # Add this line
                    } for c in candidates
                ]
            })
        return JsonResponse({'results': data})
    
    context = {
        "position_candidates": position_candidates, 
        "timer": timer,
        "can_vote": can_vote,
        'is_admin': is_admin,

    }
    return render(request, 'dashboard.html', context)

def voting_casting(request):
    positions = Position.objects.all()
    position_candidates = [
        (pos, Candidate.objects.filter(candidate_position=pos))
        for pos in positions
    ]
    
    user_votes = {}
    for position in Position.objects.all():
        vote = Vote.objects.filter(user=request.user, candidate__candidate_position=position).first()
        user_votes[position.id] = vote.candidate.id if vote else None
    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        response = {"success": [], "warnings": []}
        for pos in positions:
            candidate_id = request.POST.get(f'position_{pos.id}')
            if candidate_id:
                candidate = Candidate.objects.get(id=candidate_id)
                if not Vote.objects.filter(user=request.user, position=pos).exists():
                    Vote.objects.create(user=request.user, position=pos, candidate=candidate)
                    candidate.votes = (candidate.votes or 0) + 1
                    candidate.save()
                    response["success"].append(f"Vote cast for {pos.title}.")
                else:
                    response["warnings"].append(f"You have already voted for {pos.title}.")
        
        if response["success"]:
            response["message"] = "Your votes have been cast."
        return JsonResponse(response)
    
    context = {
        'position_candidates': position_candidates,
        'user_votes': user_votes,
    }
    return render(request, 'voting_casting.html', context)


def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Login Successful")
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid Credentials')
            return redirect('login')
    return render(request, 'login.html')


def register_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm-password')

        if password != confirm_password:
            messages.error(request, 'Password Do Not Match')
            return render(request, 'register.html')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username Exists')
            return render(request, 'register.html')
        
        try:
            user = User.objects.create_user(username=username, 
                                            password=password, 
                                            is_active=True)
        except:
            messages.error(request, "Registration Failed")
            return render(request, 'register.html')
    return render(request, 'register.html')

from django.contrib.auth.views import LogoutView

from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    logout(request)
    return redirect('login')

def public_results(request):
    positions = Position.objects.all().order_by('title')
    votes_by_position = {}
    for pos in positions:
        votes = Vote.objects.filter(position=pos).select_related('user', 'candidate')
        votes_by_position[pos] = votes
    return render(request, 'public_results.html', {'votes_by_position': votes_by_position, 'positions': positions})


########## ADMIN CUSTOM VIEWS ##########

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Candidate, Department, Position, Vote, Election

def is_admin(user):
    return user.is_superuser or user.is_staff

@login_required
@user_passes_test(is_admin)
def admin_candidates(request):
    candidates = Candidate.objects.all()
    return render(request, 'admin_candidates.html', {'candidates': candidates})

@login_required
@user_passes_test(is_admin)
def add_candidate(request):
    departments = Department.objects.all()
    positions = Position.objects.all()
    if request.method == 'POST':
        name = request.POST.get('name')
        department_id = request.POST.get('department')
        position_id = request.POST.get('position')
        Candidate.objects.create(
            name=name,
            department_id=department_id,
            candidate_position_id=position_id
        )
        return redirect('admin_candidates')
    return render(request, 'add_candidate.html', {'departments': departments, 'positions': positions})

@login_required
@user_passes_test(is_admin)
def edit_candidate(request, pk):
    candidate = get_object_or_404(Candidate, pk=pk)
    departments = Department.objects.all()
    positions = Position.objects.all()
    if request.method == 'POST':
        candidate.name = request.POST.get('name')
        candidate.department_id = request.POST.get('department')
        candidate.candidate_position_id = request.POST.get('position')
        candidate.save()
        return redirect('admin_candidates')
    return render(request, 'edit_candidate.html', {'candidate': candidate, 'departments': departments, 'positions': positions})

@login_required
@user_passes_test(is_admin)
def delete_candidate(request, pk):
    candidate = get_object_or_404(Candidate, pk=pk)
    if request.method == 'POST':
        candidate.delete()
        return redirect('admin_candidates')
    return render(request, 'delete_candidate.html', {'candidate': candidate})

