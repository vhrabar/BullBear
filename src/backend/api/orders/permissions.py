from rest_framework.permissions import BasePermission


class IsOrderOwner(BasePermission):
    """
    Allows access only to objects owned by the authenticated user's profile.
    """

    def has_object_permission(self, request, view, obj):
        profile = getattr(request.user, "profile", None)
        return profile is not None and obj.user_id == profile.id


class IsServiceExecutor(BasePermission):
    """
    Allow only executor service to access
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff
                    and request.user.is_superuser and request.user.username == "executor")
