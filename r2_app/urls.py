from django.conf.urls import  static, include
from r2 import settings
from r2_app import views
from django.urls import re_path as url

urlpatterns = [
    url(r'^$', views.default, name='default'),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^get_profile_info/$', views.get_profile_info, name='get_profile_info'),
    url(r'^get_all_students/$', views.get_all_students, name='get_all_students'),
    url(r'^add_post/$', views.add_post, name='add_post'),
    url(r'^get_posts/$', views.get_posts, name='get_posts'),
    url(r'^like_post/$', views.like_post, name='like_post'),
    url(r'^add_comment/$', views.add_comment, name='add_comment'),
    url(r'^get_comments/$', views.get_comments, name='get_comments'),
    url(r'^change_password/$', views.change_password, name='change_password'),
    url(r'^toggle_bookmark/$', views.toggle_bookmark, name='toggle_bookmark'),
    url(r'^get_bookmarks/$', views.get_bookmarks, name='get_bookmarks'),
    url(r'^update_profile/$', views.update_profile, name='update_profile'),
    url(r'^submit_quiz/$', views.submit_quiz, name='submit_quiz'),
    url(r'^add_feedback/$', views.add_feedback, name='add_feedback'),
    url(r'^ranking_graph/(\w*)', views.ranking_graph, name='ranking_graph'),
    url(r'^get_batch_students/$', views.get_batch_students, name='get_batch_students'),
    url(r'^get_notifications/$', views.get_notifications, name='get_notifications'),
    url(r'^read_notification/$', views.read_notification, name='read_notification'),
    url(r'^delete_all_notifications/$', views.delete_all_notifications, name='delete_all_notifications'),
    url(r'^set_version/$', views.set_version, name='set_version'),
    url(r'^get_student_quiz_list/$', views.get_student_quiz_list, name='get_student_quiz_list'),
    url(r'^get_dashboard_count/$', views.get_dashboard_count, name='get_dashboard_count'),
    url(r'^get_quiz_questions/$', views.get_quiz_questions, name='get_quiz_questions'),
    url(r'^submit_assignment/$', views.submit_assignment, name='submit_assignment'),
    url(r'^get_student_assign_list/$', views.get_student_assign_list, name='get_student_assign_list'),
    url(r'^start_assignment/$', views.start_assignment, name='start_assignment'),
    url(r'^get_application_list/$', views.get_application_list, name='get_application_list'),
    url(r'^submit_application/$', views.submit_application, name='submit_application'),
    url(r'^view_quiz_answers/$', views.view_quiz_answers, name='view_quiz_answers'),
    url(r'^view_app_answers/$', views.view_app_answers, name='view_app_answers'),
    url(r'^view_assignment_ans/$', views.view_assignment_ans, name='view_assignment_ans'),
    url(r'^share_post/(\w*)', views.share_post, name='share_post'),
    url(r'^get_leader_board_ranks/$', views.get_leader_board_ranks, name='get_leader_board_ranks'),
    url(r'^boost_me_info/$', views.boost_me_info, name='boost_me_info'),

    # ADMIN APIs
    url(r'^get_admin_counts/$', views.get_admin_counts, name='get_admin_counts'),

    url(r'^add_batch/$', views.add_batch, name='add_batch'),
    url(r'^update_batch/$', views.update_batch, name='update_batch'),
    url(r'^delete_batch/$', views.delete_batch, name='delete_batch'),
    url(r'^admin_batch_performance/$', views.admin_batch_performance, name='admin_batch_performance'),

    url(r'^create_quiz/$', views.create_quiz, name='create_quiz'),
    url(r'^get_quiz_by_batch_admin/$', views.get_quiz_by_batch_admin, name='get_quiz_by_batch_admin'),
    url(r'^get_question_by_quiz_admin/$', views.get_question_by_quiz_admin, name='get_question_by_quiz_admin'),
    url(r'^submit_quiz_review/$', views.submit_quiz_review, name='submit_quiz_review'),
    url(r'^get_quiz_quest_to_choose/$', views.get_quiz_quest_to_choose, name='get_quiz_quest_to_choose'),

    url(r'^get_students/$', views.get_students, name='get_students'),
    url(r'^get_all_batches/$', views.get_all_batches, name='get_all_batches'),
    url(r'^edit_student/$', views.edit_student, name='edit_student'),
    url(r'^delete_student/$', views.delete_student, name='delete_student'),
    url(r'^add_student/$', views.add_student, name='add_student'),
    url(r'^update_student_badges/$', views.update_student_badges, name='update_student_badges'),

    url(r'^admin_get_posts/$', views.admin_get_posts, name='admin_get_posts'),
    url(r'^admin_add_post/$', views.admin_add_post, name='admin_add_post'),
    url(r'^admin_udpate_post/$', views.admin_udpate_post, name='admin_udpate_post'),
    url(r'^admin_delete_post/$', views.admin_delete_post, name='admin_delete_post'),

    url(r'^admin_get_assign_ans/$', views.admin_get_assign_ans, name='admin_get_assign_ans'),
    url(r'^admin_review_assign/$', views.admin_review_assign, name='admin_review_assign'),

    url(r'^admin_get_topics/$', views.admin_get_topics, name='admin_get_topics'),
    url(r'^admin_get_appls/$', views.admin_get_appls, name='admin_get_appls'),
    url(r'^admin_review_application/$', views.admin_review_application, name='admin_review_application'),

    url(r'^admin_view_badges/$', views.admin_view_badges, name='admin_review_application'),
    url(r'^admin_add_badge/$', views.admin_add_badge, name='admin_review_application'),

    url(r'^get_badge_list/$', views.get_badge_list, name='get_badge_list'),

    url(r'^admin_login/$', views.admin_login, name='admin_login'),

    # ADMIN PANEL VIEWS
    url(r'^custom_admin_panel/', include('r2_app.custom_admin_urls')),
] + static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

