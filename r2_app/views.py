from django.views.decorators.csrf import csrf_exempt
import json
from django.shortcuts import render
from django.http import HttpResponse
from r2_app.manager.user_manage import UserProfile


def default(request):
    return render(request, "default.html", {})


@csrf_exempt
def login(request):
    data = {}
    if request.method == "POST":
        login_res = UserProfile.login(request)
        data['login'] = login_res

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def signup(request):
    data = {}
    if request.method == "POST":
        signup_res = UserProfile.signup(request)
        data['signup'] = signup_res

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def get_profile_info(request):
    data = {}
    if request.method == "POST":
        get_profile_info_res = UserProfile.get_profile_info(request)
        data['get_profile_info'] = get_profile_info_res

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def get_all_students(request):
    data = {}
    if request.method == "POST":
        get_all_students_res = UserProfile.get_all_students(request)
        data['get_all_students'] = get_all_students_res

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def add_post(request):
    data = {}
    if request.method == "POST":
        add_post_res = UserProfile.add_post(request)
        data['add_post'] = add_post_res

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def get_posts(request):
    data = {}
    if request.method == "POST":
        get_posts_res = UserProfile.get_posts(request)
        data['get_posts'] = get_posts_res

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def like_post(request):
    data = {}
    if request.method == "POST":
        like_post_res = UserProfile.like_post(request)
        data['like_post'] = like_post_res

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def add_comment(request):
    data = {}
    if request.method == "POST":
        add_comment_res = UserProfile.add_comment(request)
        data['add_comment'] = add_comment_res

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def get_comments(request):
    data = {}
    if request.method == "POST":
        get_comments_res = UserProfile.get_comments(request)
        data['get_comments'] = get_comments_res

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def change_password(request):
    data = {}
    if request.method == "POST":
        change_password_res = UserProfile.change_password(request)
        data['change_password'] = change_password_res

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def toggle_bookmark(request):
    data = {}
    if request.method == "POST":
        toggle_bookmark_res = UserProfile.toggle_bookmark(request)
        data['toggle_bookmark'] = toggle_bookmark_res

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def get_bookmarks(request):
    data = {}
    if request.method == "POST":
        get_bookmarks_res = UserProfile.get_bookmarks(request)
        data['get_bookmarks'] = get_bookmarks_res

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def update_profile(request):
    data = {}
    if request.method == "POST":
        update_profile_res = UserProfile.update_profile(request)
        data['update_profile'] = update_profile_res

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def submit_quiz(request):
    data = {}
    if request.method == "POST":
        submit_quiz_res = UserProfile.submit_quiz(request)
        data['submit_quiz'] = submit_quiz_res

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def add_feedback(request):
    data = {}
    if request.method == "POST":
        add_feedback_res = UserProfile.add_feedback(request)
        data['add_feedback'] = add_feedback_res

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def get_batch_students(request):
    data = {}
    if request.method == "POST":
        get_batch_students_res = UserProfile.get_batch_students(request)
        data['get_batch_students'] = get_batch_students_res

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def get_admin_counts(request):
    data = {}
    if request.method == "POST":
        get_admin_counts_res = UserProfile.get_admin_counts(request)
        data['get_admin_counts'] = get_admin_counts_res

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def get_notifications(request):
    data = {}
    if request.method == "POST":
        get_notifications_res = UserProfile.get_notifications(request)
        data['get_notifications'] = get_notifications_res

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def read_notification(request):
    data = {}
    if request.method == "POST":
        read_notification_res = UserProfile.read_notification(request)
        data['read_notification'] = read_notification_res

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def delete_all_notifications(request):
    data = {}
    if request.method == "POST":
        delete_all_notifications_res = UserProfile.delete_all_notifications(request)
        data['delete_all_notifications'] = delete_all_notifications_res

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def set_version(request):
    data = {}
    if request.method == "POST":
        set_version_res = UserProfile.set_version(request)
        data['set_version'] = set_version_res

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def get_student_quiz_list(request):
    data = {}
    if request.method == "POST":
        data['get_student_quiz_list'] = UserProfile.get_student_quiz_list(request)

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def get_dashboard_count(request):
    data = {}
    if request.method == "POST":
        data['get_dashboard_count'] = UserProfile.get_dashboard_count(request)

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def get_quiz_questions(request):
    data = {}
    if request.method == "POST":
        data['get_quiz_questions'] = UserProfile.get_quiz_questions(request)

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def submit_assignment(request):
    data = {}
    if request.method == "POST":
        data['submit_assignment'] = UserProfile.submit_assignment(request)

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def get_student_assign_list(request):
    data = {}
    if request.method == "POST":
        data['get_student_assign_list'] = UserProfile.get_student_assign_list(request)

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def start_assignment(request):
    data = {}
    if request.method == "POST":
        data['start_assignment'] = UserProfile.start_assignment(request)

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def get_application_list(request):
    data = {}
    if request.method == "POST":
        data['get_application_list'] = UserProfile.get_application_list(request)

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def submit_application(request):
    data = {}
    if request.method == "POST":
        data['submit_application'] = UserProfile.submit_application(request)

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def view_quiz_answers(request):
    data = {}
    if request.method == "POST":
        data['view_quiz_answers'] = UserProfile.view_quiz_answers(request)

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def view_app_answers(request):
    data = {}
    if request.method == "POST":
        data['view_app_answers'] = UserProfile.view_app_answers(request)

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def view_assignment_ans(request):
    data = {}
    if request.method == "POST":
        data['view_assignment_ans'] = UserProfile.view_assignment_ans(request)

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def get_leader_board_ranks(request):
    data = {}
    if request.method == "POST":
        data['get_leader_board_ranks'] = UserProfile.get_leader_board_ranks(request)

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def get_badge_list(request):
    data = {}
    if request.method == "POST":
        data['get_badge_list'] = UserProfile.get_badge_list(request)

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def update_student_badges(request):
    data = {}
    if request.method == "POST":
        data['update_student_badges'] = UserProfile.update_student_badges(request)

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def boost_me_info(request):
    data = {}
    if request.method == "POST":
        data['boost_me_info'] = UserProfile.boost_me_info(request)

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def logout(request):
    data = {}
    if request.method == "POST":
        data['logout'] = UserProfile.logout(request)

    return HttpResponse(json.dumps(data), content_type='application/json')


#########
# Admin #
#########


@csrf_exempt
def ranking_graph(request, var):
    data = {}
    # if request.method == "POST":
    get_ranking_graph_res = UserProfile.get_ranking_graph(request, var)
    data['get_ranking_graph'] = get_ranking_graph_res

    # return HttpResponse(json.dumps(data), content_type='application/json')

    if get_ranking_graph_res['data'] == 'fail':
        return render(request, "ranking_graph/graph_error.html", {})
    else:
        return render(
            request,
            "ranking_graph/ranking_graph.html",
            {"ranking_list": json.dumps(get_ranking_graph_res['data'])})


@csrf_exempt
def get_all_batches(request):
    data = {}
    if request.method == "POST":
        if request.user.is_authenticated:
            get_all_batches_res = UserProfile.get_all_batches()
            data['get_all_batches'] = get_all_batches_res
        else:
            data['get_all_batches'] = {
                'message': 'Not logged in',
                'status': 'fail'
            }

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def create_quiz(request):
    data = {}
    if request.method == "POST":
        if request.user.is_authenticated:
            create_quiz_res = UserProfile.create_quiz(request)
            data['create_quiz'] = create_quiz_res
        else:
            data['get_all_batches'] = {
                'message': 'Not logged in',
                'status': 'fail'
            }

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def add_batch(request):
    data = {}
    if request.method == "POST":
        if request.user.is_authenticated:
            add_batch_res = UserProfile.add_batch(request)
            data['add_batch'] = add_batch_res
        else:
            data['get_all_batches'] = {
                'message': 'Not logged in',
                'status': 'fail'
            }

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def update_batch(request):
    data = {}
    if request.method == "POST":
        if request.user.is_authenticated:
            update_batch_res = UserProfile.update_batch(request)
            data['update_batch'] = update_batch_res
        else:
            data['get_all_batches'] = {
                'message': 'Not logged in',
                'status': 'fail'
            }

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def delete_batch(request):
    data = {}
    if request.method == "POST":
        if request.user.is_authenticated:
            delete_batch_res = UserProfile.delete_batch(request)
            data['delete_batch'] = delete_batch_res
        else:
            data['get_all_batches'] = {
                'message': 'Not logged in',
                'status': 'fail'
            }

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def get_quiz_by_batch_admin(request):
    data = {}
    if request.method == "POST":
        if request.user.is_authenticated:
            get_quiz_by_batch_admin_res = UserProfile.get_quiz_by_batch_admin(request)
            data['get_quiz_by_batch_admin'] = get_quiz_by_batch_admin_res
        else:
            data['get_all_batches'] = {
                'message': 'Not logged in',
                'status': 'fail'
            }

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def get_question_by_quiz_admin(request):
    data = {}
    if request.method == "POST":
        if request.user.is_authenticated:
            get_question_by_quiz_admin_res = UserProfile.get_question_by_quiz_admin(request)
            data['get_question_by_quiz_admin'] = get_question_by_quiz_admin_res
        else:
            data['get_all_batches'] = {
                'message': 'Not logged in',
                'status': 'fail'
            }

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def submit_quiz_review(request):
    data = {}
    if request.method == "POST":
        if request.user.is_authenticated:
            submit_quiz_review_res = UserProfile.submit_quiz_review(request)
            data['submit_quiz_review'] = submit_quiz_review_res
        else:
            data['get_all_batches'] = {
                'message': 'Not logged in',
                'status': 'fail'
            }

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def get_students(request):
    data = {}
    if request.method == "POST":
        if request.user.is_authenticated:
            get_students_res = UserProfile.get_students()
            data['get_students'] = get_students_res
        else:
            data['get_students'] = {
                'message': 'Not logged in',
                'status': 'fail'
            }

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def edit_student(request):
    data = {}
    if request.method == "POST":
        if request.user.is_authenticated:
            edit_student_res = UserProfile.edit_student(request)
            data['edit_student'] = edit_student_res
        else:
            data['edit_student'] = {
                'message': 'Not logged in',
                'status': 'fail'
            }

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def add_student(request):
    data = {}
    if request.method == "POST":
        if request.user.is_authenticated:
            add_student_res = UserProfile.add_student(request)
            data['add_student'] = add_student_res
        else:
            data['add_student'] = {
                'message': 'Not logged in',
                'status': 'fail'
            }

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def delete_student(request):
    data = {}
    if request.method == "POST":
        if request.user.is_authenticated:
            delete_student_res = UserProfile.delete_student(request)
            data['delete_student'] = delete_student_res
        else:
            data['delete_student'] = {
                'message': 'Not logged in',
                'status': 'fail'
            }

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def admin_get_posts(request):
    data = {}
    if request.method == "POST":
        if request.user.is_authenticated:
            data['admin_get_posts'] = UserProfile.admin_get_posts()
        else:
            data['admin_get_posts'] = {
                'message': 'Not logged in',
                'status': 'fail'
            }

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def admin_add_post(request):
    data = {}
    if request.method == "POST":
        if request.user.is_authenticated:
            data['admin_add_post'] = UserProfile.admin_add_post(request)
        else:
            data['admin_add_post'] = {
                'message': 'Not logged in',
                'status': 'fail'
            }

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def admin_udpate_post(request):
    data = {}
    if request.method == "POST":
        if request.user.is_authenticated:
            data['admin_udpate_post'] = UserProfile.admin_udpate_post(request)
        else:
            data['admin_udpate_post'] = {
                'message': 'Not logged in',
                'status': 'fail'
            }

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def admin_delete_post(request):
    data = {}
    if request.method == "POST":
        if request.user.is_authenticated:
            data['admin_delete_post'] = UserProfile.admin_delete_post(request)
        else:
            data['admin_delete_post'] = {
                'message': 'Not logged in',
                'status': 'fail'
            }

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def admin_get_assign_ans(request):
    data = {}
    if request.method == "POST":
        if request.user.is_authenticated:
            data['admin_get_assign_ans'] = UserProfile.admin_get_assign_ans(request)
        else:
            data['admin_get_assign_ans'] = {
                'message': 'Not logged in',
                'status': 'fail'
            }

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def admin_review_assign(request):
    data = {}
    if request.method == "POST":
        if request.user.is_authenticated:
            data['admin_review_assign'] = UserProfile.admin_review_assign(request)
        else:
            data['admin_review_assign'] = {
                'message': 'Not logged in',
                'status': 'fail'
            }

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def admin_get_topics(request):
    data = {}
    if request.method == "POST":
        if request.user.is_authenticated:
            data['admin_get_topics'] = UserProfile.admin_get_topics(request)
        else:
            data['admin_get_topics'] = {
                'message': 'Not logged in',
                'status': 'fail'
            }

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def admin_get_appls(request):
    data = {}
    if request.method == "POST":
        if request.user.is_authenticated:
            data['admin_get_appls'] = UserProfile.admin_get_appls(request)
        else:
            data['admin_get_appls'] = {
                'message': 'Not logged in',
                'status': 'fail'
            }

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def admin_review_application(request):
    data = {}
    if request.method == "POST":
        if request.user.is_authenticated:
            data['admin_review_application'] = UserProfile.admin_review_application(request)
        else:
            data['admin_review_application'] = {
                'message': 'Not logged in',
                'status': 'fail'
            }

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def admin_batch_performance(request):
    data = {}
    if request.method == "POST":
        if request.user.is_authenticated:
            data['admin_batch_performance'] = UserProfile.admin_batch_performance(request)
        else:
            data['admin_review_application'] = {
                'message': 'Not logged in',
                'status': 'fail'
            }

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def get_quiz_quest_to_choose(request):
    data = {}
    if request.method == "POST":
        if request.user.is_authenticated:
            data['get_quiz_quest_to_choose'] = UserProfile.get_quiz_quest_to_choose(request)
        else:
            data['get_quiz_quest_to_choose'] = {
                'message': 'Not logged in',
                'status': 'fail'
            }

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def admin_view_badges(request):
    data = {}
    if request.method == "POST":
        if request.user.is_authenticated:
            data['admin_view_badges'] = UserProfile.admin_view_badges(request)
        else:
            data['admin_view_badges'] = {
                'message': 'Not logged in',
                'status': 'fail'
            }

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def admin_add_badge(request):
    data = {}
    if request.method == "POST":
        if request.user.is_authenticated:
            data['admin_add_badge'] = UserProfile.admin_add_badge(request)
        else:
            data['admin_add_badge'] = {
                'message': 'Not logged in',
                'status': 'fail'
            }

    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def admin_login(request):
    data = {'admin_get_posts': UserProfile.admin_login(request)}
    return HttpResponse(json.dumps(data), content_type='application/json')


@csrf_exempt
def share_post(request, var):
    data = {}
    # if request.method == "POST":
    share_post_res = UserProfile.share_post(request, var)
    data['share_post'] = share_post_res

    # return HttpResponse(json.dumps(data), content_type='application/json')

    if share_post_res['data'] == 'fail':
        return render(request, "share_post/share_post.html", {})
    else:
        return render(
            request,
            "share_post/share_post.html",
            {"share_post": share_post_res['data']})
