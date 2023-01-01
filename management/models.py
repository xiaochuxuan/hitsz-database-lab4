from django.db import models
# Create your models here.


class AcademicBuild(models.Model):
    build_id = models.CharField(primary_key=True, max_length=10)
    build_name = models.CharField(max_length=14)
    build_address = models.CharField(max_length=20)

    def __str__(self):
        return "build_id: %s\n" \
                "build_name: %s\n" \
                "build_address: %s\n" % (self.build_id,
                                         self.build_name,
                                         self.build_address)

    class Meta:
        managed = True
        db_table = 'academic_build'


class AvailableLaboratory(models.Model):
    id = models.CharField(primary_key=True, max_length=12)
    laboratory = models.ForeignKey('Laboratory', models.DO_NOTHING, blank=True, null=True)
    laboratory_name = models.CharField(max_length=12)
    avai_date = models.DateField()
    avai_time = models.CharField(max_length=20)

    def __str__(self):
        return "id: %s\n" \
               "laboratory_id: %s\n" \
               "laboratory_name: %s\n" \
               "avai_date: %s\n" \
               "avai_time: %s\n" % (self.id,
                                    self.laboratory_id,
                                    self.laboratory_name,
                                    self.avai_date,
                                    self.avai_time)

    class Meta:
        managed = True
        db_table = 'available_laboratory'


class CompConfiguration(models.Model):
    conf_id = models.CharField(primary_key=True, max_length=10)
    cpu = models.CharField(max_length=14)
    memory = models.IntegerField()
    gpu = models.CharField(max_length=14)
    mainboard = models.CharField(max_length=14)

    def __str__(self):
        return "conf_id: %s\n" \
               "cpu: %s\n" \
               "memory: %d\n" \
               "gpu: %s\n" \
               "mainboard: %s\n" % (self.conf_id,
                                    self.cpu,
                                    self.memory,
                                    self.gpu,
                                    self.mainboard)

    class Meta:
        managed = True
        db_table = 'comp_configuration'


class Course(models.Model):
    course_id = models.CharField(primary_key=True, max_length=10)
    course_name = models.CharField(max_length=14)
    course_hours = models.IntegerField()
    course_t = models.CharField(db_column='course_T', max_length=10)  # Field name made lowercase.
    course_depart = models.CharField(max_length=10)
    course_software = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return "course_id: %s\n" \
               "course_name: %s\n" \
               "course_hours: %d\n" \
               "course_t: %s\n" \
               "course_depart: %s\n" \
               "course_software: %s\n" % (self.course_id,
                                          self.course_name,
                                          self.course_hours,
                                          self.course_t,
                                          self.course_depart,
                                          self.course_software)

    class Meta:
        managed = True
        db_table = 'course'


class CourseSoftware(models.Model):
    software_name = models.CharField(primary_key=True, max_length=14)
    course = models.ForeignKey(Course, models.DO_NOTHING)

    def __str__(self):
        return "software_name: %s\n" \
                "course_id: %s\n" % (self.software_name,
                                     self.course_id)

    class Meta:
        managed = True
        db_table = 'course_software'
        unique_together = (('software_name', 'course'),)


class Laboratory(models.Model):
    laboratory_id = models.CharField(primary_key=True, max_length=10)
    manager = models.ForeignKey('Manager', models.DO_NOTHING, blank=True, null=True)
    conf = models.ForeignKey(CompConfiguration, models.DO_NOTHING, blank=True, null=True)
    build = models.ForeignKey(AcademicBuild, models.DO_NOTHING, blank=True, null=True)
    laboratory_name = models.CharField(unique=True, max_length=12)
    area = models.IntegerField()
    location = models.IntegerField()
    comp_sets = models.IntegerField()

    def __str__(self):
        return "laboratory_id: %s\n" \
               "manager_id: %s\n" \
               "conf_id: %s\n" \
               "build_id: %s\n" \
               "laboratory_name: %s\n" \
               "area: %d\n" \
               "location: %d\n" \
               "comp_sets: %d\n" % (self.laboratory_id,
                                    self.manager_id,
                                    self.conf_id,
                                    self.build_id,
                                    self.laboratory_name,
                                    self.area,
                                    self.location,
                                    self.comp_sets)

    class Meta:
        managed = True
        db_table = 'laboratory'


class LaboratorySoftware(models.Model):
    software_name = models.CharField(primary_key=True, max_length=14)
    laboratory = models.ForeignKey(Laboratory, models.DO_NOTHING)

    def __str__(self):
        return "software_name: %s\n" \
                "laboratory_id: %s\n" % (self.software_name, self.laboratory_id)

    class Meta:
        managed = True
        db_table = 'laboratory_software'
        unique_together = (('software_name', 'laboratory'),)


class Manager(models.Model):
    manager_id = models.CharField(primary_key=True, max_length=10)
    t_id = models.OneToOneField('Teacher', models.DO_NOTHING, db_column='T_id', blank=True, null=True)  # Field name made lowercase.
    manager_name = models.CharField(max_length=12)

    def __str__(self):
        return "manager_id: %s\n" \
                "t_id: %s\n" \
                "manager_name: %s\n" % (self.manager_id,
                                        self.t_id,
                                        self.manager_name)

    class Meta:
        managed = True
        db_table = 'manager'


class ReservationRecord(models.Model):
    record_id = models.CharField(primary_key=True, max_length=12)
    user = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True)
    manager = models.ForeignKey(Manager, models.DO_NOTHING, blank=True, null=True)
    laboratory_name = models.CharField(max_length=12)
    reserve_date = models.DateField()
    reserve_time = models.IntegerField()
    post_time = models.DateTimeField()
    event = models.TextField(blank=True, null=True)
    if_success = models.SmallIntegerField()

    def __str__(self):
        return "record_id: %s\n" \
                "user_id: %s\n" \
                "manager_id: %s\n" \
                "laboratory_name: %s\n" \
                "reserve_date: %s\n" \
                "reserve_time: %d\n" \
                "post_time: %s\n" \
                "event: %s\n" \
                "if_successful: %d\n" % (self.record_id,
                                         self.user_id,
                                         self.manager_id,
                                         self.laboratory_name,
                                         self.reserve_date,
                                         self.reserve_time,
                                         self.post_time,
                                         self.event,
                                         self.if_success)

    class Meta:
        managed = True
        db_table = 'reservation_record'


class Software(models.Model):
    software_name = models.CharField(primary_key=True, max_length=14)
    software_category = models.CharField(max_length=12, blank=True, null=True)
    version = models.CharField(max_length=14)
    developer = models.CharField(max_length=14)

    def __str__(self):
        return "software_name: %s\n" \
                "software_category: %s\n" \
                "version: %s\n" \
                "developer: %s\n" % (self.software_name,
                                     self.software_category,
                                     self.version,
                                     self.developer)

    class Meta:
        managed = True
        db_table = 'software'


class Teacher(models.Model):
    t_id = models.CharField(db_column='T_id', primary_key=True, max_length=10)  # Field name made lowercase.
    t_name = models.CharField(db_column='T_name', max_length=12)  # Field name made lowercase.
    t_sex = models.CharField(db_column='T_sex', max_length=1)  # Field name made lowercase.
    t_department = models.CharField(db_column='T_department', max_length=14)  # Field name made lowercase.

    def __str__(self):
        return "t_id: %s\n" \
                "t_name: %s\n" \
                "t_sex: %s\n" \
                "t_department: %s\n" % (self.t_id,
                                        self.t_name,
                                        self.t_sex,
                                        self.t_department)

    class Meta:
        managed = True
        db_table = 'teacher'


class TeacherCourse(models.Model):
    course_id = models.CharField(primary_key=True, max_length=10)
    t = models.ForeignKey(Teacher, models.DO_NOTHING, db_column='T_id')  # Field name made lowercase.
    laboratory_name = models.CharField(max_length=12, blank=True, null=True)
    course_hours = models.IntegerField()
    start_time = models.DateTimeField()

    def __str__(self):
        return "course_id: %s\n" \
                "t_id: %s\n" \
                "laboratory: %s\n" \
                "course_hours: %d\n" \
                "start_time: %s\n" %(self.course_id,
                                     self.t_id,
                                     self.laboratory_name,
                                     self.course_hours,
                                     self.start_time)

    class Meta:
        managed = True
        db_table = 'teacher_course'
        unique_together = (('course_id', 't'),)

class User(models.Model):
    user_id = models.CharField(primary_key=True, max_length=10)
    t = models.ForeignKey(Teacher, models.DO_NOTHING, db_column='T_id', blank=True, null=True)
    user_name = models.CharField(max_length=16)
    user_sex = models.SmallIntegerField()
    password = models.CharField(max_length=16)
    user_phone = models.DecimalField(max_digits=12, decimal_places=0)
    user_character = models.SmallIntegerField()

    def __str__(self):
        return "user_id: %s\n" \
               "t_id: %s\n" \
               "user_name: %s\n" \
               "user_sex: %d\n" \
               "password: %s\n" \
               "user_phone: %s\n" \
               "user_character: %d\n" %(self.user_id,
                                        self.t_id,
                                        self.user_name,
                                        self.user_sex,
                                        self.password,
                                        self.user_phone,
                                        self.user_character)

    class Meta:
        managed = True
        db_table = 'user'

class LaboratoryReserveCase(models.Model):
    lr_id = models.AutoField(primary_key=True)
    laboratory = models.ForeignKey(Laboratory, models.DO_NOTHING)
    lr_date = models.DateField()
    lr_time = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'laboratory_reserve_case'

    def __str__(self):
        return "lr_id: %d\n" \
                "laboratory_id: %s\n" \
                "lr_date: %s\n" \
                "lr_time: %d\n" % (self.lr_id,
                                   self.laboratory_id,
                                   self.lr_date,
                                   self.lr_time)
