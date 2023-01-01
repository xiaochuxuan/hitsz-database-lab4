from crispy_forms.layout import HTML, ButtonHolder, Div, Field, Layout, Submit, Row, Column
from django import forms
from django.forms import widgets
from crispy_forms.helper import FormHelper
from management.models import Laboratory, LaboratoryReserveCase, Software, LaboratorySoftware
import datetime

# # 可用时间段
# free_time_list = [
#     '未被预约时间段',
#     '8:00-10:00',
#     '10:00-12:00',
#     '12:00-14:00',
#     '14:00-16:00',
#     '16:00-18:00',
#     '18:00-20:00',
#     '20:00-22:00',
# ]

# # 根据数据库记录判断当天可用实验室
# def get_free_time_list(date, laboratory_name):
#     laboratory_id = Laboratory.objects.get(laboratory_name=laboratory_name)
#     laboratory_reserve_case = LaboratoryReserveCase.objects.filter(laboratory_id=laboratory_id,
#                                                                    lr_date=date).first()
#
#     if laboratory_reserve_case:
#         time_list = list()
#         time_list.append(free_time_list[0])
#
#         bit = 0b1111111 - laboratory_reserve_case.lr_time
#         for i in range(1, len(free_time_list)):
#             if bit & (1 << (i - 1)):
#                 time_list.append(free_time_list[i])
#         return time_list
#     else:
#         return free_time_list

reserve_time = [
    (0b0, '8:00'),
    (0b1, '10:00'),
    (0b11, '12:00'),
    (0b111, '14:00'),
    (0b1111, '16:00'),
    (0b11111, '18:00'),
    (0b111111, '20:00'),
    (0b1111111, '22:00'),
]


class ReserveForm(forms.Form):
    laboratory_name = forms.CharField(
        label='laboratory_name',
        required=True,
        min_length=1,
        max_length=12,
        widget=widgets.Select()
    )

    reserve_date = forms.DateField(     # 预约日期
        label='reserve_date',
        required=True,
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    # free_time = forms.CharField(
    #     label='free',
    #     widget=widgets.Select()
    # )

    begin_time = forms.ChoiceField(
        label='begin_time',
        choices=reserve_time,
        required=True,
    )

    end_time = forms.ChoiceField(
        label='end_time',
        choices=reserve_time,
        required=True,
    )

    purpose = forms.CharField(
        label="用途",
        widget=forms.Textarea,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        laboratory_name = kwargs.pop('laboratory_name', None)
        super().__init__(*args, **kwargs)

        self.fields['laboratory_name'].widget.choices = list(Laboratory.objects.values_list('laboratory_name', 'laboratory_name'))
        self.initial['laboratory_name'] = laboratory_name

        self.helper = FormHelper()
        self.helper.form_id = "id-reserveForm"
        self.helper.form_method = 'post'
        self.helper.form_action = '/management/reserve_view/' + laboratory_name + '/'
        self.helper.form_show_labels = False

        self.helper.layout = Layout(
            Field('laboratory_name', css_class="form-control item",
                  placeholder='laboratory_name'),
            Field('reserve_date', css_class="form-control item",
                  placeholder='reserve_date'),
            Row(
                Column(
                    Field('begin_time', css_class="form-control item",
                          placeholder='begin_time'),
                    css_class="form-group col-md-6 mb-0",
                ),
                Column(
                    Field('end_time', css_class="form-control item",
                          placeholder='end_time'),
                    css_class="form-group col-md-6 mb-0",
                ),
            ),
            Field('purpose', css_class="form-control text",
                  placeholder='purpose, can be null'),
            ButtonHolder(
                Submit('submit', 'Reserve', css_class="btn btn-block submit")
            )
        )

    # 对字段进行检验
    def clean(self):
        date = self.cleaned_data['reserve_date']
        begin_time = self.cleaned_data['begin_time']
        end_time = self.cleaned_data['end_time']
        laboratory_name = self.cleaned_data['laboratory_name']

        # 检验实验室输入是否合法
        laboratory = Laboratory.objects.filter(laboratory_name=laboratory_name)

        if laboratory is None:
            raise forms.ValidationError('Please input a correct laboratory', code='invalid')
        # 检验日期是否正确
        if date <= datetime.date.today():
            raise forms.ValidationError('Please choose date after now', code='invalid')
        # 检验时间是否正确
        elif int(end_time) <= int(begin_time):
            raise forms.ValidationError('The end_time must be greater than begin_time', code='invalid')

        # 检验实验是否已预约
        reserve_duration = int(end_time) - int(begin_time)
        laboratory_id = laboratory.first().laboratory_id
        laboratory_reserve_case = LaboratoryReserveCase.objects.filter(laboratory_id=laboratory_id, lr_date=date).first()
        # > 0 说明预约时间和占用时间之间存在交集，无法预约
        if laboratory_reserve_case and (reserve_duration & laboratory_reserve_case.lr_time) > 0:
            raise forms.ValidationError('您所选的部分时间段已被预约', code='invalid')

        return self.cleaned_data


class AddSoftwareForm(forms.Form):
    software_name = forms.CharField(
        label='software_name',
        required=True,
        max_length=14,
    )

    software_category = forms.CharField(
        label='software_category',
        required=False,
        max_length=12,
    )

    version = forms.CharField(
        label='version',
        max_length=14,
        required=True,
    )

    developer = forms.CharField(
        label='developer',
        max_length=14,
        required=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_id = "id-addSoftwareForm"
        self.helper.form_method = 'post'
        self.helper.form_action = 'add_software'
        self.helper.form_show_labels = False

        self.helper.layout = Layout(
            Field('software_name', css_class="form-control item",
                  placeholder='software_name'),
            Field('software_category', css_class="form-control item",
                  placeholder='software_category, can be null'),
            Field('version', css_class="form-control item",
                  placeholder='version'),
            Field('developer', css_class="form-control item",
                  placeholder='developer'),
            ButtonHolder(
                Submit('submit', 'Add software', css_class="btn btn-block submit")
            )
        )

    def clean_software_name(self):
        value = self.cleaned_data.get('software_name')
        if Software.objects.filter(software_name=value):
            raise forms.ValidationError('the software already exists', code='invalid')
        else:
            return value

class UpdateConfForm(forms.Form):
    cpu = forms.CharField(
        label='cpu',
        required=True,
        max_length=14,
    )

    memory = forms.DecimalField(
        label='memory',
        required=True,
    )

    gpu = forms.CharField(
        label='gpu',
        required=True,
        max_length=14,
    )

    mainboard = forms.CharField(
        label='mainboard',
        required=True,
        max_length=14
    )

    def __init__(self, *args, **kwargs):
        laboratory_name = kwargs.pop('laboratory_name', None)
        super().__init__(*args, **kwargs)

        conf = Laboratory.objects.get(laboratory_name=laboratory_name).conf
        self.initial['cpu'] = conf.cpu
        self.initial['memory'] = conf.memory
        self.initial['gpu'] = conf.gpu
        self.initial['mainboard'] = conf.mainboard

        self.helper = FormHelper()
        self.helper.form_id = "id-update_conf"
        self.helper.form_method = 'post'
        self.helper.form_action = '/management/update_conf/' + laboratory_name + '/'
        self.helper.form_show_labels = False

        self.helper.layout = Layout(
            Field('cpu', css_class="form-control item",
                  placeholder='cpu'),
            Field('memory', css_class="form-control item",
                  placeholder='memory'),
            Field('gpu', css_class="form-control item",
                  placeholder='gpu'),
            Field('mainboard', css_class="form-control item",
                  placeholder='mainboard'),
            ButtonHolder(
                Submit('submit', 'update', css_class="btn btn-block submit")
            )
        )