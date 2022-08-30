from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver, Signal
from django.utils.timezone import now, utc
from datetime import datetime, time
from ckeditor.fields import RichTextField
from import_export import resources

from r2.logger import log
# now().astimezone('Asia/Kolkata')
import os as r2_os
from django.utils.encoding import python_2_unicode_compatible

from r2_app.r2_services.pushy import PushyAPI

BATCH_COMPANY_LOGO = 'batch_company_logo/'
STUDENT_PROFILE_PICTURE = 'student_profile_picture/'
POST_IMG = 'post_image/'
ASSIGNMENT_IMG = 'assign_image/'
BADGE_IMG = 'badge_image/'


DEFAULT_STUDENT_PROFILE_PICTURE = 'default/profile_picture/placeholder.png'

DEVICE_TYPE = (
    ('Android', 'Android'),
    ('iOS', 'iOS')
)
POSTED_BY = (
    ('Admin', 'Admin'),
    ('Student', 'Student')
)
QUESTION_TYPE = (
    ('MCQ', 'MCQ'),
    ('Essay', 'Essay')
)
QUESTION_OPTIONS = (
    ('A', 'A'),
    ('B', 'B'),
    ('C', 'C'),
    ('D', 'D')
)
ANSWER_STATUS = (
    ('Pending', 'Pending'),
    ('Checked', 'Checked')
)
QUIZ_RATING = (
    ('0', '0'),
    ('1', '1'),
    ('2', '2'),
    ('3', '3'),
    ('4', '4'),
    ('5', '5'),
)
REDIRECT_TO = (
    ('Post', 'Post'),
    ('Quiz', 'Quiz'),
    ('Comment', 'Comment'),
    ('Application', 'Application'),
    ('Assignment', 'Assignment'),
)


def student_profile_pic_upload(instance, filename):
    # if r2_os.path.isfile('media/student_profile_picture/%s/%s' % (instance.id, filename)):
    #     r2_os.remove('media/student_profile_picture/%s/%s' % (instance.id, filename))

    return '{0}/{1}/{2}'.format(STUDENT_PROFILE_PICTURE, instance.id, filename)


def post_pic_upload(instance, filename):
    return '{0}/{1}/{2}'.format(POST_IMG, instance.id, filename)


def assign_pic_upload(instance, filename):
    return '{0}/{1}/{2}'.format(ASSIGNMENT_IMG, instance.id, filename)


def batch_logo_upload(instance, filename):
    # file will be uploaded to media/batch_company_logo/<user_id>/<filename>
    # if r2_os.path.isfile('media/batch_company_logo/%s/%s' % (instance.id, filename)):
    #     r2_os.remove('media/batch_company_logo/%s/%s' % (instance.id, filename))

    return '{0}/{1}/{2}'.format(BATCH_COMPANY_LOGO, instance.id, filename)


def badge_pic_upload(instance, filename):
    return '{0}/{1}/{2}'.format(BADGE_IMG, instance.id, filename)


@python_2_unicode_compatible
class Batch(models.Model):
    id = models.AutoField(primary_key=True)
    batch_company_name = models.CharField(max_length=51)
    batch_name = models.CharField(max_length=100, blank=True, null=True)
    batch_desc = models.CharField(max_length=251)
    batch_create_at = models.DateField(auto_now_add=True)
    batch_company_logo = models.ImageField(upload_to=batch_logo_upload, blank=True, null=True)

    def __str__(self):
        return "%s. %s" % (self.id, self.batch_name)


@python_2_unicode_compatible
class Student(models.Model):
    student_user_id = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    id = models.AutoField(primary_key=True)
    student_password = models.CharField(max_length=51)
    student_picture_url = models.ImageField(
        upload_to=student_profile_pic_upload,
        null=True,
        default=DEFAULT_STUDENT_PROFILE_PICTURE,
        max_length=800
    )
    student_create_at = models.DateField(auto_now_add=True)
    student_email = models.EmailField()
    student_first_name = models.CharField(max_length=100, null=True)
    student_last_name = models.CharField(max_length=100, null=True)
    student_batch_id = models.ForeignKey(Batch, on_delete=models.CASCADE)
    student_device_type = models.CharField(choices=DEVICE_TYPE, max_length=100, null=True)
    student_os_version = models.CharField(max_length=20, null=True, blank=True)
    student_app_version = models.CharField(max_length=20, null=True, blank=True)
    student_device_token = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return "%s. %s %s" % (self.id, self.student_first_name, self.student_last_name)


@python_2_unicode_compatible
class Post(models.Model):
    id = models.AutoField(primary_key=True)
    post_title = models.CharField(max_length=500, blank=True, null=True)
    post_text = RichTextField()
    post_has_img = models.BooleanField(default=False)
    post_img_url = models.ImageField(upload_to=post_pic_upload, blank=True, null=True)
    post_has_video = models.BooleanField(default=False)
    post_video = models.URLField(blank=True, null=True)
    post_created_at = models.DateTimeField(auto_now_add=True)
    post_user_id = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)
    posted_by = models.CharField(choices=POSTED_BY, default='Admin', max_length=10)
    post_is_enabled = models.BooleanField(default=True)
    post_batch_id = models.ForeignKey(Batch, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return "%s. %s" % (self.id, self.post_title)


@python_2_unicode_compatible
class Like(models.Model):
    id = models.AutoField(primary_key=True)
    like_student = models.ForeignKey(Student, on_delete=models.CASCADE)
    like_post = models.ForeignKey(Post, on_delete=models.CASCADE)

    def __str__(self):
        return "%s" % self.id


@python_2_unicode_compatible
class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    comment_post = models.ForeignKey(Post, on_delete=models.CASCADE)
    comment_student = models.ForeignKey(Student, on_delete=models.CASCADE)
    comment_created_at = models.DateTimeField(auto_now_add=True)
    comment_text = models.CharField(max_length=500)
    comment_is_enabled = models.BooleanField(default=True)

    def __str__(self):
        return "%s. %s" % (self.id, self.comment_text)


@python_2_unicode_compatible
class Bookmark(models.Model):
    id = models.AutoField(primary_key=True)
    bookmark_created_at = models.DateTimeField(auto_now_add=True)
    bookmark_post = models.ForeignKey(Post, on_delete=models.CASCADE)
    bookmark_student = models.ForeignKey(Student, on_delete=models.CASCADE)

    def __str__(self):
        return '%s' % self.id


@python_2_unicode_compatible
class Quiz(models.Model):
    id = models.AutoField(primary_key=True)
    quiz_desc = models.CharField(max_length=300)
    quiz_created_at = models.DateTimeField(auto_now_add=True)
    quiz_batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    quiz_published = models.BooleanField(default=False, null=True, blank=True)

    def __str__(self):
        return '%s. %s' % (self.id, self.quiz_desc)


@python_2_unicode_compatible
class Question(models.Model):
    id = models.AutoField(primary_key=True)
    question_quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    question_text = models.CharField(max_length=1000)
    question_type = models.CharField(choices=QUESTION_TYPE, max_length=5)
    question_op_a = models.CharField(max_length=1000, null=True, blank=True)
    question_op_b = models.CharField(max_length=1000, null=True, blank=True)
    question_op_c = models.CharField(max_length=1000, null=True, blank=True)
    question_op_d = models.CharField(max_length=1000, null=True, blank=True)
    question_correct_ans = models.CharField(choices=QUESTION_OPTIONS, max_length=1, null=True, blank=True)

    def __str__(self):
        return '%s. %s' % (self.id, self.question_text)


@python_2_unicode_compatible
class Answer(models.Model):
    id = models.AutoField(primary_key=True)
    answer_student = models.ForeignKey(Student, on_delete=models.CASCADE)
    answer_question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_text = models.CharField(max_length=2000)
    answer_status = models.CharField(choices=ANSWER_STATUS, max_length=10, null=True)
    answer_seen = models.IntegerField(default=0, null=True)
    answer_attempt = models.IntegerField(default=0, null=True)
    answer_other_marks = models.IntegerField(default=0, null=True)

    def __str__(self):
        return '%s. %s' % (self.id, self.answer_text)


@python_2_unicode_compatible
class StudentQuiz(models.Model):
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, null=True)
    quiz_rating = models.CharField(choices=QUIZ_RATING, max_length=1, null=True)
    quiz_submit_date = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return '%s. %s %s' % (self.id, self.student.student_first_name, self.student.student_last_name)


@python_2_unicode_compatible
class Feedback(models.Model):
    id = models.AutoField(primary_key=True)
    feedback_student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True)
    feedback_text = models.CharField(max_length=500, null=True)
    feedback_created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return '%s' % self.id


@python_2_unicode_compatible
class Assignment(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=300, null=True, blank=True)
    text = RichTextField()
    has_img = models.BooleanField(default=False)
    img_url = models.ImageField(upload_to=assign_pic_upload, blank=True, null=True)
    has_video = models.BooleanField(default=False)
    video_url = models.URLField(blank=True, null=True)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return '%s' % self.id


@python_2_unicode_compatible
class AssignmentAnswer(models.Model):
    id = models.AutoField(primary_key=True)
    answer_text = models.CharField(max_length=10000)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    answer_seen = models.IntegerField(default=0, null=True)
    answer_attempt = models.IntegerField(default=0, null=True)
    answer_other_marks = models.IntegerField(default=0, null=True)
    status = models.CharField(choices=ANSWER_STATUS, default='Pending', max_length=10, blank=True, null=True)

    def __str__(self):
        return '%s' % self.id


@python_2_unicode_compatible
class ApplicationTopic(models.Model):
    id = models.AutoField(primary_key=True)
    topic_text = models.CharField(max_length=500)
    topic_desc = models.CharField(max_length=500)
    topic_date = models.DateTimeField(auto_now_add=True)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)

    def __str__(self):
        return '%s' % self.id


@python_2_unicode_compatible
class Application(models.Model):
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True)
    submitted_at = models.DateField(auto_now_add=True, blank=True, null=True)
    topic = models.ForeignKey(ApplicationTopic, on_delete=models.CASCADE)
    instance = models.CharField(max_length=10000)
    effect = models.CharField(max_length=10000)
    well = models.CharField(max_length=10000)
    unexpected = models.CharField(max_length=10000)
    reflection = models.CharField(max_length=10000)
    different = models.CharField(max_length=10000)
    date_applied = models.DateField(blank=True, null=True)
    app_seen = models.IntegerField(default=0, null=True)
    app_attempt = models.IntegerField(default=0, null=True)
    app_other_marks = models.IntegerField(default=0, null=True)
    app_status = models.CharField(choices=ANSWER_STATUS, max_length=10, default='Pending')

    def __str__(self):
        return '%s' % self.id


@python_2_unicode_compatible
class Notification(models.Model):
    id = models.AutoField(primary_key=True)
    notif_text = RichTextField()
    notif_post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    notif_comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True)
    notif_quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, null=True, blank=True, related_name='notif_quiz')
    notif_app_topic = models.ForeignKey(ApplicationTopic, on_delete=models.CASCADE, related_name='notif_app_topic', null=True, blank=True)
    notif_review_app = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='notif_review_app', null=True, blank=True)
    notif_assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='notif_assignment', null=True, blank=True)
    notif_review_assignment = models.ForeignKey(AssignmentAnswer, on_delete=models.CASCADE, related_name='notif_review_assignment', null=True, blank=True)
    notif_student = models.ForeignKey(Student, related_name='notif_student', on_delete=models.CASCADE)  # Receiver of the notification
    notifier_student = models.ForeignKey(Student, related_name='notifier_student', on_delete=models.CASCADE, null=True, blank=True)  # Sender of the notification
    notif_created_at = models.DateTimeField(auto_now_add=True)
    notif_read = models.BooleanField(default=False)
    notif_type = models.CharField(choices=POSTED_BY, default='Admin', max_length=20)
    redirect_to = models.CharField(choices=REDIRECT_TO, max_length=50, default='Post')

    def __str__(self):
        return '%s' % self.id


@python_2_unicode_compatible
class R2Settings(models.Model):
    id = models.AutoField(primary_key=True)
    android_current_version = models.CharField(max_length=20, null=True, blank=True)
    ios_current_version = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return '%s' % self.id


@python_2_unicode_compatible
class Badge(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    desc = models.CharField(max_length=500)
    image = models.ImageField(upload_to=badge_pic_upload, null=True, blank=True)

    def __str__(self):
        return '%s. %s' % (self.id, self.name)


class StudentBadge(models.Model):
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)

    def __str__(self):
        return '%s' % self.id


# ----------------------
# ----------------------
# ----------------------
# ------TRIGGERS--------
# ----------------------
# ----------------------
# ----------------------


@receiver(post_save, sender=Post, dispatch_uid="new_post_trigger")
def new_post_trigger(sender, instance, created, **kwargs):

    try:

        current_post = instance

        if created:
            print('\ncalled new_post_trigger\n')
            log.info('called new_post_trigger')

            # if current_post.post_video is None:
            #     current_post.post_has_video = False
            # else:
            #     current_post.post_has_video = True
            #
            # # print('\n\n\n\n\n\n Image url length: %s' % current_post.post_img_url.length)
            #
            # if current_post.post_img_url:
            #     current_post.post_has_img = True
            # else:
            #     current_post.post_has_img = False

            current_post.save()

            current_batch = current_post.post_batch_id

            all_students = Student.objects.filter(student_batch_id=current_batch)

            pushy_to = []

            for one_student in all_students:

                try:

                    Notification.objects.create(
                        notif_text='New post in your batch: <strong>%s</strong>' % current_post.post_title,
                        notif_post=current_post,
                        notif_student=one_student,
                        notif_type='Admin',
                        redirect_to='Post'
                    ).save()

                    if one_student.student_device_token is not None:
                        pushy_to.append(str(one_student.student_device_token))

                except Exception as ex:
                    log.error('New Post: Unable to send in-app notification: %s' % ex)

                PushyAPI.prepare_notification(
                    student=one_student,
                    data_msg='New Post',
                    body_text='New post in your batch: %s' % current_post.post_title
                )

            log.info('\nNotification for new post created successfully\n')

    except Exception as ex:
        log.error('\nUnable to create notification of new post: %s\n' % ex)


@receiver(post_save, sender=Comment, dispatch_uid="new_comment_trigger")
def new_comment_trigger(sender, instance, created, **kwargs):
    try:

        if created:
            print('\ncalled new_comment_trigger\n')
            log.info('called new_comment_trigger')

            current_batch = instance.comment_post.post_batch_id

            all_students = Student.objects.exclude(
                id=instance.comment_student.id
            ).filter(student_batch_id=current_batch)

            for one_student in all_students:
                Notification.objects.create(
                    notif_text='<strong>%s</strong> has commented on post: %s' % (
                        instance.comment_student.student_first_name,
                        instance.comment_post.post_title
                    ),
                    notif_post=instance.comment_post,
                    notif_comment=instance,
                    notif_student=one_student,
                    notifier_student=instance.comment_student,
                    notif_type='Student',
                    redirect_to='Post'
                ).save()

                PushyAPI.prepare_notification(
                    student=one_student,
                    data_msg='New Comment',
                    body_text='%s has commented on post: %s' % (
                        instance.comment_student.student_first_name,
                        instance.comment_post.post_title
                    )
                )

            print('\nNotification for new comment created successfully\n')
            log.info('Notification for new comment created successfully')
    except Exception as ex:
        print('\nUnable to create notification of new comment: %s\n' % ex)
        log.error('Unable to create notification of new comment: %s' % ex)


@receiver(post_save, sender=ApplicationTopic, dispatch_uid="new_application_topic_trigger")
def new_application_topic_trigger(sender, instance, created, **kwargs):
    try:

        if created:
            print('\ncalled application topic trigger\n')
            log.info('called application topic trigger')

            current_batch = instance.batch

            all_students = Student.objects.filter(student_batch_id=current_batch)

            for one_student in all_students:
                Notification.objects.create(
                    notif_text='New Application in your batch: <strong>%s</strong>' % (
                        instance.topic_text
                    ),
                    notif_student=one_student,
                    notif_type='Admin',
                    redirect_to='Application',
                    notif_app_topic=instance
                ).save()

                PushyAPI.prepare_notification(
                    student=one_student,
                    data_msg='New Application Topic',
                    body_text='%s, new Application in your batch: %s' % (
                        one_student.student_first_name,
                        instance.topic_text
                    )
                )

            print('\nNotification for new application created successfully\n')
            log.info('Notification for new application created successfully')
    except Exception as ex:
        print('\nUnable to create notification of new application: %s\n' % ex)
        log.error('Unable to create notification of new application: %s' % ex)


@receiver(post_save, sender=Assignment, dispatch_uid="new_assignment_topic_trigger")
def new_assignment_topic_trigger(sender, instance, created, **kwargs):
    try:

        if created:
            print('\ncalled assignment topic trigger\n')
            log.info('called assignment topic trigger')

            current_batch = instance.batch

            all_students = Student.objects.filter(student_batch_id=current_batch)

            for one_student in all_students:
                Notification.objects.create(
                    notif_text='New Assignment in your batch: <strong>%s</strong>' % (
                        instance.title
                    ),
                    notif_student=one_student,
                    notif_type='Admin',
                    redirect_to='Assignment',
                    notif_assignment=instance
                ).save()

                PushyAPI.prepare_notification(
                    student=one_student,
                    data_msg='New Assignment',
                    body_text='%s, new Assignment in your batch: %s' % (
                        one_student.student_first_name,
                        instance.title
                    )
                )

            print('\nNotification for new assignment created successfully\n')
            log.info('Notification for new assignment created successfully')
    except Exception as ex:
        print('\nUnable to create notification of new assignment: %s\n' % ex)
        log.error('Unable to create notification of new assignment: %s' % ex)


# @receiver(post_save, sender=Quiz, dispatch_uid='new_quiz_trigger')
# def new_quiz_trigger(sender, instance, created, **kwargs):
#     try:
#         if created:
#             current_batch = instance.quiz_batch
#
#             all_students = Student.objects.filter(student_batch_id=current_batch)
#
#             for one_student in all_students:
#                 Notification.objects.create(
#                     notif_text='<strong>%s</strong>, You have a new quiz to solve in your batch.' % one_student.student_first_name,
#                     notif_student=one_student,
#                     notif_type='Admin',
#                     notif_quiz=instance
#                 ).save()
#             print('Notification for new quiz created successfully')
#
#     except Exception as ex:
#         print('\nUnable to create notification for new quiz: %s\n' % ex)
