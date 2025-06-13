from rest_framework import permissions


class NotFirstLogin(permissions.BasePermission):
    message = "You must change your password before accessing this resource."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and not request.user.is_first_login)

class IsAdminUser(permissions.BasePermission):
    """
    Allows access only to super_admin users.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.user_type == 'super_admin')

class IsManagerUser(permissions.BasePermission):
    """
    Allows access only to manager users.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'manager')

class IsCashierUser(permissions.BasePermission):
    """
    Allows access only to cashier users.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'cashier')