import datetime
from django.contrib import messages
from django.shortcuts import redirect, render, reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .forms import ReserveForm, AddSoftwareForm, UpdateConfForm
from .models import Laboratory, User, LaboratorySoftware, ReservationRecord, \
                    Manager, LaboratoryReserveCase, Software

# 时间段
reserve_time = [
    '8:00', '10:00', '12:00', '14:00', '16:00', '18:00', '20:00', '22:00'
]

# 占用时间段
occupy_duration = [
    '8:00-10:00', '10:00-12:00', '12:00-14:00', '14:00-16:00',
    '16:00-18:00', '18:00-20:00', '20:00-22:00'
]

# 定义一个预约表类用于展示
class Reserve_list:
    def __init__(self, record_id, laboratory_name, reserve_date,
                 reserve_time, post_time, purpose, if_success):
        self.record_id = record_id
        self.laboratory_name = laboratory_name
        self.reserve_date = reserve_date
        self.reserve_time = reserve_time
        self.post_time = post_time
        self.purpose = purpose
        self.if_success = if_success

# 定义一个实验室类用于展示
class laboratory_display:
    def __init__(self, laboratory_id, laboratory_name, area, location, comp_sets):
        self.laboratory_id = laboratory_id
        self.laboratory_name = laboratory_name
        self.area = area
        self.location = location
        self.comp_sets = comp_sets
        self.software_list = list()
        self.software_list_add = list()

    def __str__(self):
        t_str = ""
        for software in self.software_list:
            t_str = t_str + " " + software
        return "实验室名称: %s\n" \
               "可用软件列表: %s\n" % (self.laboratory_name, t_str)

class Laboratory_occupy:
    def __init__(self, date, time):
        self.date = date
        self.time = time

# 获取待展示的实验室列表
def get_laboratory_dsp_list(laboratory_list_tmp):
    laboratory_list = list()

    # 统计所有软件列表
    for laboratory in laboratory_list_tmp:
        laboratory_dsp = laboratory_display(laboratory_id=laboratory.laboratory_id,
                                            laboratory_name=laboratory.laboratory_name,
                                            area=laboratory.area, location=laboratory.location,
                                            comp_sets=laboratory.comp_sets)
        software_list = LaboratorySoftware.objects.filter(laboratory_id=laboratory.laboratory_id)

        laboratory_dsp.laboratory_name = laboratory.laboratory_name
        for software in software_list:
            laboratory_dsp.software_list.append(software.software_name)

        laboratory_list.append(laboratory_dsp)

    return laboratory_list

# 获取待展示的预约表
def get_reserve_list(_list):
    rs_list = list()

    for record in _list:
        # 获取预约的时间段
        time_bit = record.reserve_time
        flag = False
        i = begin = end = 0
        while 1:
            if not flag and time_bit & 1:
                begin = i
                flag = True
            elif flag and time_bit & 1 == 0:
                end = i
                break
            i = i + 1
            time_bit = time_bit >> 1

        duration = reserve_time[begin] + " - " + reserve_time[end]
        rs = Reserve_list(record.record_id, record.laboratory_name, record.reserve_date,
                          duration,
                          record.post_time, record.event, record.if_success)
        rs_list.append(rs)

    return rs_list


# 设置分页功能
def set_page(page_list, page, num_per_page):
    # 实现分页
    paginator = Paginator(page_list, num_per_page)

    try:
        page_list = paginator.page(page)
    except PageNotAnInteger:
        # 用户请求的页码号不是整数，显示第一页
        page_list = paginator.page(1)
    except EmptyPage:
        # 如果用户请求的页码号超过了最大页码号，显示最后一页
        page_list = paginator.page(paginator.num_pages)

    return page_list


def index(request):
    user_name = request.session.get('user_name')
    user_character = request.session.get('user_character')
    print(user_character)
    if user_name is None:
        return render(request, 'management/index.html')
    else:
        return render(request, 'management/index.html',
                      context={
                          'user_name': user_name,
                          'user_character': user_character,
                      })


# 视图：展示实验室
def laboratory_view(request):
    laboratory_list_tmp = Laboratory.objects.all()
    laboratory_list = get_laboratory_dsp_list(laboratory_list_tmp)

    # 实现分页
    page = request.GET.get('page')
    laboratory_list = set_page(laboratory_list, page, 2)

    user_name = request.session.get('user_name')
    user_character = request.session.get('user_character')
    if user_name is None:
        return render(request, 'management/lab_list.html',
                      context={
                          'post_list': laboratory_list
                      })
    else:
        return render(request, 'management/lab_list.html',
                      context={
                          'post_list': laboratory_list,
                          'user_name': user_name,
                          'user_character': user_character,
                      })

# 视图: 预约
def reserve_view(request, laboratory_name):
    # # 接收到数据
    if request.method == 'POST':
        reserve_form = ReserveForm(request.POST, laboratory_name=laboratory_name)

        if reserve_form.is_valid():
            laboratory_name = reserve_form.cleaned_data['laboratory_name']
            reserve_date = reserve_form.cleaned_data['reserve_date']
            reserve_time = int(reserve_form.cleaned_data['end_time']) - int(reserve_form.cleaned_data['begin_time'])
            purpose = reserve_form.cleaned_data['purpose']

            # 从session中获取用户id
            user_id = request.session['user_id']
            # 生成记录id
            record_id = 0
            for record in ReservationRecord.objects.all():
                if int(record.record_id) > record_id:
                    record_id = int(record.record_id)
            record_id = record_id + 1
            # 审核情况置为0, 即未通过
            if_success = 0
            # 获取实验室对应管理员
            if Laboratory.objects.filter(laboratory_name=laboratory_name):
                manager_id = Laboratory.objects.get(laboratory_name=laboratory_name).manager_id
            else:
                messages.warning(request, 'Invaild Laboratory')
                return render(request, 'Share/form.html', {
                    'form': reserve_form, 'title': 'Login'
                })

            # 将记录保存在数据库中
            record = ReservationRecord(record_id=str(record_id), user_id=user_id, manager_id=manager_id,
                                       laboratory_name=laboratory_name, reserve_date=reserve_date,
                                       reserve_time=reserve_time, post_time=datetime.datetime.now(), event=purpose, if_success=if_success)
            record.save()

            return redirect(reverse('laboratory_list'))
        else:
            return render(request, 'Share/form.html',
                          context={'title': "预约", 'form': reserve_form})

    reserve_form = ReserveForm(laboratory_name=laboratory_name)
    return render(request, 'Share/form.html',
                  context={
                      'title': "预约",
                      'form': reserve_form,
                  })


# 视图：管理实验室
def manage_view(request):
    # 获取对应管理员id
    user_id = request.session.get('user_id')
    manager_id = Manager.objects.get(t_id=User.objects.get(user_id=user_id).t_id)
    # 查找对应管理的实验室
    laboratory_list_tmp = Laboratory.objects.filter(manager_id=manager_id)
    laboratory_list = get_laboratory_dsp_list(laboratory_list_tmp)

    # 加入可添加软件
    software_list = list(Software.objects.all().values_list('software_name', flat=True))
    print(software_list)
    for laboratory in laboratory_list:
        for software in software_list:
            if software not in laboratory.software_list:
                laboratory.software_list_add.append(software)

    page = request.GET.get('page')
    laboratory_list = set_page(laboratory_list, page, 2)

    user_name = request.session.get('user_name')
    user_character = request.session.get('user_character')
    if user_name is None:
        return render(request, 'management/manage_laboratory.html',
                      context={
                          'post_list': laboratory_list
                      })
    else:
        return render(request, 'management/manage_laboratory.html',
                      context={
                          'post_list': laboratory_list,
                          'user_name': user_name,
                          'user_character': user_character,
                      })


# 视图：添加软件
def add_software(request):
    if request.method == 'POST':
        add_software_form = AddSoftwareForm(request.POST)

        if add_software_form.is_valid():
            software_name = add_software_form.cleaned_data['software_name']
            software_category = add_software_form.cleaned_data['software_category']
            version = add_software_form.cleaned_data['version']
            developer = add_software_form.cleaned_data['developer']

            software = Software(software_name=software_name, software_category=software_category,
                                version=version, developer=developer)
            software.save()

            user_name = request.session.get('user_name')
            user_character = request.session.get('user_character')
            if user_name is None:
                return render(request, 'management/index.html')
            else:
                return render(request, 'management/index.html',
                              context={
                                  'user_name': user_name,
                                  'user_character': user_character,
                              })
        else:
            return render(request, 'Share/form.html',
                          context={'title': "添加软件到软件列表", 'form': add_software_form})

    add_software_form = AddSoftwareForm()
    return render(request, 'Share/form.html',
                  context={'title': "添加软件到软件列表", 'form': add_software_form})


# 视图：为相应实验室电脑添加软件
def add_software_laboratory(request, laboratory_name, software_name):
    laboratory_software = LaboratorySoftware(
        laboratory_id=Laboratory.objects.get(laboratory_name=laboratory_name).laboratory_id,
        software_name=software_name
    )
    laboratory_software.save()

    return redirect(reverse('manage_laboratory'))


# 视图：修改电脑配置
def update_conf(request, laboratory_name):
    # todo
    if request.method == 'POST':
        update_conf_form = UpdateConfForm(request.POST, laboratory_name=laboratory_name)

        if update_conf_form.is_valid():
            cpu = update_conf_form.cleaned_data['cpu']
            memory = update_conf_form.cleaned_data['memory']
            gpu = update_conf_form.cleaned_data['gpu']
            mainboard = update_conf_form.cleaned_data['mainboard']

            conf = Laboratory.objects.get(laboratory_name=laboratory_name).conf
            conf.cpu = cpu
            conf.memory = memory
            conf.gpu = gpu
            conf.mainboard = mainboard
            conf.save()

            return redirect(reverse('manage_laboratory'))
        else:
            return render(request, 'Share/form.html',
                          context={'title': "修改实验室电脑配置", 'form': update_conf_form})

    update_conf_form = UpdateConfForm(laboratory_name=laboratory_name)
    return render(request, 'Share/form.html',
                  context={'title': "修改实验室电脑配置", 'form': update_conf_form})


# 视图：管理预约
def reservation_manage_view(request):
    # 从session获取
    user_id = request.session.get('user_id')
    user_name = request.session.get('user_name')
    user_character = request.session.get('user_character')

    # 获取管理实验室对应的预约记录(未审批)
    # 获取的记录申请时间在当前时间之后
    # todo: 优化，在当前时间之后
    manager_id = Manager.objects.get(t_id=User.objects.get(user_id=user_id).t_id)
    date = datetime.date.today()

    record_list = ReservationRecord.objects.filter(manager_id=manager_id,
                                                   reserve_date__gte=date, if_success=0).order_by('-post_time')
    manage_record_list = get_reserve_list(record_list)
    #分页
    page = request.GET.get('page')
    manage_record_list = set_page(manage_record_list, page, 4)

    return render(request, 'management/reserve_manage.html',
                  context={
                      'post_list': manage_record_list,
                      'user_name': user_name,
                      'user_character': user_character,
                  })


# 视图：通过预约申请
def pass_reservation(request, record_id):
    record = ReservationRecord.objects.get(record_id=record_id)

    # 同时更新该天的实验室预约情况
    laboratory_name = record.laboratory_name
    lr_date = record.reserve_date
    laboratory_id = Laboratory.objects.get(laboratory_name=laboratory_name).laboratory_id
    # 若还未创建记录则先创建
    if not LaboratoryReserveCase.objects.filter(laboratory_id=laboratory_id, lr_date=lr_date):
        # 创建时lr_time每一位都为0，表示还未被占用
        lr = LaboratoryReserveCase(laboratory_id=laboratory_id, lr_date=lr_date, lr_time=0)
        lr.save()

    # 二进制表示时间段
    # 比如：0b000001 表示 8:30-10:15 0b000010 表示 10:30-12:15
    # 将预约后的位置为1
    laboratory_reserve_case = LaboratoryReserveCase.objects.get(laboratory_id=laboratory_id, lr_date=lr_date)

    # todo, 待优化
    if laboratory_reserve_case.lr_time & record.reserve_time != 0:
        return redirect(reverse('reservation_manage'))

    laboratory_reserve_case.lr_time = (laboratory_reserve_case.lr_time | record.reserve_time)
    laboratory_reserve_case.save()

    # 将审核通过标志置为真
    record.if_success = 1
    record.save()

    return redirect(reverse('reservation_manage'))


# 视图：驳回申请
def reject_reservation(request):
    # todo
    return None


# 视图：查看预约申请
def reservation_query_view(request):
    # 从session获取
    user_id = request.session.get('user_id')
    user_name = request.session.get('user_name')
    user_character = request.session.get('user_character')

    if user_name is not None:
        # 在预约表中查找
        reservation_list = ReservationRecord.objects.filter(user_id=user_id).order_by('-post_time')

        rs_list = get_reserve_list(reservation_list)

        page = request.GET.get('page')
        rs_list = set_page(rs_list, page, 10)

        return render(request, 'management/reserve_show.html',
                      context={
                          'post_list': rs_list,
                          'user_name': user_name,
                          'user_character': user_character,
                      })
    else:
        return render(request, 'management/reserve_show.html')


# 视图：删除预约
def delete_reservation(request, record_id):
    print("要删除的记录id: " + str(record_id))

    record = ReservationRecord.objects.get(record_id=record_id)
    record.delete()

    return redirect(reverse('reservation_query'))

# 视图：查看实验室使用情况
def laboratory_occupancy_view(request, laboratory_name):
    # 从占用表中获取
    laboratory_id = Laboratory.objects.get(laboratory_name=laboratory_name)
    occupancy_case_list_tmp = LaboratoryReserveCase.objects.filter(
        laboratory_id=laboratory_id, lr_date__gte=datetime.date.today()).order_by('-lr_date')

    occupancy_case_list = list()
    for occupancy_case in occupancy_case_list_tmp:
        for i in range(0, len(occupy_duration)):
            if occupancy_case.lr_time & (1 << i):
                laboratory_occupy = Laboratory_occupy(date=occupancy_case.lr_date,
                                                      time=occupy_duration[i])
                occupancy_case_list.append(laboratory_occupy)

    page = request.GET.get('page')
    occupancy_case_list = set_page(occupancy_case_list, page, 10)

    user_name = request.session.get('user_name')
    user_character = request.session.get('user_character')

    if user_name is None:
        return render(request, 'management/laboratory_occupancy.html',
                      context={
                          'laboratory_name': laboratory_name,
                          'post': occupancy_case_list
                      })

    return render(request, 'management/laboratory_occupancy.html',
                  context={
                      'user_name': user_name,
                      'user_character': user_character,
                      'laboratory_name': laboratory_name,
                      'post_list': occupancy_case_list
                  })


# 视图：个人信息
def info_view(request):
    user_name = request.session.get('user_name')
    user_character = request.session.get('user_character')

    if user_name is None:
        return render(request, 'management/info.html')

    user = User.objects.get(user_name=user_name)
    return render(request, 'management/info.html',
                  context={
                      'user': user,
                      'user_name': user_name,
                      'user_character': user_character
                  })
