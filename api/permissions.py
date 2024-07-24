from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_staff

class IsSeller(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_seller

class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return request.user and not request.user.is_seller

class IsAuthenticatedOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return request.user and request.user.is_authenticated
