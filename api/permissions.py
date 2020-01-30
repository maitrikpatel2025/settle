from django.contrib.auth.models import Group
from rest_framework import permissions


def is_in_group(user, group_name):
    """
    Takes a user and a group name, and returns `True` if the user is in that group.
    """
    try:
        return Group.objects.get(name=group_name).user_set.filter(id=user.id).exists()
    except Group.DoesNotExist:
        return None


class HasGroupPermission(permissions.BasePermission):
    """
    Ensure user is in required groups.
    """

    def has_permission(self, request, view):
        # Get a mapping of methods -> required group.
        required_groups_mapping = getattr(view, "required_groups", {})

        # Determine the required groups for this particular request method.
        required_groups = required_groups_mapping.get(request.method, [])

        is_user_in_required_groups = [
            is_in_group(request.user, group_name)
            if group_name != "__all__"  else True 
            for group_name in required_groups
        ]

        # Return True if the user has all the required groups or is staff.
        return (
            all(is_user_in_required_groups) or 
            (request.user and request.user.is_staff)
        )


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the property.
        return obj.owner == request.user


class IsAllowedUser(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_permission(self, request, view):
        if request.method in ['POST']:
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj == request.user


class BelongsToPropertyOwnedByAuthenticatedUser(permissions.BasePermission):
    """
    Custom permission to only allow owners of an property to edit it's pictures.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the property.
        return obj.property.owner == request.user