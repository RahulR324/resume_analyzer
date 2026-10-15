from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Profile

User = get_user_model()


class StyledFormMixin:
    def _style(self):
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs.setdefault("rows", 8)
                css = "input input--area"
            else:
                css = "input"
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing} {css}".strip()
            field.widget.attrs.setdefault("placeholder", field.label or name.replace("_", " ").title())


class RegisterForm(StyledFormMixin, UserCreationForm):
    full_name = forms.CharField(max_length=160)
    email = forms.EmailField()
    field_order = ("full_name", "username", "email", "password1", "password2")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style()

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["full_name"].split(" ")[0][:30]
        if commit:
            user.save()
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.full_name = self.cleaned_data["full_name"]
            profile.save(update_fields=["full_name"])
        return user


class LoginForm(StyledFormMixin, AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style()


class ProfileForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("full_name", "headline", "target_role", "location")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style()
