from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            # Try to find user by email (for frontend)
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            try:
                # Fall back to username (for admin)
                user = UserModel.objects.get(username=username)
            except UserModel.DoesNotExist:
                return None
                
        if user.check_password(password):
            return user
        return None