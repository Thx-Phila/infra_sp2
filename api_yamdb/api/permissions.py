from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsOwners(BasePermission):

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            obj == request.user
        )


class IsAdminOrReadOnly(BasePermission):
    """Разрешение на уровне админ."""

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or (request.user.is_authenticated
                and (request.user.is_admin()
                     or request.user.is_superuser)
                )
        )


class IsAdmin(BasePermission):
    """Разрешение на уровне админ."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and (request.user.is_admin()
                 or request.user.is_superuser)
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_authenticated
            and (request.user.is_admin()
                 or request.user.is_superuser)
        )


class AuthorAndStaffOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or (
                request.user.is_authenticated
                and (
                    obj.author == request.user
                    or request.user.is_moderator()
                    or request.user.is_admin()
                    or request.user.is_superuser
                )
            )
        )
