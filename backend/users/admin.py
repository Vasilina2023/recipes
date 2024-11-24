from django.contrib import admin
from django.contrib.auth.models import Group

from users.models import Subscription, User

admin.site.empty_value_display = 'Не задано'


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'username', 'first_name', 'last_name', 'email'
    )
    search_fields = ('email', 'username')
    list_filter = ('username',)


admin.site.register(User, UserAdmin)
admin.site.register(Subscription)
admin.site.unregister(Group)
