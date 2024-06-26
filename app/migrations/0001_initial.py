# Generated by Django 5.0.1 on 2024-05-18 13:21

import datetime
import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=50, unique=True)),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('is_reset_password_email_token_expired', models.BooleanField(default=True)),
                ('is_reset_password_token_expired', models.BooleanField(default=True)),
                ('role', models.CharField(blank=True, choices=[('trainer', 'Trainer'), ('student', 'Student'), ('coordinator', 'Coordinator')], max_length=20, null=True)),
                ('is_reset_password_needed', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CourseDays',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.CharField(choices=[('luni', 'Luni'), ('marti', 'Marti'), ('miercuri', 'Miercuri'), ('joi', 'Joi'), ('vineri', 'Vineri'), ('sambata', 'Sambata'), ('duminica', 'Duminica')], max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('feedback_for', models.CharField(choices=[('trainer', 'Trainer'), ('student', 'Student'), ('school', 'School'), ('course', 'Course')])),
            ],
        ),
        migrations.CreateModel(
            name='SentEmailsMessages',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sent_on_time', models.TimeField(auto_now_add=True)),
                ('sent_on_date', models.DateField(auto_now_add=True)),
                ('sent_to_mail', models.CharField(max_length=100)),
                ('sent_mail_subject', models.TextField(max_length=500)),
                ('sent_mail_body', models.TextField(max_length=500)),
                ('has_errors', models.BooleanField(default=False)),
                ('error_message', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SentWhatsappMessages',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sent_on_time', models.TimeField(auto_now_add=True)),
                ('sent_on_date', models.DateField(auto_now_add=True)),
                ('sent_to_number', models.CharField(max_length=50)),
                ('sent_message', models.TextField(max_length=500)),
                ('has_errors', models.BooleanField(default=False)),
                ('error_message', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('course_type', models.CharField(max_length=50)),
                ('next_possible_course', models.ManyToManyField(blank=True, related_name='next_course', to='app.course')),
            ],
        ),
        migrations.CreateModel(
            name='CourseDescription',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('short_description', models.TextField(max_length=100)),
                ('long_description', models.TextField(max_length=1000)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='course_description', to='app.course')),
            ],
        ),
        migrations.CreateModel(
            name='School',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
                ('phone_contact', models.CharField(max_length=50)),
                ('email_contact', models.EmailField(max_length=254)),
                ('smartbill_api_key', models.CharField(blank=True, max_length=100, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_school', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('room_name', models.CharField(default='room name', max_length=50)),
                ('capacity', models.SmallIntegerField()),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.school')),
            ],
        ),
        migrations.CreateModel(
            name='Parent',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('phone_number1', models.CharField(blank=True, max_length=50, null=True)),
                ('phone_number2', models.CharField(blank=True, max_length=50, null=True)),
                ('email1', models.CharField(blank=True, max_length=50, null=True)),
                ('email2', models.CharField(blank=True, max_length=50, null=True)),
                ('active_account', models.BooleanField(default=True)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='school_students', to='app.school')),
            ],
        ),
        migrations.CreateModel(
            name='DaysOff',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_day_off', models.DateField()),
                ('last_day_off', models.DateField()),
                ('day_off_info', models.CharField(max_length=200)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.school')),
            ],
        ),
        migrations.CreateModel(
            name='CourseSchedule',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('group_name', models.CharField(max_length=50)),
                ('total_sessions', models.SmallIntegerField()),
                ('first_day_of_session', models.DateField()),
                ('last_day_of_session', models.DateField()),
                ('day', models.CharField(choices=[('luni', 'Luni'), ('marti', 'Marti'), ('miercuri', 'Miercuri'), ('joi', 'Joi'), ('vineri', 'Vineri'), ('sambata', 'Sambata'), ('duminica', 'Duminica')], max_length=15)),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField(default=None)),
                ('course_type', models.CharField(choices=[('onl', 'Online'), ('hbr', 'Hibrid'), ('sed', 'Sediu')], max_length=10)),
                ('online_link', models.CharField(blank=True, max_length=500, null=True)),
                ('can_be_used_as_online_make_up_for_other_schools', models.BooleanField(default=True)),
                ('available_places_for_make_up_online', models.IntegerField(default=3)),
                ('available_places_for_make_up_on_site', models.IntegerField(default=3)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='course_schedules', to='app.course')),
                ('classroom', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.room')),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='school_courses', to='app.school')),
            ],
        ),
        migrations.CreateModel(
            name='SchoolSchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('working_day', models.CharField(choices=[('luni', 'Luni'), ('marti', 'Marti'), ('miercuri', 'Miercuri'), ('joi', 'Joi'), ('vineri', 'Vineri'), ('sambata', 'Sambata'), ('duminica', 'Duminica')], max_length=20)),
                ('start_hour', models.TimeField()),
                ('end_hour', models.TimeField()),
                ('school', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.school')),
            ],
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('session_passed', models.BooleanField(default=False)),
                ('date', models.DateField()),
                ('session_no', models.SmallIntegerField()),
                ('course_session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sessions', to='app.courseschedule')),
            ],
        ),
        migrations.CreateModel(
            name='MakeUp',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('date_time', models.DateTimeField(blank=True, null=True)),
                ('end_time', models.TimeField(default=None)),
                ('online_link', models.CharField(max_length=500)),
                ('type', models.CharField(blank=True, choices=[('onl', 'Online'), ('hbr', 'Hibrid'), ('sed', 'Sediu')], max_length=50, null=True)),
                ('duration_in_minutes', models.SmallIntegerField(default=30)),
                ('make_up_approved', models.BooleanField(default=False)),
                ('make_up_completed', models.BooleanField(default=False)),
                ('can_be_used_as_online_make_up_for_other_schools', models.BooleanField(default=True)),
                ('available_places_for_make_up_online', models.IntegerField(default=3)),
                ('available_places_for_make_up_on_site', models.IntegerField(default=3)),
                ('classroom', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.room')),
                ('session', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.session')),
            ],
        ),
        migrations.CreateModel(
            name='SessionsDescription',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('min_session_no_description', models.IntegerField()),
                ('max_session_no_description', models.IntegerField()),
                ('description', models.TextField(max_length=1000)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='session_descriptions', to='app.course')),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='children', to='app.parent')),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='student_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SessionPresence',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('status', models.CharField(choices=[('present', 'Present'), ('absent', 'Absent'), ('made_up_complete', 'Made Up Complete'), ('made_up_setup', 'Made Up Setup'), ('made_up_absent', 'Made Up Absent')], max_length=20)),
                ('session', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='session_presences', to='app.session')),
                ('student', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='student_presences', to='app.student')),
            ],
        ),
        migrations.CreateModel(
            name='News',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=50)),
                ('short_description', models.CharField(max_length=100)),
                ('text', models.TextField(max_length=1000)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('news_for_group', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.courseschedule')),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.school')),
                ('news_for_student', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.student')),
            ],
        ),
        migrations.CreateModel(
            name='AbsentStudent',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('is_absence_in_crm', models.BooleanField(default=False)),
                ('is_absence_communicated_to_parent', models.BooleanField(default=False)),
                ('is_absence_completed', models.BooleanField(default=False, help_text='if make up happened and student was not absent')),
                ('is_absent_for_absence', models.BooleanField(blank=True, help_text='if student was absent for makeup', null=True)),
                ('has_make_up_scheduled', models.BooleanField(default=False)),
                ('is_make_up_online', models.BooleanField(default=False)),
                ('is_make_up_on_site', models.BooleanField(default=False)),
                ('comment', models.TextField(blank=True, max_length=500, null=True)),
                ('choosed_make_up_session_for_absence', models.ForeignKey(blank=True, help_text='get absences setted up for make up', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='make_up_absences', to='app.makeup')),
                ('absent_on_session', models.ForeignKey(help_text='get all absences for session', on_delete=django.db.models.deletion.CASCADE, related_name='session_absences', to='app.session')),
                ('choosed_course_session_for_absence', models.ForeignKey(blank=True, help_text='get absences setted up for session', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='course_session_absence', to='app.session')),
                ('absent_participant', models.ForeignKey(help_text='get all absences for student', on_delete=django.db.models.deletion.CASCADE, related_name='student_absences', to='app.student')),
            ],
        ),
        migrations.CreateModel(
            name='StudentCourseSchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField(blank=True, null=True)),
                ('course_schedule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.courseschedule')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.student')),
            ],
            options={
                'unique_together': {('course_schedule', 'student')},
            },
        ),
        migrations.AddField(
            model_name='courseschedule',
            name='students',
            field=models.ManyToManyField(related_name='course_schedule_students', through='app.StudentCourseSchedule', to='app.student'),
        ),
        migrations.CreateModel(
            name='StudentInvoice',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('payment_frequency', models.CharField(choices=[('monthly', 'Lunar'), ('module', 'Semestrial'), ('yearly', 'Anual'), ('four_courses', 'La 4 cursuri')], max_length=50)),
                ('module_full_price', models.FloatField()),
                ('invoice_price', models.FloatField()),
                ('full_discount', models.FloatField()),
                ('discount_details', models.CharField(max_length=100)),
                ('invoice_with_student_found', models.BooleanField(default=False)),
                ('smartbill_client', models.CharField(max_length=100, null=True)),
                ('smarbill_cif', models.CharField(max_length=100, null=True)),
                ('smarbill_email', models.CharField(max_length=100, null=True)),
                ('smarbill_phone', models.CharField(blank=True, max_length=100)),
                ('course_schedule', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.courseschedule')),
                ('student', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.student')),
            ],
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('invoice_no', models.CharField(max_length=50)),
                ('invoice_status', models.CharField(blank=True, choices=[('platita', 'Platita'), ('emisa', 'Emisa'), ('depasita', 'Depasita'), ('anulata', 'Anulata')], max_length=20, null=True)),
                ('invoice_date_time', models.DateTimeField(default=datetime.datetime(2024, 5, 18, 13, 21, 53, 744023))),
                ('student_invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.studentinvoice')),
            ],
        ),
        migrations.CreateModel(
            name='Trainer',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('phone_contact', models.CharField(max_length=50)),
                ('email_contact', models.EmailField(max_length=254)),
                ('user', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='session',
            name='session_trainer',
            field=models.ForeignKey(blank=True, help_text='In case other trainer will replace a trainer', null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.trainer'),
        ),
        migrations.AddField(
            model_name='makeup',
            name='trainer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.trainer'),
        ),
        migrations.CreateModel(
            name='DailySchoolSchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('busy_from', models.TimeField()),
                ('busy_to', models.TimeField()),
                ('blocked_by', models.CharField(choices=[('course', 'Curs'), ('make_up', 'Make Up'), ('other', 'Other')], max_length=20)),
                ('activity_type', models.CharField(verbose_name=(('online', 'Online'), ('sed', 'Sediu')))),
                ('room', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.room')),
                ('school_schedule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.schoolschedule')),
                ('trainer_involved', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.trainer')),
            ],
        ),
        migrations.AddField(
            model_name='courseschedule',
            name='default_trainer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.trainer'),
        ),
        migrations.CreateModel(
            name='TrainerFromSchool',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('school', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='school_trainers', to='app.school')),
                ('trainer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.trainer')),
            ],
        ),
        migrations.CreateModel(
            name='TrainerSchedule',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('year', models.IntegerField(default=2024)),
                ('week', models.IntegerField(default=1)),
                ('date', models.DateField(blank=True, null=True)),
                ('available_hour_from', models.TimeField()),
                ('available_hour_to', models.TimeField()),
                ('online_only', models.BooleanField(default=False)),
                ('available_day', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='app.coursedays')),
                ('school', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.school')),
                ('trainer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.trainer')),
            ],
        ),
    ]
