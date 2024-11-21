from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Course, Profile, Lesson, Answer, Team, Match
from django.forms.widgets import DateTimeInput

class CustomUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'role', 'password1', 'password2')

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone_number', 'bio', 'profile_picture']
    
    # Виджет для phone_number (можно задать свой виджет, если нужно)
    phone_number = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Введите номер телефона'}))
    
    # Виджет для bio (текстовое поле для ввода био)
    bio = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Напишите ваше био', 'rows': 3, 'cols': 30}))
    
    # Виджет для profile_picture (отображение изображения)
    profile_picture = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={'multiple': False, 'accept': 'image/*'})
    )
class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'teacher']

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'description', 'task']
        labels = {
            'title': 'Название урока',
            'description': 'Описание урока',
            'task': 'Задание',
        }
        
class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['content']
        labels = {
            'content': 'Ваш ответ',
        }

class GradeForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['grade']
        labels = {
            'grade': 'Оценка',
        }

class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'sport_type', 'players']

    players = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(role='student'),  # Фильтруем только пользователей с ролью 'student'
        widget=forms.CheckboxSelectMultiple
    )

class MatchForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ['team_1', 'team_2', 'date', 'result', 'location']

    date = forms.DateTimeField(
        widget=DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M'],  # Формат для поля datetime-local
    )


class MatchFilterForm(forms.Form):
    team_1 = forms.ModelChoiceField(
        queryset=Team.objects.all(),
        required=False,
        empty_label='Выберите команду 1',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    team_2 = forms.ModelChoiceField(
        queryset=Team.objects.all(),
        required=False,
        empty_label='Выберите команду 2',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    result = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Результат матча'})
    )
    date_from = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M']
    )
    date_to = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M']
    )

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, label='Ваше имя')
    email = forms.EmailField(label='Ваш Email')
    message = forms.CharField(widget=forms.Textarea, label='Сообщение')


