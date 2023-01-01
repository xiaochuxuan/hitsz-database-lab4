from django.db import models


class AcademicBuild(models.Model):
    build_id = models.CharField(primary_key=True, max_length=10)
    build_name = models.CharField(max_length=14)
    build_address = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'academic_build'


class AvailableLaboratory(models.Model):
    id = models.CharField(primary_key=True, max_length=12)
    laboratory = models.ForeignKey('Laboratory', models.DO_NOTHING, blank=True, null=True)
    laboratory_name = models.CharField(max_length=12)
    avai_date = models.DateField()
    avai_time = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'available_laboratory'


class CompConfiguration(models.Model):
    conf_id = models.CharField(primary_key=True, max_length=10)
    cpu = models.CharField(max_length=14)
    memory = models.IntegerField()
    gpu = models.CharField(max_length=14)
    mainboard = models.CharField(max_length=14)

    class Meta:
        managed = False
        db_table = 'comp_configuration'


class Course(models.Model):
    course_id = models.CharField(primary_key=True, max_length=10)
    course_name = models.CharField(max_length=14)
    course_hours = models.IntegerField()
    course_t = models.CharField(db_column='course_T', max_length=10)  # Field name made lowercase.
    course_depart = models.CharField(max_length=10)
    course_software = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'course'


class CourseSoftware(models.Model):
    software_name = models.CharField(primary_key=True, max_length=14)
    course = models.ForeignKey(Course, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'course_software'
        unique_together = (('software_name', 'course'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class Laboratory(models.Model):
    laboratory_id = models.CharField(primary_key=True, max_length=10)
    manager = models.ForeignKey('Manager', models.DO_NOTHING, blank=True, null=True)
    conf = models.ForeignKey(CompConfiguration, models.DO_NOTHING, blank=True, null=True)
    build = models.ForeignKey(AcademicBuild, models.DO_NOTHING, blank=True, null=True)
    laboratory_name = models.CharField(unique=True, max_length=12)
    area = models.IntegerField()
    location = models.IntegerField()
    comp_sets = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'laboratory'


class LaboratorySoftware(models.Model):
    software_name = models.CharField(primary_key=True, max_length=14)
    laboratory = models.ForeignKey(Laboratory, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'laboratory_software'
        unique_together = (('software_name', 'laboratory'),)


class Manager(models.Model):
    manager_id = models.CharField(primary_key=True, max_length=10)
    t = models.OneToOneField('Teacher', models.DO_NOTHING, db_column='T_id', blank=True, null=True)  # Field name made lowercase.
    manager_name = models.CharField(max_length=12)

    class Meta:
        managed = False
        db_table = 'manager'


class ReservationRecord(models.Model):
    record_id = models.CharField(primary_key=True, max_length=12)
    user = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True)
    manager = models.ForeignKey(Manager, models.DO_NOTHING, blank=True, null=True)
    laboratory_name = models.CharField(max_length=12)
    reserver_time = models.DateTimeField()
    event = models.TextField(blank=True, null=True)
    if_success = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'reservation_record'


class Software(models.Model):
    software_name = models.CharField(primary_key=True, max_length=14)
    software_category = models.CharField(max_length=12, blank=True, null=True)
    version = models.CharField(max_length=14)
    developer = models.CharField(max_length=14)

    class Meta:
        managed = False
        db_table = 'software'


class Teacher(models.Model):
    t_id = models.CharField(db_column='T_id', primary_key=True, max_length=10)  # Field name made lowercase.
    t_name = models.CharField(db_column='T_name', max_length=12)  # Field name made lowercase.
    t_sex = models.CharField(db_column='T_sex', max_length=1)  # Field name made lowercase.
    t_department = models.CharField(db_column='T_department', max_length=14)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'teacher'


class TeacherCourse(models.Model):
    course_id = models.CharField(primary_key=True, max_length=10)
    t = models.ForeignKey(Teacher, models.DO_NOTHING, db_column='T_id')  # Field name made lowercase.
    laboratory_name = models.CharField(max_length=12, blank=True, null=True)
    course_hours = models.IntegerField()
    start_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'teacher_course'
        unique_together = (('course_id', 't'),)


class User(models.Model):
    user_id = models.CharField(primary_key=True, max_length=10)
    t = models.ForeignKey(Teacher, models.DO_NOTHING, db_column='T_id', blank=True, null=True)  # Field name made lowercase.
    user_name = models.CharField(max_length=16)
    user_sex = models.SmallIntegerField()
    password = models.CharField(max_length=16)
    user_phone = models.DecimalField(max_digits=12, decimal_places=0)
    user_character = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = 'user'
