from django.contrib import admin
from .models import ContactMessage

@admin.register(ContactMessage)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'message', 'created_at')
    search_fields = ('name', 'email', 'message')
