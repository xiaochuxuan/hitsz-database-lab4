from crispy_forms.layout import HTML, ButtonHolder, Div, Field, Layout, Submit, Row, Column
from django import forms
from django.forms.widgets import PasswordInput
from crispy_forms.helper import FormHelper

from management.models import User, Teacher

class RegistForm(forms.Form):

    user_name = forms.CharField(
        label='user_name',
        required=True,
        min_length=1,
        max_length=16,
    )

    password = forms.CharField(
        label='password',
        widget=forms.PasswordInput,
        required=True,
        min_length=1,
        max_length=16,
    )

    pwd_confirm = forms.CharField(
        label='password_confirm',
        widget=PasswordInput,
        required=True,
        min_length=1,
        max_length=16,
    )

    user_phone = forms.CharField(
        label='user_phone',
        required=True,
        min_length=8,
        max_length=14,
    )

    user_sex = forms.ChoiceField(
        choices=((1, "男"), (0, "女")),
    )

    teacher_id = forms.CharField(
        label='teacher_id',
        required=True,
        min_length=1,
        max_length=14,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_id = "id-registForm"
        self.helper.form_method = 'post'
        self.helper.form_action = 'regist'
        self.helper.form_show_labels = False

        self.helper.layout = Layout(
            Div(
                HTML('<span><i class="icon icon-user"></i></span>'),
                css_class="form-icon"
            ),

            Field('user_name', css_class="form-control item",
                  placeholder='user_name'),
            Field('teacher_id', css_class="form-control item",
                  placeholder='teacher_id'),
            Row(
                Column(
                    Field('user_sex', css_class="form-control item",
                          placeholder='user_sex'),
                    css_class="form-group col-md-4 mb-0",
                ),
                Column(
                    Field('user_phone', css_class="form-control item",
                          placeholder='user_phone'),
                    css_class="form-group col-md-8 mb-0",
                )
            ),
            Field('password', css_class="form-control item",
                  placeholder='password'),
            Field('pwd_confirm', css_class="form-control item",
                  placeholder='password confirm'),

            ButtonHolder(
                Submit('submit', 'Regist', css_class="btn btn-block create-user")
            )
        )

    def clean_user_name(self):
        value = self.cleaned_data['user_name']
        if User.objects.filter(user_name=value):    # 该用户名已被使用
            raise forms.ValidationError('User_name has been registed', code='invalid')
        else:
            return value

    def clean_teacher_id(self):
        value = self.cleaned_data['teacher_id']
        if Teacher.objects.filter(t_id=value):
            return value
        else:
            raise forms.ValidationError('Teacher_id does not exist', code='invalid')

    def clean_password(self):
        value = self.cleaned_data['password']
        if value.isdigit():     # 密码全为数字
            raise forms.ValidationError('Password must have characters', code='invalid')
        else:
            return value

    def clean_user_phone(self):
        value = self.cleaned_data['user_phone']
        if User.objects.filter(user_phone=value):   # 该手机号已被使用
            raise forms.ValidationError('Phone has been used', code='invalid')

        if not value.isdigit():
            raise forms.ValidationError('illegal character', code='invalid')
        else:
            return value

    def clean_pwd_confirm(self):
        value = self.cleaned_data['pwd_confirm']

        try:
            target = self.cleaned_data['password']
        except Exception as e:
            raise forms.ValidationError('Password is valid', code='invalid')
        else:
            if value != target or target is None:   # 前后输入密码不同
                raise forms.ValidationError('Password are not same', code='invalid')
            else:
                return value


class LoginForm(forms.Form):
    user_name = forms.CharField(
        label='user_name',
        required=True,
        min_length=1,
        max_length=14,
    )

    password = forms.CharField(
        label='password',
        widget=forms.PasswordInput,
        required=True,
        min_length=1,
        max_length=20,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-loginForm'
        self.helper.form_method = 'post'
        self.helper.form_action = 'login'
        self.helper.form_show_labels = False

        self.helper.layout = Layout(
            Div(
                HTML('<span><i class="icon icon-user"></i></span>'),
                css_class="form-icon"
            ),

            Field('user_name', css_class="form-control item",
                  placeholder="user_name/user_phone"),
            Field('password', css_class="form-control item",
                  placeholder="password"),

            ButtonHolder(
                Submit('submit', 'Login', css_class="btn btn-block create-user")
            ),
        )

    def clean_user_name(self):
        value = self.cleaned_data['user_name']
        if not User.objects.filter(user_name=value):
            raise forms.ValidationError('No such user_name or phone!', code='invalid')
        else:
            return value
