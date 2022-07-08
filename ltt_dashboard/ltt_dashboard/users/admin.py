from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.contrib.auth.forms import UserCreationForm as DjangoUserCreationForm
from django.contrib.auth.forms import UserChangeForm as DjangoUserChangeForm

# Register your models here.
from ltt_dashboard.users.models import User


class MyUserCreationForm(DjangoUserCreationForm):
    class Meta:
        model = User
        fields = ('email', )


class MyUserChangeForm(DjangoUserChangeForm):
    class Meta:
        model = User
        fields = '__all__'


@admin.register(User)
class UserAdmin(AuthUserAdmin):
    model = User
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('full_name', 'image', 'is_verified')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser',
                                    'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined', )}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "user_name", "password1", "password2"),
            },
        ),
    )
    readonly_fields = ('date_joined', 'last_login', )
    form = MyUserChangeForm
    add_form = MyUserCreationForm
    list_display = ('email', 'user_name', 'is_active', 'is_staff', 'modified_at', )
    list_filter = ('is_superuser', 'is_active')
    list_editable = ('is_staff', 'is_active', )
    search_fields = ('full_name', 'email', 'user_name')
    ordering = ('-date_joined',)
    list_per_page = 10
