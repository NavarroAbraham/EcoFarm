from __future__ import annotations

from .models import UserProfile

ROLE_ADMIN = 'admin'
ROLE_BUYER = UserProfile.ROLE_BUYER
ROLE_PROVIDER = UserProfile.ROLE_PROVIDER


def get_user_role(user) -> str | None:
    if user is None or user.is_anonymous:
        return None
    if getattr(user, 'is_staff', False) or getattr(user, 'is_superuser', False):
        return ROLE_ADMIN
    profile, _ = UserProfile.objects.get_or_create(
        user=user,
        defaults={'role': UserProfile.ROLE_BUYER},
    )
    return profile.role


def is_provider(user) -> bool:
    return get_user_role(user) == ROLE_PROVIDER


def is_buyer(user) -> bool:
    return get_user_role(user) == ROLE_BUYER
