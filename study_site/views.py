from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.shortcuts import redirect
from django.http import HttpResponseNotAllowed, HttpResponseRedirect 
from django.contrib.auth.decorators import login_required
from functools import wraps
from .forms import CustomUserCreationForm, CourseForm, ProfileForm, LessonForm, AnswerForm, GradeForm, TeamForm, MatchForm, MatchFilterForm
from .models import Course, Lesson, Profile, User, Answer, Team, Match
from django.contrib.auth.forms import AuthenticationForm

def get_user_role(user):
    return getattr(user, 'role', None)

def role_required(role):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if getattr(request.user, 'role', None) == role:
                return view_func(request, *args, **kwargs)
            return redirect('dashboard')  # Or a 403 page
        return _wrapped_view
    return decorator


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})

def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect('login')
    else:
        return HttpResponseNotAllowed(['POST'])

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()

    return render(request, 'register.html', {'form': form})

@login_required
def dashboard(request):
    courses = Course.objects.all().prefetch_related('students')
    return render(request, 'dashboard.html', {'courses': courses})

@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    # Получаем студентов, которые еще не добавлены в курс
    available_students = User.objects.exclude(id__in=course.students.values('id'))

    if request.method == 'POST' and 'student' in request.POST:
        student_id = request.POST['student']
        student = get_object_or_404(User, id=student_id)
        course.students.add(student)
        return HttpResponseRedirect(request.path)

    return render(request, 'course_detail.html', {
        'course': course,
        'available_students': available_students,
    })


@login_required
@role_required('teacher')
def add_course(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save(commit=False)
            course.teacher = request.user
            course.save()
            return redirect('course_list')
    else:
        form = CourseForm()
    return render(request, 'add_course.html', {'form': form})

@login_required
def course_list(request):
    courses = Course.objects.all()
    return render(request, 'course_list.html', {'courses': courses})


def is_teacher(user):
    return user.groups.filter(name='Teachers').exists()

@login_required
@role_required('teacher')
def grade_answer(request, answer_id):
    answer = get_object_or_404(Answer, id=answer_id)

    if request.method == 'POST':
        form = GradeForm(request.POST, instance=answer)
        if form.is_valid():
            form.save()
            return redirect('lesson_detail', lesson_id=answer.lesson.id)
    else:
        form = GradeForm(instance=answer)

    return render(request, 'grade_answer.html', {
        'form': form,
        'answer': answer,
    })

@login_required
@role_required('teacher')
def add_lesson(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.method == 'POST':
        form = LessonForm(request.POST)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.course = course 
            lesson.save()
            return redirect('course_detail', course_id=course.id)
    else:
        form = LessonForm()

    return render(request, 'add_lesson.html', {'form': form, 'course': course})

@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    lessons = course.lessons.all()
    return render(request, 'course_detail.html', {'course': course, 'lessons': lessons})

@login_required
def lesson_detail(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    answers = lesson.answers.filter(student=request.user)

    if request.method == 'POST':
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.student = request.user
            answer.lesson = lesson
            answer.save()
            return redirect('lesson_detail', lesson_id=lesson.id)
    else:
        form = AnswerForm()

    return render(request, 'lesson_detail.html', {
        'lesson': lesson,
        'form': form,
        'answers': answers
    })

@login_required
@role_required('teacher')
def add_student_to_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.user != course.teacher:
        return redirect('course_detail', course_id=course.id)

    if request.method == 'POST' and 'student' in request.POST:
        student_id = request.POST['student']
        student = get_object_or_404(User, id=student_id)
        course.students.add(student)
        return redirect('course_detail', course_id=course.id)

    available_students = User.objects.exclude(id__in=course.students.values('id'))

    return render(request, 'course_detail.html', {
        'course': course,
        'available_students': available_students,
    })


@login_required
def profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile') 
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'profile.html', {'form': form})


@login_required
@role_required('teacher')
def create_team(request):
    if request.method == 'POST':
        form = TeamForm(request.POST)
        if form.is_valid():
            team = form.save(commit=False)
            team.coach = request.user  # Связываем тренера с командой
            team.save()  # Сохраняем команду
            form.save_m2m()  # Сохраняем связи с игроками

            # Обновляем связь игроков с командой
            for player in form.cleaned_data['players']:
                player.teams.add(team)  # Добавляем команду к игроку

            return redirect('team_list')  # Перенаправляем на список команд

    else:
        form = TeamForm()

    return render(request, 'create_team.html', {'form': form})

@login_required
def match_list(request):
    # Получаем фильтры из запроса
    form = MatchFilterForm(request.GET)
    matches = Match.objects.all()

    # Применяем фильтрацию по данным из формы
    if form.is_valid():
        if form.cleaned_data.get('team_1'):
            matches = matches.filter(team_1=form.cleaned_data['team_1'])
        if form.cleaned_data.get('team_2'):
            matches = matches.filter(team_2=form.cleaned_data['team_2'])
        if form.cleaned_data.get('result'):
            matches = matches.filter(result__icontains=form.cleaned_data['result'])
        if form.cleaned_data.get('date_from'):
            matches = matches.filter(date__gte=form.cleaned_data['date_from'])
        if form.cleaned_data.get('date_to'):
            matches = matches.filter(date__lte=form.cleaned_data['date_to'])

    return render(request, 'match_list.html', {'form': form, 'matches': matches})

@login_required
def create_match(request):
    if request.method == 'POST':
        form = MatchForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('match_list')
    else:
        form = MatchForm()
    return render(request, 'create_match.html', {'form': form})

@login_required
def team_list(request):
    teams = Team.objects.filter(coach=request.user)
    return render(request, 'team_list.html', {'teams': teams})

def team_detail(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    players = team.players.all()

    return render(request, 'team_detail.html', {'team': team, 'players': players})



from .forms import ContactForm
from .models import ContactMessage


def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Получаем данные из формы
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            
            # Сохраняем данные в базу
            ContactMessage.objects.create(
                name=name,
                email=email,
                message=message,
            )
            
            # Можно добавить сообщение об успешной отправке
            return render(request, 'contact_success.html')
    else:
        form = ContactForm()

    return render(request, 'contact.html', {'form': form})