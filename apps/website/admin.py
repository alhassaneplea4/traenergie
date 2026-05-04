from django.contrib import admin
from .models import Service, Project, TeamMember, Testimonial, ContactMessage, CompanyInfo


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ["title", "icon", "color", "order", "is_active"]
    list_editable = ["order", "is_active"]
    list_filter = ["is_active"]


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "client", "completion_date", "is_featured"]
    list_filter = ["category", "is_featured"]
    search_fields = ["title", "client"]


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ["name", "role", "order", "is_active"]
    list_editable = ["order", "is_active"]


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ["author_name", "author_company", "rating", "is_active", "created_at"]
    list_filter = ["rating", "is_active"]


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "subject", "status", "created_at"]
    list_filter = ["status"]
    readonly_fields = ["name", "email", "phone", "subject", "message", "created_at"]


@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not CompanyInfo.objects.exists()
