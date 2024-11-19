from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.conf import settings

class User(AbstractUser):
    TEACHER = 'teacher'
    STUDENT = 'student'
    ROLE_CHOICES = [
        (TEACHER, 'Teacher'),
        (STUDENT, 'Student'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=STUDENT)
    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_set',
        blank=True
    )
    teams = models.ManyToManyField('Team', related_name='members', blank=True)


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    
    def __str__(self):
        return f"Profile of {self.user.username}"

    
class Lesson(models.Model):
    course = models.ForeignKey('Course', related_name='lessons', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    task = models.TextField(null=True, blank=True, verbose_name="Задание")

    def __str__(self):
        return self.title
    

class Course(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    students = models.ManyToManyField(User, related_name="student_courses")

    def __str__(self):
        return self.title
    
class Answer(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answers')
    lesson = models.ForeignKey('Lesson', on_delete=models.CASCADE, related_name='answers')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    grade = models.IntegerField(null=True, blank=True)  # Добавляем поле для оценки

    def __str__(self):
        return f"Answer by {self.student.username} for {self.lesson.title}"

class Team(models.Model):
    name = models.CharField(max_length=100)
    sport_type = models.CharField(max_length=100)
    coach = models.ForeignKey(User, related_name='coached_teams', on_delete=models.CASCADE)
    players = models.ManyToManyField(User, related_name='teams_playing_in', blank=True)

    def __str__(self):
        return f"{self.name} ({self.sport_type})"   

class Match(models.Model):
    team_1 = models.ForeignKey(Team, related_name='team_1_matches', on_delete=models.CASCADE)
    team_2 = models.ForeignKey(Team, related_name='team_2_matches', on_delete=models.CASCADE)
    date = models.DateTimeField()
    result = models.CharField(max_length=100)
    location = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.team_1.name} vs {self.team_2.name} on {self.date}"
