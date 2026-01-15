from rest_framework.permissions import BasePermission


class IsOrderOwner(BasePermission):
    """
    Allows access only to objects owned by the authenticated user's profile.
    """

    def has_object_permission(self, request, view, obj):
        profile = getattr(request.user, "userprofile", None)
        return profile is not None and obj.user_id == profile.id
