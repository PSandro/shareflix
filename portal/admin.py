from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Account, GiftCard, Claim

class CustomUserAdmin(UserAdmin):
    fieldsets = (
        *UserAdmin.fieldsets,
        (
            'Netflix Account',
            {
                'fields': (
                    'account',
                ),
            },
        ),
    )

admin.site.register(Account)
admin.site.register(GiftCard)
admin.site.register(Claim)
admin.site.register(User, CustomUserAdmin)
