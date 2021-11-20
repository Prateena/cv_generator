
from django.contrib.auth import get_user_model

User = get_user_model()

class SuperAdminRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        return self.handle_no_permission()

class FormControlMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })
