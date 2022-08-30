from django.conf.urls import  static
from r2 import settings
from r2_app import views, custom_admin_views
from django.urls import re_path as url

urlpatterns = [
    url(r'^$', custom_admin_views.custom_admin_panel, name='custom_admin_panel'),
    url(r'^about_page/$', custom_admin_views.custom_admin_panel_about, name='custom_admin_panel_about'),
    url(r'^help_page/$', custom_admin_views.custom_admin_panel_help, name='custom_admin_panel_help'),
    url(r'^batch_home/$', custom_admin_views.batch_home, name='batch_home'),
    url(r'^quiz_home/$', custom_admin_views.quiz_home, name='quiz_home'),
    url(r'^home_page/$', custom_admin_views.home_page, name='home_page'),
    url(r'^student_home/$', custom_admin_views.student_home, name='student_home'),
    url(r'^new_quiz/$', custom_admin_views.new_quiz, name='new_quiz'),
    url(r'^post_home/$', custom_admin_views.post_home, name='post_home'),
    url(r'^review_as/$', custom_admin_views.review_as, name='review_as'),
    url(r'^review_application/$', custom_admin_views.review_application, name='review_application'),
    url(r'^batch_perf/$', custom_admin_views.batch_perf, name='batch_perf'),
    url(r'^view_badge/$', custom_admin_views.view_badge, name='view_badge'),
] + static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
