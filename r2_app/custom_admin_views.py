from django.shortcuts import render


def custom_admin_panel(request):
    if request.user.is_authenticated:
        return render(request, "custom_admin_panel/index.html", {})
    else:
        return render(request, "not_logged_in.html", {"url": "admin/login/?next=/custom_admin_panel/"})


def custom_admin_panel_about(request):
    if request.user.is_authenticated:
        return render(request, "custom_admin_panel/modules/about/about_page.html", {})
    else:
        return render(request, "not_logged_in.html", {})


def custom_admin_panel_help(request):
    if request.user.is_authenticated:
        return render(request, "custom_admin_panel/modules/help/help_page.html", {})
    else:
        return render(request, "not_logged_in.html", {})


def batch_home(request):
    if request.user.is_authenticated:
        return render(request, "custom_admin_panel/modules/batch/batch_home.html", {})
    else:
        return render(request, "not_logged_in.html", {})


def quiz_home(request):
    if request.user.is_authenticated:
        return render(request, "custom_admin_panel/modules/quiz/quiz_home.html", {})
    else:
        return render(request, "not_logged_in.html", {})


def home_page(request):
    if request.user.is_authenticated:
        return render(request, "custom_admin_panel/modules/home/home_page.html", {})
    else:
        return render(request, "not_logged_in.html", {})


def student_home(request):
    if request.user.is_authenticated:
        return render(request, "custom_admin_panel/modules/student/student_home.html", {})
    else:
        return render(request, "not_logged_in.html", {})


def new_quiz(request):
    if request.user.is_authenticated:
        return render(request, "custom_admin_panel/modules/quiz/new_quiz.html", {})
    else:
        return render(request, "not_logged_in.html", {})


def post_home(request):
    if request.user.is_authenticated:
        return render(request, "custom_admin_panel/modules/post/post_home.html", {})
    else:
        return render(request, "not_logged_in.html", {})


def review_as(request):
    if request.user.is_authenticated:
        return render(request, "custom_admin_panel/modules/assignment/review/review_as.html", {})
    else:
        return render(request, "not_logged_in.html", {})


def review_application(request):
    if request.user.is_authenticated:
        return render(request, "custom_admin_panel/modules/application/review.html", {})
    else:
        return render(request, "not_logged_in.html", {})


def batch_perf(request):
    if request.user.is_authenticated:
        return render(request, "custom_admin_panel/modules/batch/batch_perf.html", {})
    else:
        return render(request, "not_logged_in.html", {})


def view_badge(request):
    if request.user.is_authenticated:
        return render(request, "custom_admin_panel/modules/badge/badge.html", {})
    else:
        return render(request, "not_logged_in.html", {})
