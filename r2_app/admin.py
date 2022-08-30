from django.contrib import admin
from .models import Answer, Question, Bookmark, StudentQuiz, Batch, Comment, Quiz, Student, Notification, Post, \
    Feedback, Like, Assignment, AssignmentAnswer, Application, ApplicationTopic, R2Settings, Badge, StudentBadge

from import_export.admin import ImportExportMixin


class StudentAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'student_picture_url', 'student_create_at', 'student_email', 'student_first_name',
                    'student_last_name', 'student_batch_id', 'student_device_type', 'student_os_version',
                    'student_app_version', 'student_device_token')
    search_fields = ('id', 'student_picture_url', 'student_create_at', 'student_email', 'student_first_name',
                     'student_last_name', 'student_device_type', 'student_os_version', 'student_app_version',
                     'student_batch_id__batch_name', 'student_batch_id__batch_company_name', 'student_device_token')


class BatchAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'batch_desc', 'batch_create_at', 'batch_name', 'batch_company_name', 'batch_company_logo')
    search_fields = ('id', 'batch_desc', 'batch_create_at', 'batch_name', 'batch_company_name', 'batch_company_logo')


class PostAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'post_title', 'post_created_at', 'post_user_id', 'post_img_url', 'post_has_img', 'post_video',
                    'post_has_video', 'post_text', 'post_is_enabled')
    search_fields = ('id', 'post_title', 'post_created_at', 'post_img_url', 'post_has_img', 'post_video',
                     'post_has_video', 'post_text')


class LikeAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'like_student', 'like_post')
    search_fields = ('id',)


class CommentAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'comment_post', 'comment_student', 'comment_created_at', 'comment_text',
                    'comment_is_enabled')
    search_fields = ('id', 'comment_created_at', 'comment_text', 'comment_is_enabled')


class BookmarkAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'bookmark_created_at', 'bookmark_post', 'bookmark_student')
    search_fields = ('id', 'bookmark_created_at')


class QuizAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'quiz_desc', 'quiz_created_at', 'quiz_batch', 'quiz_published')
    search_fields = ('id', 'quiz_desc', 'quiz_created_at', 'quiz_published')


class QuestionAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'question_quiz', 'question_text', 'question_type', 'question_op_a', 'question_op_b',
                    'question_op_c', 'question_op_d', 'question_correct_ans')
    search_fields = ('id', 'question_text', 'question_type', 'question_op_a', 'question_op_b',
                     'question_op_c', 'question_op_d', 'question_correct_ans', 'question_quiz__quiz_desc')


class AnswerAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'answer_student', 'answer_question', 'answer_text', 'answer_status', 'answer_seen',
                    'answer_attempt', 'answer_other_marks')
    search_fields = ('id', 'answer_text', 'answer_status', 'answer_seen', 'answer_attempt', 'answer_other_marks'
                     , 'answer_student__student_first_name', 'answer_student__student_last_name')


class StudentQuizAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'student', 'quiz', 'quiz_submit_date')
    search_fields = ('id', 'quiz_submit_date', 'student__student_first_name', 'student__student_last_name')


class FeedbackAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'feedback_student', 'feedback_text', 'feedback_created_at')
    search_fields = ('id', 'feedback_text', 'feedback_created_at')


class NotificationAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'notif_text', 'notif_quiz', 'notif_student', 'notifier_student', 'notif_created_at',
                    'notif_read', 'notif_type', 'redirect_to', 'notif_post', 'notif_comment')
    search_fields = ('id', 'notif_text', 'notif_created_at', 'notif_read', 'notif_type', 'redirect_to')


class AssignmentAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'title', 'text', 'has_img', 'img_url', 'has_video', 'video_url', 'batch')
    search_fields = ('id', 'title', 'text', 'has_img', 'img_url', 'has_video', 'video_url')


class AssignmentAnswerAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'student', 'answer_text', 'assignment', 'submitted_at', 'answer_seen', 'answer_attempt', 'answer_other_marks')
    search_fields = ('id', 'student__student_first_name', 'student__student_last_name', 'answer_text', 'submitted_at', 'answer_seen', 'answer_attempt', 'answer_other_marks')


class ApplicationAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'student', 'submitted_at', 'topic', 'instance', 'effect', 'well', 'unexpected', 'reflection', 'different', 'date_applied', 'app_seen', 'app_attempt', 'app_other_marks', 'app_status')
    search_fields = ('id', 'student__student_first_name', 'student__student_last_name', 'submitted_at', 'topic__topic_text', 'instance', 'effect', 'well', 'unexpected', 'reflection', 'different', 'date_applied', 'app_seen', 'app_attempt', 'app_other_marks', 'app_status')


class ApplicationTopicAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'topic_text', 'topic_desc', 'topic_date', 'batch')
    search_fields = ('id', 'topic_text', 'topic_desc', 'topic_date', 'batch__batch_name', 'batch__batch_company_name')


class R2SettingsAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'android_current_version', 'ios_current_version')
    search_fields = ('id', 'android_current_version', 'ios_current_version')


class BadgeAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'name', 'desc', 'image')
    search_fields = ('id', 'name', 'desc', 'image')


class StudentBadgeAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'student', 'badge')
    search_fields = ('id', 'student__first_name', 'badge__name')


admin.site.register(Student, StudentAdmin)
admin.site.register(Batch, BatchAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Like, LikeAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Bookmark, BookmarkAdmin)
admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(StudentQuiz, StudentQuizAdmin)
admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(Assignment, AssignmentAdmin)
admin.site.register(AssignmentAnswer, AssignmentAnswerAdmin)
admin.site.register(Application, ApplicationAdmin)
admin.site.register(ApplicationTopic, ApplicationTopicAdmin)
admin.site.register(R2Settings, R2SettingsAdmin)
admin.site.register(Badge, BadgeAdmin)
admin.site.register(StudentBadge, StudentBadgeAdmin)

#admin.site.index_template = 'admin/index.html'
admin.site.index_template = 'admin/newadminindextemplate.html'