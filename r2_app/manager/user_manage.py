import base64
import json
from django.views.generic import View
from r2_app.models import Like, Feedback, Post, Student, Quiz, Comment, Batch, StudentQuiz, Bookmark, \
    Question, Answer, Notification, AssignmentAnswer, Assignment, ApplicationTopic, Application, R2Settings, Badge, \
    StudentBadge
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login

from r2_app.r2_services.pushy import PushyAPI
from r2_app.r2_services.r2_data_time import R2DateTime
from datetime import datetime
import time as py_time
import smtplib as py_smtp
from PIL import Image
from io import BytesIO
from django.core.files import File
from django.utils.timezone import now
from r2.logger import log
from email.mime.multipart import MIMEMultipart
from socket import socket

MAIL_FROM_ID = 'arnold.parge@nonstopio.com'
MAIL_FROM_PASSWORD = '****'
MAIL_FROM_NAME = 'Arnold Parge'


def datetime_from_utc_to_local(utc_datetime):
    now_timestamp = py_time.time()
    offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(now_timestamp)
    return utc_datetime + offset


def r2_mail(mail_to, mail_subject, mail_body):

        try:

            # message = """From: Arnold Nonstopio <%s>
            # To: To Person <%s>
            # MIME-Version: 1.0
            # Content-type: text/html
            # Subject: %s
            #
            #
            # %s
            # """ % (MAIL_FROM_ID, mail_to, mail_subject, mail_body)

            message = """Subject: %s

            %s
            """ % (mail_subject, mail_body)

            mail_to_send = py_smtp.SMTP('smtp.gmail.com', 587)
            mail_to_send.starttls()
            mail_to_send.login(MAIL_FROM_ID, MAIL_FROM_PASSWORD)
            mail_to_send.sendmail(MAIL_FROM_ID, mail_to, message)
            mail_to_send.quit()

        except Exception as ex:
            print('Error in sending mail: %s' % ex)
            log.error('Error in sending mail: %s' % ex)


def get_student_marks(one_student, current_student):

    get_student_marks_res = {}

    try:

        total_marks = 0

        is_current_student = one_student == current_student

        all_answers = Answer.objects.filter(answer_student=one_student)

        for one_answer in all_answers:
            sub_total = one_answer.answer_seen + one_answer.answer_attempt + one_answer.answer_other_marks
            total_marks = total_marks + sub_total

    except Exception as ex:
        get_student_marks_res['message'] = 'Error in fetching quiz marks: %s' % ex
        get_student_marks_res['status'] = 'fail'
        log.error(get_student_marks_res['message'])
        return get_student_marks_res

    try:

        appli_marks = 0

        if Application.objects.filter(student=one_student).exists():

            all_applications = Application.objects.filter(student=one_student)

            for one_application in all_applications:
                app_sub_total = one_application.app_seen + one_application.app_attempt + one_application.app_other_marks
                appli_marks = appli_marks + app_sub_total

    except Exception as ex:
        get_student_marks_res['message'] = 'Error in fetching application marks: %s' % ex
        get_student_marks_res['status'] = 'fail'
        log.error(get_student_marks_res['message'])
        return get_student_marks_res

    try:

        assign_marks = 0

        if AssignmentAnswer.objects.filter(student=one_student).exists():

            all_assign = AssignmentAnswer.objects.filter(student=one_student)

            for one_assign in all_assign:
                ass_sub_total = one_assign.answer_seen + one_assign.answer_attempt + one_assign.answer_other_marks
                assign_marks = assign_marks + ass_sub_total

    except Exception as ex:
        get_student_marks_res['message'] = 'Error in fetching assignment marks: %s' % ex
        get_student_marks_res['status'] = 'fail'
        log.error(get_student_marks_res['message'])
        return get_student_marks_res

    grand_total = int(total_marks) + int(appli_marks) + int(assign_marks)

    return {
        'quiz': total_marks,
        'app': appli_marks,
        'ass': assign_marks,
        'total': grand_total,
        'status': 'success',
        'is_current_student': is_current_student
    }


def get_student_rank_reuse(student):

    user_rank = 0

    try:
        get_student_rank_reuse_res = {}

        data = []

        all_student = Student.objects.filter(student_batch_id=student.student_batch_id)

        for one_student in all_student:

            student_marks_data = get_student_marks(
                one_student=one_student,
                current_student=student
            )

            is_current_student = student_marks_data['is_current_student']

            sub_data = {
                'user_id': one_student.id,
                'user_rank': '',
                'user_points': student_marks_data['total'],
                'current_user': student_marks_data['is_current_student'],
            }

            data.append(sub_data)

            if is_current_student:
                current_student_data = sub_data

        data.sort(key=lambda x: x['user_points'], reverse=True)

        rank = 1

        for one_data in data:
            one_data['user_rank'] = rank
            rank = rank + 1

        for one_data in data:
            if one_data['user_id'] == current_student_data['user_id']:
                user_rank = one_data['user_rank']

    except Exception as ex:
        log.error('Error in get_student_rank_reuse Function: getting user rank: %s' % ex)
        get_student_rank_reuse_res['status'] = 'fail'
        get_student_rank_reuse_res['message'] = str(ex)
        return get_student_rank_reuse_res

    return {
        'status': 'success',
        'rank': user_rank
    }


R2SETTINGS_ID = 7


APPLICATION_OUT_OF = 10
ASSIGNMENT_OUT_OF = 10
QUIZ_QUESTION_OUT_OF = 5


class UserProfile(View):

    @staticmethod
    def user_details_reuse(user_to_fetch):

        data = {
            'student_picture_url': str('media/%s' % user_to_fetch.student_picture_url),
            'student_create_at': str(user_to_fetch.student_create_at),
            'student_first_name': str(user_to_fetch.student_first_name),
            'student_last_name': str(user_to_fetch.student_last_name),
            'student_batch_id': str(user_to_fetch.student_batch_id.id),
            'student_id': str(user_to_fetch.id),
            'student_email': str(user_to_fetch.student_email)
        }

        return data

    @staticmethod
    def r2_auth(username, password, request):

        r2_auth = {}

        try:
            authenticated_user = authenticate(username=username, password=password)
            if authenticated_user is not None:
                if authenticated_user.is_active:
                    auth_login(request, authenticated_user)
                    msg = 'Authentication successfully'
                    print(msg)
                    log.info(msg)
                    r2_auth['status'] = 'success'
                    r2_auth['message'] = str(msg)
                    return r2_auth
                else:
                    ex = 'Authentication fail: Inactive user'
                    print(ex)
                    log.error(ex)
                    r2_auth['status'] = 'fail'
                    r2_auth['message'] = str(ex)
                    return r2_auth
            else:
                ex = 'Authentication fail: Invalid user'
                print(ex)
                log.error(ex)
                r2_auth['status'] = 'fail'
                r2_auth['message'] = str(ex)
                return r2_auth

        except Exception as ex:
            print(ex)
            log.error(ex)
            r2_auth['status'] = 'fail'
            r2_auth['message'] = str(ex)
            return r2_auth

    @staticmethod
    def login(parameter_list):
        print('\n\nInside login API: Logging student in\n\n')
        log.info('Inside login API: Logging student in')

        login_res = {}

        try:
            req_data = json.loads(parameter_list.POST.get('data'))
        except Exception as ex:
            print('Error in login API: req_data: %s' % ex)
            log.error('Error in login API: req_data: %s' % ex)
            login_res['status'] = 'fail'
            login_res['message'] = str(ex)
            return login_res

        r2_res = UserProfile.r2_auth(username=req_data['email'], password=req_data['password'], request=parameter_list)

        if r2_res['status'] is 'success':
            logged_in_user = Student.objects.get(student_email=req_data['email'], student_password=req_data['password'])
            logged_in_user.student_device_type = req_data['device_type']
            logged_in_user.student_device_token = req_data['device_token']
            logged_in_user.save()

            login_res['data'] = UserProfile.user_details_reuse(logged_in_user)
            login_res['status'] = 'success'
            login_res['message'] = 'User Logged in successfully'

            return login_res
        else:
            return r2_res

    @staticmethod
    def logout(parameter_list):
        print('\n\nInside logout API: logging out student\n\n')
        log.info('Inside logout API: logging out student')

        logout_res = {}

        try:
            req_data = json.loads(parameter_list.POST.get('data'))

            r2_auth_res = UserProfile.r2_auth(
                username=req_data['email'],
                password=req_data['password'],
                request=parameter_list
            )

            if r2_auth_res['status'] is 'fail':
                return r2_auth_res
            else:

                current_student = Student.objects.get(student_email=req_data['email'])
                current_token = current_student.student_device_token

                all_students = Student.objects.filter(student_device_token=current_token)

                for one_student in all_students:

                    one_student.student_device_token = ''
                    one_student.save()

        except Exception as ex:
            print('Error in API logout: %s' % ex)
            log.error('Error in API logout: %s' % ex)
            logout_res['status'] = 'fail'
            logout_res['message'] = str(ex)
            return logout_res

        log.info('Student logged out successfully')
        logout_res['status'] = 'success'
        logout_res['message'] = 'Student logged out successfully'
        return logout_res

    @staticmethod
    def get_profile_info(parameter_list):
        print('\n\nInside get_profile_info API: Getting student profile info\n\n')
        log.info('Inside get_profile_info API: Getting student profile info')

        get_profile_info_res = {}

        try:
            req_data = json.loads(parameter_list.POST.get('data'))

            r2_auth_res = UserProfile.r2_auth(
                username=req_data['email'],
                password=req_data['password'],
                request=parameter_list
            )

            if r2_auth_res['status'] is 'fail':
                return r2_auth_res
            else:
                current_student = Student.objects.get(
                    student_email=req_data['email'],
                    student_password=req_data['password']
                )

                bookmark_count = 0

                all_bookmarks = Bookmark.objects.filter(bookmark_student=current_student)

                for one_bookmark in all_bookmarks:
                    if one_bookmark.bookmark_post.post_is_enabled:
                        bookmark_count = bookmark_count + 1

                data = {
                    'student_picture_url': str('media/%s' % current_student.student_picture_url),
                    'student_create_at': str(current_student.student_create_at),
                    'student_first_name': str(current_student.student_first_name),
                    'student_last_name': str(current_student.student_last_name),
                    'student_batch_id': str(current_student.student_batch_id.id),
                    'bookmark_count': str(bookmark_count),
                    'company_image': str('media/%s' % current_student.student_batch_id.batch_company_logo),
                    'student_email': str(current_student.student_email)
                }

                get_profile_info_res['data'] = data
                get_profile_info_res['status'] = 'success'
                get_profile_info_res['message'] = 'Student details fetched successfully'
                return get_profile_info_res

        except Exception as ex:
            print('Error in API get_profile_info: %s' % ex)
            log.error('Error in API get_profile_info: %s' % ex)
            get_profile_info_res['data'] = ''
            get_profile_info_res['status'] = 'fail'
            get_profile_info_res['message'] = str(ex)
            return get_profile_info_res

    @staticmethod
    def add_post(parameter_list):
        print('\n\nInside add_post API: Adding new post\n\n')
        log.info('Inside add_post API: Adding new post')

        add_post_res = {}

        try:
            req_data = json.loads(parameter_list.POST.get('data'))
        except Exception as ex:
            print('Error in add_post API: req_data: %s' % ex)
            log.error('Error in add_post API: req_data: %s' % ex)
            add_post_res['status'] = 'fail'
            add_post_res['message'] = str(ex)
            return add_post_res

        r2_res = UserProfile.r2_auth(
            username=req_data['email'],
            password=req_data['password'],
            request=parameter_list
        )

        if r2_res['status'] is 'fail':
            return r2_res
        else:
            try:
                current_user = Student.objects.get(student_email=req_data['email'])
                current_post = Post.objects.create(
                    post_user_id=current_user,
                    post_img_url='image',
                    post_has_img=req_data['has_img'],
                    post_video=req_data['video_url'],
                    post_has_video=req_data['has_video'],
                    post_text=req_data['text'],

                    posted_by=req_data['posted_by'],
                    post_batch_id=current_user.student_batch_id
                )

                current_post.save()

                try:

                    # post_image / sample / post_pic.png
                    # media/post_image/temp/post_pic.png

                    req_image = req_data['image_url']
                    req_image = req_image.replace(' ', '+')

                    im = Image.open(BytesIO(base64.b64decode(req_image)))
                    im.save('media/post_image/temp/post_pic.png', 'PNG')
                    temp_post_img = File(open('media/post_image/temp/post_pic.png', 'rb'))
                    temp_post_img.name = 'image.png'

                    current_post.post_img_url = temp_post_img

                    current_post.save()

                except Exception as ex:
                    print('Error in add_post API - saving post image: %s' % ex)
                    log.error('Error in add_post API - saving post image: %s' % ex)
                    add_post_res['msg'] = str(ex)
                    add_post_res['status'] = 'fail'
                    return add_post_res

                add_post_res['msg'] = 'Post added successfully!'
                add_post_res['status'] = 'success'
                return add_post_res

            except Exception as ex:
                print('Error in add_post API: %s' % ex)
                log.error('Error in add_post API: %s' % ex)
                add_post_res['msg'] = str(ex)
                add_post_res['status'] = 'fail'
                return add_post_res

    @staticmethod
    def get_posts(parameter_list):

        # try:
        #
        #     mail_to_send = py_smtp.SMTP('smtp.gmail.com', 587)
        #     mail_to_send.starttls()
        #     mail_to_send.login('arnold.parge@nonstopio.com', '****')
        #     mail_to_send.sendmail(
        #         'arnold.parge@nonstopio.com',
        #         'rauf.shaikh@nonstopio.com',
        #         'This is a test message,test body'
        #     )
        #     mail_to_send.quit()
        #
        # except Exception as ex:
        #     print('Error in sending mail: %s' % ex)
        #     log.error('Error in sending mail: %s' % ex)

        print('\n\nInside get_posts API: Getting all posts\n\n')
        log.info('Inside get_posts API: Getting all posts')

        get_posts_res = {}

        try:
            req_data = json.loads(parameter_list.POST.get('data'))
        except Exception as ex:
            print('Error in get_posts API: req_data: %s' % ex)
            log.error('Error in get_posts API: req_data: %s' % ex)
            get_posts_res['status'] = 'fail'
            get_posts_res['message'] = str(ex)
            return get_posts_res

        r2_auth_res = UserProfile.r2_auth(
            username=req_data['email'],
            password=req_data['password'],
            request=parameter_list
        )

        if r2_auth_res['status'] is 'success':

            data = []

            try:

                page_no = req_data['page_no']

                page_to = int(page_no) * 10

                page_from = page_to - 10

                current_user = Student.objects.get(student_email=req_data['email'])

                all_posts = Post.objects.filter(
                    post_batch_id=current_user.student_batch_id
                ).order_by('-post_created_at')[page_from:page_to]

                for one_post in all_posts:
                    if one_post.post_is_enabled:
                        like_count = Like.objects.filter(like_post=one_post).count()

                        comment_count = Comment.objects.filter(comment_post=one_post, comment_is_enabled=True).count()

                        if Like.objects.filter(like_post=one_post, like_student=current_user).exists():
                            is_liked = "1"
                        else:
                            is_liked = "0"

                        if Bookmark.objects.filter(bookmark_post=one_post, bookmark_student=current_user).exists():
                            is_bookmarked = "1"
                        else:
                            is_bookmarked = "0"

                        data.append({
                            'post_id': one_post.id,
                            # 'creator_name': '{0} {1}'.format(
                            #     one_post.post_user_id.student_first_name,
                            #     one_post.post_user_id.student_last_name
                            # ),
                            # 'creator_img': str('media/%s' % one_post.post_user_id.student_picture_url),
                            'created_at': 'posted %s' % R2DateTime.humanize_date(
                                datetime_from_utc_to_local(
                                    one_post.post_created_at
                                )
                            ),
                            'text': str(one_post.post_text).replace("<p>", "").replace("</p>", ""),
                            'has_img': str(one_post.post_has_img),
                            'img_url': str('media/%s' % one_post.post_img_url),
                            'has_video': str(one_post.post_has_video),
                            'video_url': str(one_post.post_video),
                            'like_count': str(like_count),
                            'is_liked': is_liked,
                            'comment_count': str(comment_count),
                            'is_bookmarked': is_bookmarked,
                            'title': str(one_post.post_title).replace("<p>", "").replace("</p>", "")
                        })

            except Exception as ex:
                print('Error in get_posts API: fetch posts: %s' % ex)
                log.error('Error in get_posts API: fetch posts: %s' % ex)
                get_posts_res['status'] = 'fail'
                get_posts_res['message'] = str(ex)
                return get_posts_res

            msg = 'Post successfully fetched'
            print(msg)
            log.info(msg)
            get_posts_res['status'] = 'success'
            get_posts_res['message'] = str(msg)
            get_posts_res['data'] = data
            return get_posts_res

        else:
            return r2_auth_res

    @staticmethod
    def like_post(parameter_list):
        print('\n\nInside like_post API: Liking a posts\n\n')
        log.info('Inside like_post API: Liking a posts')

        like_post_res = {}

        try:
            req_data = json.loads(parameter_list.POST.get('data'))
        except Exception as ex:
            print('Error in like_post API: req_data: %s' % ex)
            log.error('Error in like_post API: req_data: %s' % ex)
            like_post_res['status'] = 'fail'
            like_post_res['message'] = str(ex)
            return like_post_res

        r2_auth_res = UserProfile.r2_auth(
            username=req_data['email'],
            password=req_data['password'],
            request=parameter_list
        )

        if r2_auth_res['status'] is 'fail':
            return r2_auth_res
        else:
            try:

                current_user = Student.objects.get(student_email=req_data['email'])
                current_post = Post.objects.get(id=req_data['post_id'])

                if Like.objects.filter(like_student=current_user, like_post=current_post).exists():
                    Like.objects.filter(like_student=current_user, like_post=current_post).delete()
                    msg = 'Post unliked!'
                    print(msg)
                    log.info(msg)
                    like_post_res['status'] = 'success'
                    like_post_res['message'] = str(msg)
                    return like_post_res

                else:
                    Like.objects.create(
                        like_post=current_post,
                        like_student=current_user
                    ).save()

                    msg = 'Post liked!'
                    print(msg)
                    log.info(msg)
                    like_post_res['status'] = 'success'
                    like_post_res['message'] = str(msg)
                    return like_post_res

            except Exception as ex:
                print('Error in like_post API: creating like: %s' % ex)
                log.error('Error in like_post API: creating like: %s' % ex)
                like_post_res['status'] = 'fail'
                like_post_res['message'] = str(ex)
                return like_post_res

    @staticmethod
    def add_comment(parameter_list):
        print('\n\nInside add_comment API: Commenting on a posts\n\n')
        log.info('Inside add_comment API: Commenting on a posts')

        add_comment_res = {}

        try:
            req_data = json.loads(parameter_list.POST.get('data'))
        except Exception as ex:
            print('Error in add_comment API: req_data: %s' % ex)
            log.error('Error in add_comment API: req_data: %s' % ex)
            add_comment_res['status'] = 'fail'
            add_comment_res['message'] = str(ex)
            return add_comment_res

        r2_auth_res = UserProfile.r2_auth(
            username=req_data['email'],
            password=req_data['password'],
            request=parameter_list
        )

        if r2_auth_res['status'] is 'fail':
            return r2_auth_res
        else:
            try:

                current_user = Student.objects.get(student_email=req_data['email'])

                Comment.objects.create(
                    comment_post=Post.objects.get(id=req_data['post_id']),
                    comment_student=current_user,
                    comment_text=req_data['comment_text']
                ).save()

                msg = 'Comment added successfully'
                print(msg)
                log.info(msg)
                add_comment_res['status'] = 'success'
                add_comment_res['message'] = str(msg)
                return add_comment_res

            except Exception as ex:

                print('Error in add_comment API: adding comment: %s' % ex)
                log.error('Error in add_comment API: adding comment: %s' % ex)
                add_comment_res['status'] = 'fail'
                add_comment_res['message'] = str(ex)
                return add_comment_res

    @staticmethod
    def get_comments(parameter_list):
        print('\n\nInside get_comments API: Fetching post comments\n\n')
        log.info('Inside get_comments API: Fetching post comments')

        get_comments_res = {}

        data = []

        try:
            req_data = json.loads(parameter_list.POST.get('data'))
        except Exception as ex:
            print('Error in get_comments API: req_data: %s' % ex)
            log.error('Error in get_comments API: req_data: %s' % ex)
            get_comments_res['status'] = 'fail'
            get_comments_res['message'] = str(ex)
            return get_comments_res

        r2_auth_res = UserProfile.r2_auth(
            username=req_data['email'],
            password=req_data['password'],
            request=parameter_list
        )

        if r2_auth_res['status'] is 'fail':
            return r2_auth_res
        else:

            current_post = Post.objects.get(id=req_data['post_id'])
            current_user = Student.objects.get(student_email=req_data['email'], student_password=req_data['password'])

            # get_comments_res['post_creator_name'] = str('%s %s') % (
            #     current_post.post_user_id.student_first_name,
            #     current_post.post_user_id.student_last_name
            # )
            # get_comments_res['post_creator_img'] = str(current_post.post_user_id.student_picture_url)
            # get_comments_res['post_created_at'] = R2DateTime.humanize_date(
            #     datetime_from_utc_to_local(
            #         current_post.post_created_at
            #     )
            # )
            # get_comments_res['post_text'] = str(current_post.post_text)
            # get_comments_res['post_has_img'] = str(current_post.post_has_img)
            # get_comments_res['post_img_url'] = str('media/%s' % current_post.post_img_url)
            # get_comments_res['post_has_video'] = str(current_post.post_has_video)
            # get_comments_res['post_video_url'] = str(current_post.post_video)
            # get_comments_res['post_like_count'] = str(like_count)

            like_count = Like.objects.filter(like_post=current_post).count()

            comment_count = Comment.objects.filter(comment_post=current_post, comment_is_enabled=True).count()

            if Like.objects.filter(like_post=current_post, like_student=current_user).exists():
                is_liked = "1"
            else:
                is_liked = "0"

            if Bookmark.objects.filter(bookmark_post=current_post, bookmark_student=current_user).exists():
                is_bookmarked = "1"
            else:
                is_bookmarked = "0"

            data.append({
                # 'post_creator_name': str('%s %s') % (
                #     current_post.post_user_id.student_first_name,
                #     current_post.post_user_id.student_last_name
                # ),
                # 'post_creator_img': str(current_post.post_user_id.student_picture_url),
                # 'post_created_at': R2DateTime.humanize_date(
                #     datetime_from_utc_to_local(
                #         current_post.post_created_at
                #     )
                # ),
                # 'post_text': str(current_post.post_text),
                # 'post_has_img': str(current_post.post_has_img),
                # 'post_img_url': str('media/%s' % current_post.post_img_url),
                # 'post_has_video': str(current_post.post_has_video),
                # 'post_video_url': str(current_post.post_video),
                # 'post_like_count': str(like_count)

                'post_id': current_post.id,
                # 'creator_name': '{0} {1}'.format(
                #     current_post.post_user_id.student_first_name,
                #     current_post.post_user_id.student_last_name
                # ),
                # 'creator_img': str('media/%s' % current_post.post_user_id.student_picture_url),
                'created_at': 'posted %s ' % R2DateTime.humanize_date(
                    datetime_from_utc_to_local(
                        current_post.post_created_at
                    )
                ),
                'text': str(current_post.post_text).replace("<p>", "").replace("</p>", ""),
                'has_img': str(current_post.post_has_img),
                'img_url': str('media/%s' % current_post.post_img_url),
                'has_video': str(current_post.post_has_video),
                'video_url': str(current_post.post_video),
                'like_count': str(like_count),
                'is_liked': is_liked,
                'comment_count': str(comment_count),
                'is_bookmarked': is_bookmarked,
                'title': str(current_post.post_title).replace("<p>", "").replace("</p>", "")
            })

            try:

                all_comments = Comment.objects.filter(
                    comment_post=current_post
                ).order_by('comment_created_at')

                for one_comment in all_comments:
                    if one_comment.comment_is_enabled:
                        print(' Comment Time:::::::: %s' % one_comment.comment_created_at)
                        log.info(' Comment Time:::::::: %s' % one_comment.comment_created_at)
                        data.append({
                            'comment_id': one_comment.id,
                            'student_image': str('media/%s' % one_comment.comment_student.student_picture_url),
                            'student_name': '%s %s' % (
                                one_comment.comment_student.student_first_name,
                                one_comment.comment_student.student_last_name
                            ),
                            'comment_text': str(one_comment.comment_text).replace("<p>", "").replace("</p>", ""),
                            'comment_time': R2DateTime.humanize_date(
                                datetime_from_utc_to_local(
                                    one_comment.comment_created_at
                                )
                            ),
                        })

                msg = 'Comment fetched successfully'
                print(msg)
                log.info(msg)
                get_comments_res['status'] = 'success'
                get_comments_res['message'] = str(msg)
                get_comments_res['comments'] = data
                return get_comments_res

            except Exception as ex:
                print('Error in get_comments API: fetching comments: %s' % ex)
                log.error('Error in get_comments API: fetching comments: %s' % ex)
                get_comments_res['status'] = 'fail'
                get_comments_res['message'] = str(ex)
                get_comments_res['data'] = ex
                return get_comments_res

    @staticmethod
    def change_password(parameter_list):
        print('\n\nInside change_password API: Changing the password\n\n')
        log.info('Inside change_password API: Changing the password')

        change_password_res = {}

        try:
            req_data = json.loads(parameter_list.POST.get('data'))
        except Exception as ex:
            print('Error in change_password API: req_data: %s' % ex)
            log.error('Error in change_password API: req_data: %s' % ex)
            change_password_res['status'] = 'fail'
            change_password_res['message'] = str(ex)
            return change_password_res

        r2_auth_res = UserProfile.r2_auth(
            username=req_data['email'],
            password=req_data['password'],
            request=parameter_list
        )

        if r2_auth_res['status'] is 'fail':
            return r2_auth_res
        else:
            try:

                current_user = Student.objects.get(student_email=req_data['email'])
                current_user.student_password = req_data['new_password']
                current_user.save()

            except Exception as ex:

                print('Error in change_password API: updating student: %s' % ex)
                log.error('Error in change_password API: updating student: %s' % ex)
                change_password_res['status'] = 'fail'
                change_password_res['message'] = str(ex)
                return change_password_res

            try:

                auth_user = User.objects.get(username=req_data['email'])
                auth_user.set_password(req_data['new_password'])
                auth_user.save()

            except Exception as ex:

                print('Error in change_password API: updating auth user: %s' % ex)
                change_password_res['status'] = 'fail'
                change_password_res['message'] = str(ex)
                return change_password_res

        msg = 'Password changed successfully'
        print(msg)
        log.info(msg)
        change_password_res['status'] = 'success'
        change_password_res['message'] = str(msg)
        return change_password_res

    @staticmethod
    def toggle_bookmark(parameter_list):
        print('\n\nInside add_bookmark API: Adding bookmark\n\n')
        log.info('Inside add_bookmark API: Adding bookmark')

        change_password_res = {}

        try:
            req_data = json.loads(parameter_list.POST.get('data'))
        except Exception as ex:
            print('Error in add_bookmark API: req_data: %s' % ex)
            log.error('Error in add_bookmark API: req_data: %s' % ex)
            change_password_res['status'] = 'fail'
            change_password_res['message'] = str(ex)
            return change_password_res

        r2_auth_res = UserProfile.r2_auth(
            username=req_data['email'],
            password=req_data['password'],
            request=parameter_list
        )

        if r2_auth_res['status'] is 'fail':
            return r2_auth_res
        else:
            try:
                current_user = Student.objects.get(student_email=req_data['email'])

                current_bookmark = Bookmark.objects.filter(
                    bookmark_student=current_user,
                    bookmark_post=Post.objects.get(id=req_data['post_id'])
                )

                if current_bookmark.exists():
                    current_bookmark.delete()

                    msg = 'Bookmark Removed successfully'
                    print(msg)
                    log.info(msg)
                    change_password_res['status'] = 'success'
                    change_password_res['message'] = str(msg)
                    return change_password_res
                else:
                    Bookmark.objects.create(
                        bookmark_student=current_user,
                        bookmark_post=Post.objects.get(id=req_data['post_id'])
                    ).save()

                    msg = 'Bookmark Added successfully'
                    print(msg)
                    log.info(msg)
                    change_password_res['status'] = 'success'
                    change_password_res['message'] = str(msg)
                    return change_password_res

            except Exception as ex:
                print('Error in add_bookmark API: adding bookmark: %s' % ex)
                log.error('Error in add_bookmark API: adding bookmark: %s' % ex)
                change_password_res['status'] = 'fail'
                change_password_res['message'] = str(ex)
                return change_password_res

    @staticmethod
    def get_bookmarks(parameter_list):
        print('\n\nInside get_bookmarks API: Fetching bookmarks\n\n')
        log.info('Inside get_bookmarks API: Fetching bookmarks')

        get_bookmarks_res = {}

        data = []

        try:
            req_data = json.loads(parameter_list.POST.get('data'))
        except Exception as ex:
            print('Error in get_bookmarks API: req_data: %s' % ex)
            log.error('Error in get_bookmarks API: req_data: %s' % ex)
            get_bookmarks_res['status'] = 'fail'
            get_bookmarks_res['message'] = str(ex)
            return get_bookmarks_res

        r2_auth_res = UserProfile.r2_auth(
            username=req_data['email'],
            password=req_data['password'],
            request=parameter_list
        )

        if r2_auth_res['status'] is 'fail':
            return r2_auth_res
        else:

            try:

                page_no = req_data['page_no']

                page_to = int(page_no) * 10

                page_from = page_to - 10

                current_user = Student.objects.get(student_email=req_data['email'])

                all_bookmarks = Bookmark.objects.filter(bookmark_student=current_user).order_by('-bookmark_created_at')[page_from:page_to]

                for one_bookmark in all_bookmarks:

                    if one_bookmark.bookmark_post.post_is_enabled:

                        like_count = Like.objects.filter(like_post=one_bookmark.bookmark_post).count()

                        comment_count = Comment.objects.filter(comment_post=one_bookmark.bookmark_post, comment_is_enabled=True).count()

                        if Like.objects.filter(like_post=one_bookmark.bookmark_post, like_student=current_user).exists():
                            is_liked = "1"
                        else:
                            is_liked = "0"

                        if Bookmark.objects.filter(bookmark_post=one_bookmark.bookmark_post, bookmark_student=current_user).exists():
                            is_bookmarked = "1"
                        else:
                            is_bookmarked = "0"

                        data.append({
                            'post_id': one_bookmark.bookmark_post.id,
                            'created_at': 'posted %s ' % R2DateTime.humanize_date(
                                datetime_from_utc_to_local(
                                    one_bookmark.bookmark_post.post_created_at
                                )
                            ),
                            'text': one_bookmark.bookmark_post.post_text,
                            'has_img': str(one_bookmark.bookmark_post.post_has_img),
                            'img_url': str('media/%s' % one_bookmark.bookmark_post.post_img_url),
                            'has_video': str(one_bookmark.bookmark_post.post_has_video),
                            'video_url': str(one_bookmark.bookmark_post.post_video),
                            'like_count': str(like_count),
                            'is_liked': is_liked,
                            'comment_count': str(comment_count),
                            'is_bookmarked': is_bookmarked,
                            'title': one_bookmark.bookmark_post.post_title
                        })

            except Exception as ex:
                print('Error in get_bookmarks API: fetching bookmark: %s' % ex)
                log.error('Error in get_bookmarks API: fetching bookmark: %s' % ex)
                get_bookmarks_res['status'] = 'fail'
                get_bookmarks_res['message'] = str(ex)
                return get_bookmarks_res

        msg = 'Bookmark fetched successfully'
        print(msg)
        log.info(msg)
        get_bookmarks_res['status'] = 'success'
        get_bookmarks_res['message'] = str(msg)
        get_bookmarks_res['data'] = data
        return get_bookmarks_res

    @staticmethod
    def update_profile(parameter_list):
        print('\n\nInside update_profile API: Updating profile\n\n')
        log.info('Inside update_profile API: Updating profile')

        update_profile_res = {}

        try:
            req_data = json.loads(parameter_list.POST.get('data'))
        except Exception as ex:
            print('Error in update_profile API: req_data: %s' % ex)
            log.error('Error in update_profile API: req_data: %s' % ex)
            update_profile_res['status'] = 'fail'
            update_profile_res['message'] = str(ex)
            return update_profile_res

        r2_auth_res = UserProfile.r2_auth(
            username=req_data['email'],
            password=req_data['password'],
            request=parameter_list
        )

        if r2_auth_res['status'] is 'fail':
            return r2_auth_res
        else:
            try:
                current_student = Student.objects.get(student_email=req_data['email'])
                current_student.student_first_name = req_data['first_name']
                current_student.student_last_name = req_data['last_name']
                # current_student.student_picture_url = 'image'  # req_data['picture_url']
                # current_student.student_password = req_data['new_password']
            except Exception as ex:
                print('Error in update_profile API: updating student: %s' % ex)
                log.error('Error in update_profile API: updating student: %s' % ex)
                update_profile_res['status'] = 'fail'
                update_profile_res['message'] = str(ex)
                return update_profile_res

            try:
                # post_image / sample / post_pic.png
                # media/post_image/temp/post_pic.png

                req_image = req_data['picture_url']
                req_image = req_image.replace(' ', '+')

                im = Image.open(BytesIO(base64.b64decode(req_image)))
                im.save('media/student_profile_picture/temp/student_pic.png', 'PNG')
                temp_student_img = File(open('media/student_profile_picture/temp/student_pic.png', 'rb'))
                temp_student_img.name = 'image.png'

                current_student.student_picture_url = temp_student_img

            except Exception as ex:
                print('Error in update_profile API: uploading image: %s' % ex)
                log.error('Error in update_profile API: uploading image: %s' % ex)
                update_profile_res['status'] = 'fail'
                update_profile_res['message'] = str(ex)
                return update_profile_res

            try:
                auth_user = User.objects.get(username=req_data['email'])
                auth_user.first_name = req_data['first_name']
                auth_user.last_name = req_data['last_name']
                # auth_user.set_password(req_data['new_password'])

                current_student.save()
                auth_user.save()
            except Exception as ex:
                print('Error in update_profile API: updating auth user: %s' % ex)
                update_profile_res['status'] = 'fail'
                update_profile_res['message'] = str(ex)
                return update_profile_res
        msg = 'Profile updated successfully!'
        print(msg)
        log.info(msg)
        update_profile_res['status'] = 'success'
        update_profile_res['message'] = str(msg)
        return update_profile_res

    @staticmethod
    def submit_quiz(parameter_list):
        print('\n\nInside submit_quiz API: Submitting the quiz\n\n')
        log.info('Inside submit_quiz API: Submitting the quiz')

        submit_quiz_res = {}

        try:
            req_data = json.loads(parameter_list.POST.get('data'))
        except Exception as ex:
            print('Error in submit_quiz API: req_data: %s' % ex)
            log.error('Error in submit_quiz API: req_data: %s' % ex)
            submit_quiz_res['status'] = 'fail'
            submit_quiz_res['message'] = str(ex)
            return submit_quiz_res

        r2_auth_res = UserProfile.r2_auth(
            username=req_data['email'],
            password=req_data['password'],
            request=parameter_list
        )

        if r2_auth_res['status'] is 'fail':
            return r2_auth_res
        else:

            current_student = Student.objects.get(student_email=req_data['email'])

            all_answers = req_data['answers']

            if not StudentQuiz.objects.filter(
                    student=current_student,
                    quiz=Quiz.objects.get(id=req_data['quiz_id'])
            ).exists():

                StudentQuiz.objects.create(
                    student=current_student,
                    # quiz=Question.objects.get(id=all_answers[0]['question_id']).question_quiz,
                    quiz=Quiz.objects.get(id=req_data['quiz_id']),
                    quiz_rating=req_data['quiz_rating']
                ).save()

                for one_answer in all_answers:

                    current_question = Question.objects.get(id=one_answer['question_id'])

                    try:

                        if current_question.question_type == 'MCQ':
                            ans_status = 'Checked'
                            if one_answer['answer_text'] is current_question.question_correct_ans:
                                other_marks = 3
                            else:
                                other_marks = 0
                        else:
                            ans_status = 'Pending'
                            other_marks = 0

                    except Exception as ex:
                        print('Error in submit_quiz API: calculating marks: %s' % ex)
                        log.error('Error in submit_quiz API: calculating marks: %s' % ex)
                        submit_quiz_res['status'] = 'fail'
                        submit_quiz_res['message'] = str(ex)
                        return submit_quiz_res

                    try:

                        Answer.objects.create(
                            answer_student=current_student,
                            answer_question=current_question,
                            answer_text=one_answer['answer_text'],
                            answer_status=ans_status,
                            answer_seen=one_answer['seen'],
                            answer_attempt=one_answer['attempt'],
                            answer_other_marks=other_marks
                        ).save()

                    except Exception as ex:
                        print('Error in submit_quiz API: adding answer: %s' % ex)
                        log.error('Error in submit_quiz API: adding answer: %s' % ex)
                        submit_quiz_res['status'] = 'fail'
                        submit_quiz_res['message'] = str(ex)
                        return submit_quiz_res

                msg = 'Quiz submitted successfully'
                print(msg)
                log.info(msg)
                submit_quiz_res['status'] = 'success'
                submit_quiz_res['message'] = str(msg)
                return submit_quiz_res
            else:
                msg = 'Quiz already exist.'
                print(msg)
                log.info(msg)
                submit_quiz_res['status'] = 'fail'
                submit_quiz_res['message'] = str(msg)
                return submit_quiz_res

    @staticmethod
    def add_feedback(parameter_list):
        print('\n\nInside add_feedback API: Adding feedback\n\n')
        log.info('Inside add_feedback API: Adding feedback')

        add_feedback_res = {}

        try:
            req_data = json.loads(parameter_list.POST.get('data'))
        except Exception as ex:
            print('Error in add_feedback API: req_data: %s' % ex)
            log.error('Error in add_feedback API: req_data: %s' % ex)
            add_feedback_res['status'] = 'fail'
            add_feedback_res['message'] = str(ex)
            return add_feedback_res

        r2_auth_res = UserProfile.r2_auth(
            username=req_data['email'],
            password=req_data['password'],
            request=parameter_list
        )

        if r2_auth_res['status'] is 'fail':
            return r2_auth_res
        else:

            try:

                Feedback.objects.create(
                    feedback_student=Student.objects.get(student_email=req_data['email']),
                    feedback_text=req_data['text']
                ).save()

                msg = 'Feedback added successfully'
                print(msg)
                log.info(msg)
                add_feedback_res['status'] = 'success'
                add_feedback_res['message'] = str(msg)
                return add_feedback_res

            except Exception as ex:
                print('Error in add_feedback API: adding feedback: %s' % ex)
                log.error('Error in add_feedback API: adding feedback: %s' % ex)
                add_feedback_res['status'] = 'fail'
                add_feedback_res['message'] = str(ex)
                return add_feedback_res

    @staticmethod
    def get_batch_students(parameter_list):
        print('\n\nInside get_batch_students API: Creating new Quiz\n\n')
        log.info('Inside get_batch_students API: Creating new Quiz')

        get_batch_students_res = {}

        data = []

        try:
            req_data = json.loads(parameter_list.POST.get('data'))
        except Exception as ex:
            print('Error in get_batch_students API: req_data: %s' % ex)
            log.error('Error in get_batch_students API: req_data: %s' % ex)
            get_batch_students_res['status'] = 'fail'
            get_batch_students_res['message'] = str(ex)
            return get_batch_students_res

        r2_auth_res = UserProfile.r2_auth(
            username=req_data['email'],
            password=req_data['password'],
            request=parameter_list
        )

        if r2_auth_res['status'] is 'fail':
            return r2_auth_res
        else:
            try:
                current_student = Student.objects.get(student_email=req_data['email'])

                all_students = Student.objects.filter(student_batch_id=current_student.student_batch_id).order_by('student_first_name')

                for one_student in all_students:
                    data.append(UserProfile.user_details_reuse(one_student))

                msg = 'Students fetched successfully'
                print(msg)
                log.info(msg)
                get_batch_students_res['data'] = data
                get_batch_students_res['batch_name'] = current_student.student_batch_id.batch_name
                get_batch_students_res['company_name'] = current_student.student_batch_id.batch_company_name
                get_batch_students_res['status'] = 'success'
                get_batch_students_res['message'] = str(msg)
                return get_batch_students_res
            except Exception as ex:
                print('Error in get_batch_students API: getting students: %s' % ex)
                log.error('Error in get_batch_students API: getting students: %s' % ex)
                get_batch_students_res['status'] = 'fail'
                get_batch_students_res['message'] = str(ex)
                return get_batch_students_res

    @staticmethod
    def get_notifications(parameter_list):
        print('\n\nInside get_notifications API: Fetching notifications\n\n')
        log.info('Inside get_notifications API: Fetching notifications')

        get_notifications_res = {}

        data = []

        try:
            req_data = json.loads(parameter_list.POST.get('data'))
        except Exception as ex:
            print('Error in get_notifications API: req_data: %s' % ex)
            log.error('Error in get_notifications API: req_data: %s' % ex)
            get_notifications_res['status'] = 'fail'
            get_notifications_res['message'] = str(ex)
            return get_notifications_res

        r2_auth_res = UserProfile.r2_auth(
            username=req_data['email'],
            password=req_data['password'],
            request=parameter_list
        )

        if r2_auth_res['status'] is 'fail':
            return r2_auth_res
        else:

            try:

                current_student = Student.objects.get(
                    student_email=req_data['email'],
                    student_password=req_data['password']
                )

                all_notifications = Notification.objects.filter(notif_student=current_student).order_by('-notif_created_at')

                unread_count = Notification.objects.filter(notif_student=current_student, notif_read=False).count()

                for one_notification in all_notifications:

                    if one_notification.notif_type == 'Student':
                        notif_img = 'media/%s' % one_notification.notifier_student.student_picture_url
                    else:
                        notif_img = 'media/admin/admin.png'

                    redirect_id = ''

                    if one_notification.redirect_to == 'Post' or one_notification.redirect_to == 'Comment':
                        redirect_id = one_notification.notif_post.id
                    elif one_notification.redirect_to == 'Quiz':
                        redirect_id = one_notification.notif_quiz.id
                    # elif one_notification.redirect_to == 'Application':
                    #     redirect_id = one_notification.notif_quiz.id
                    # elif one_notification.redirect_to == 'Assignment':
                    #     redirect_id = one_notification.notif_quiz.id

                    data.append({
                        'notif_img': notif_img,
                        'date': '%s' % R2DateTime.humanize_date(
                            datetime_from_utc_to_local(
                                one_notification.notif_created_at
                            )
                        ),
                        'redirect_to': one_notification.redirect_to,
                        'redirect_id': redirect_id,
                        'read': str(one_notification.notif_read),
                        'text': str(one_notification.notif_text).replace("<p>", "").replace("</p>", ""),
                        'notif_id': one_notification.id
                    })

                msg = 'Notification fetched successfully'
                print(msg)
                log.info(msg)
                get_notifications_res['status'] = 'success'
                get_notifications_res['data'] = data
                get_notifications_res['count'] = all_notifications.count()
                get_notifications_res['unread_count'] = unread_count
                get_notifications_res['message'] = str(msg)
                return get_notifications_res

            except Exception as ex:
                print('Error in get_notifications API: fetching notification: %s' % ex)
                log.error('Error in get_notifications API: fetching notification: %s' % ex)
                get_notifications_res['status'] = 'fail'
                get_notifications_res['message'] = str(ex)
                return get_notifications_res

    @staticmethod
    def read_notification(parameter_list):
        print('\n\nInside read_notification API: Marking notification as read\n\n')
        log.info('Inside read_notification API: Marking notification as read')

        get_notifications_res = {}

        try:
            req_data = json.loads(parameter_list.POST.get('data'))
        except Exception as ex:
            print('Error in read_notification API: req_data: %s' % ex)
            log.error('Error in read_notification API: req_data: %s' % ex)
            get_notifications_res['status'] = 'fail'
            get_notifications_res['message'] = str(ex)
            return get_notifications_res

        r2_auth_res = UserProfile.r2_auth(
            username=req_data['email'],
            password=req_data['password'],
            request=parameter_list
        )

        if r2_auth_res['status'] is 'fail':
            return r2_auth_res
        else:

            try:

                current_notif = Notification.objects.get(id=req_data['notif_id'])
                current_notif.notif_read = True
                current_notif.save()

                msg = 'Notification marked as read successfully'
                print(msg)
                log.info(msg)
                get_notifications_res['status'] = 'success'
                get_notifications_res['message'] = str(msg)
                return get_notifications_res

            except Exception as ex:
                print('Error in read_notification API: Marking notification as read: %s' % ex)
                log.error('Error in read_notification API: Marking notification as read: %s' % ex)
                get_notifications_res['status'] = 'fail'
                get_notifications_res['message'] = str(ex)
                return get_notifications_res

    @staticmethod
    def delete_all_notifications(parameter_list):

        print('\n\nInside delete_all_notifications API: Deleting all notifications\n\n')
        log.info('Inside delete_all_notifications API: Deleting all notifications')

        delete_all_notifications_res = {}

        try:
            req_data = json.loads(parameter_list.POST.get('data'))
        except Exception as ex:
            print('Error in delete_all_notifications API: req_data: %s' % ex)
            log.error('Error in delete_all_notifications API: req_data: %s' % ex)
            delete_all_notifications_res['status'] = 'fail'
            delete_all_notifications_res['message'] = str(ex)
            return delete_all_notifications_res

        r2_auth_res = UserProfile.r2_auth(
            username=req_data['email'],
            password=req_data['password'],
            request=parameter_list
        )

        if r2_auth_res['status'] is 'fail':
            return r2_auth_res
        else:

            try:

                current_student = Student.objects.get(student_email=req_data['email'], student_password=req_data['password'])

                Notification.objects.filter(notif_student=current_student).delete()
                # all_notifications.delete()
                # all_notifications.save()

                msg = 'All notifications deleted successfully'
                print(msg)
                log.info(msg)
                delete_all_notifications_res['status'] = 'success'
                delete_all_notifications_res['message'] = str(msg)
                return delete_all_notifications_res

            except Exception as ex:
                print('Error in delete_all_notifications API: deleting notifications: %s' % ex)
                log.error('Error in delete_all_notifications API: deleting notifications: %s' % ex)
                delete_all_notifications_res['status'] = 'fail'
                delete_all_notifications_res['message'] = str(ex)
                return delete_all_notifications_res

    @staticmethod
    def get_ranking_graph(parameter_list, student_id):

        log.info('Inside get_ranking_graph API: Getting data for ranking graph')

        get_ranking_graph_res = {}

        data = []

        try:

            current_student = Student.objects.get(id=int(student_id))
            current_student_data = {}
            current_batch = current_student.student_batch_id

            all_student = Student.objects.filter(student_batch_id=current_batch)

            for one_student in all_student:

                student_marks_data = get_student_marks(
                    one_student=one_student,
                    current_student=current_student
                )

                if student_marks_data['status'] is 'fail':
                    return student_marks_data

                sub_data = {
                    'user_id': one_student.id,
                    'user_name': '%s' % (
                        one_student.student_first_name
                    ),
                    'user_rank': '',
                    'user_points': student_marks_data['total'],
                    'current_user': student_marks_data['is_current_student'],
                    'user_img': str('media/%s' % one_student.student_picture_url),
                }

                data.append(sub_data)

                if student_marks_data['is_current_student']:
                    current_student_data = sub_data

            data.sort(key=lambda x: x['user_points'], reverse=True)

            rank = 1

            for one_data in data:
                one_data['user_rank'] = rank
                rank = rank + 1

            data = data[:3]

            student_in_top_3 = False

            for one_data in data:
                if one_data == current_student_data:
                    student_in_top_3 = True

            if student_in_top_3 is False:
                data.append(current_student_data)

            print('\n\n\n\n\n graph data: ')
            print(data)
            get_ranking_graph_res['data'] = data
            return get_ranking_graph_res

        except Exception as ex:
            get_ranking_graph_res['data'] = 'fail'
            get_ranking_graph_res['message'] = ex
            return get_ranking_graph_res

    @staticmethod
    def set_version(parameter_list):
        log.info('Inside set_set_version API: Deleting all notifications')

        set_version_res = {}

        try:
            req_data = json.loads(parameter_list.POST.get('data'))
        except Exception as ex:
            log.error('Error in set_set_version API: req_data: %s' % ex)
            set_version_res['status'] = 'fail'
            set_version_res['message'] = str(ex)
            return set_version_res

        r2_auth_res = UserProfile.r2_auth(
            username=req_data['email'],
            password=req_data['password'],
            request=parameter_list
        )

        if r2_auth_res['status'] is 'fail':
            return r2_auth_res
        else:

            try:

                current_student = Student.objects.get(student_email=req_data['email'], student_password=req_data['password'])

                current_student.student_os_version = req_data['os_version']
                current_student.student_app_version = req_data['app_version']
                current_student.save()

                msg = 'OS version saved successfully'
                log.error(msg)
                set_version_res['status'] = 'success'
                set_version_res['message'] = str(msg)
                return set_version_res

            except Exception as ex:
                log.error('Error in set_set_version API: req_data: %s' % ex)
                set_version_res['status'] = 'fail'
                set_version_res['message'] = str(ex)
                return set_version_res

    @staticmethod
    def get_student_quiz_list(parameter_list):
        log.info('Inside get_student_quiz_list API: Fetching quiz list')

        get_student_quiz_list_res = {}

        data = []

        try:
            req_data = json.loads(parameter_list.POST.get('data'))
        except Exception as ex:
            log.error('Error in get_student_quiz_list API: req_data: %s' % ex)
            get_student_quiz_list_res['status'] = 'fail'
            get_student_quiz_list_res['message'] = str(ex)
            return get_student_quiz_list_res

        r2_auth_res = UserProfile.r2_auth(
            username=req_data['email'],
            password=req_data['password'],
            request=parameter_list
        )

        if r2_auth_res['status'] is 'fail':
            return r2_auth_res
        else:

            try:

                current_student = Student.objects.get(student_email=req_data['email'], student_password=req_data['password'])

                all_quiz = Quiz.objects.filter(quiz_batch=current_student.student_batch_id).order_by('-quiz_created_at')

                for one_quiz in all_quiz:

                    quiz_status = ''

                    tot_score = 0

                    if not StudentQuiz.objects.filter(quiz=one_quiz, student=current_student).exists():
                        quiz_status = 'take_now'
                    else:
                        all_questions = Question.objects.filter(question_quiz=one_quiz)

                        for one_question in all_questions:

                            current_answer = Answer.objects.get(answer_question=one_question, answer_student=current_student)

                            if current_answer.answer_status == 'Pending':
                                quiz_status = 'pending_review'
                            tot_score = tot_score + current_answer.answer_seen + current_answer.answer_attempt + current_answer.answer_other_marks

                    if quiz_status == '':
                        quiz_status = 'submitted'

                    if one_quiz.quiz_published:
                        data.append({
                            'quiz_id': str(one_quiz.id),
                            'quiz_desc': str(one_quiz.quiz_desc),
                            'quiz_created_at': '%s' % R2DateTime.humanize_date(
                                datetime_from_utc_to_local(
                                    one_quiz.quiz_created_at
                                )
                            ),
                            'quiz_status': str(quiz_status),
                            'score': str(tot_score)
                        })

                msg = 'Quiz fetched successfully'
                log.error(msg)
                get_student_quiz_list_res['data'] = data
                get_student_quiz_list_res['status'] = 'success'
                get_student_quiz_list_res['message'] = str(msg)
                return get_student_quiz_list_res

            except Exception as ex:
                log.error('Error in get_student_batch_list API: Fetching quiz list: %s' % ex)
                get_student_quiz_list_res['status'] = 'fail'
                get_student_quiz_list_res['message'] = str(ex)
                return get_student_quiz_list_res

    @staticmethod
    def get_dashboard_count(parameter_list):

        log.info('Inside get_dashboard_count API: Gettting counts')

        get_dashboard_count_res = {}

        data = []

        user_rank = 0

        try:
            req_data = json.loads(parameter_list.POST.get('data'))
        except Exception as ex:
            log.error('Error in get_dashboard_count API: req_data: %s' % ex)
            get_dashboard_count_res['status'] = 'fail'
            get_dashboard_count_res['message'] = str(ex)
            return get_dashboard_count_res

        r2_auth_res = UserProfile.r2_auth(
            username=req_data['email'],
            password=req_data['password'],
            request=parameter_list
        )

        if r2_auth_res['status'] is 'fail':
            return r2_auth_res
        else:

            try:
                current_student = Student.objects.get(student_email=req_data['email'], student_password=req_data['password'])

                total_quiz = Quiz.objects.filter(quiz_batch=current_student.student_batch_id).count()

                submitted_quiz = StudentQuiz.objects.filter(student=current_student).count()

                pending_quiz = total_quiz - submitted_quiz

                try:
                    current_student_data = {}

                    all_student = Student.objects.filter(student_batch_id=current_student.student_batch_id)

                    for one_student in all_student:

                        student_marks_data = get_student_marks(
                            one_student=one_student,
                            current_student=current_student
                        )

                        is_current_student = student_marks_data['is_current_student']

                        sub_data = {
                            'user_id': one_student.id,
                            'user_rank': '',
                            'user_points': student_marks_data['total'],
                            'current_user': student_marks_data['is_current_student'],
                        }

                        data.append(sub_data)

                        if is_current_student:
                            current_student_data = sub_data

                    data.sort(key=lambda x: x['user_points'], reverse=True)

                    rank = 1

                    for one_data in data:
                        one_data['user_rank'] = rank
                        rank = rank + 1

                    for one_data in data:
                        if one_data['user_id'] == current_student_data['user_id']:
                            user_rank = one_data['user_rank']

                except Exception as ex:
                    log.error('Error in get_dashboard_count API: getting user rank: %s' % ex)
                    get_dashboard_count_res['status'] = 'fail'
                    get_dashboard_count_res['message'] = str(ex)
                    return get_dashboard_count_res

                feed_count = 0  # Post.objects.filter(post_created_at=datetime.now().date()).count()

                all_posts = Post.objects.filter()

                for one_post in all_posts:
                    if one_post.post_created_at.date() == datetime.now().date():
                        feed_count = feed_count + 1

                print('\n\n\ndatetime.now().date(): %s \n\n\n' % datetime.now().date())

                # user_rank = 1.1

                if int(user_rank) % 100 == 11 or int(user_rank) % 100 == 12 or int(user_rank) % 100 == 13:
                    prefix = 'th'
                elif int(user_rank) % 10 == 1:
                    prefix = 'st'
                elif int(user_rank) % 10 == 2:
                    prefix = 'nd'
                elif int(user_rank) % 10 == 3:
                    prefix = 'rd'
                else:
                    prefix = 'th'

                try:
                    all_ass = Assignment.objects.filter(batch=current_student.student_batch_id)
                    total_ass = all_ass.count()
                    submitted_ass = 0

                    for one_ass in all_ass:
                        if AssignmentAnswer.objects.filter(assignment=one_ass, student=current_student).exists():
                            submitted_ass = submitted_ass + 1

                    pending_ass = total_ass - submitted_ass

                except Exception as ex:
                    log.error('Error in get_dashboard_count API: getting assignmnet counts: %s' % ex)
                    get_dashboard_count_res['status'] = 'fail'
                    get_dashboard_count_res['message'] = str(ex)
                    return get_dashboard_count_res

                all_topics = ApplicationTopic.objects.filter(batch=current_student.student_batch_id)
                total_topic = all_topics.count()
                submitted_application = 0

                for one_topic in all_topics:
                    if Application.objects.filter(topic=one_topic, student=current_student).exists():
                        submitted_application = submitted_application + 1

                pending_application = total_topic - submitted_application

                msg = 'Counts fetched successfully'
                log.info(msg)
                get_dashboard_count_res['status'] = 'success'
                get_dashboard_count_res['message'] = str(msg)
                get_dashboard_count_res['current_version'] = R2Settings.objects.get(id=R2SETTINGS_ID).android_current_version
                get_dashboard_count_res['pending_quiz'] = str(pending_quiz)
                get_dashboard_count_res['rank'] = '%s%s' % (str(user_rank), prefix)
                get_dashboard_count_res['feed_count'] = str(feed_count)
                get_dashboard_count_res['pending_assignments'] = str(pending_ass)
                get_dashboard_count_res['pending_application'] = str(pending_application)
                return get_dashboard_count_res

            except Exception as ex:
                log.error('Error in get_dashboard_count API: getting counts: %s' % ex)
                get_dashboard_count_res['status'] = 'fail'
                get_dashboard_count_res['message'] = str(ex)
                return get_dashboard_count_res

    @staticmethod
    def get_quiz_questions(parameter_list):
        log.info('Inside get_quiz_questions API: fetching questions')

        get_quiz_questions_res = {}

        data = []

        try:
            req_data = json.loads(parameter_list.POST.get('data'))
        except Exception as ex:
            log.error('Error in get_quiz_questions API: req_data: %s' % ex)
            get_quiz_questions_res['status'] = 'fail'
            get_quiz_questions_res['message'] = str(ex)
            return get_quiz_questions_res

        r2_auth_res = UserProfile.r2_auth(
            username=req_data['email'],
            password=req_data['password'],
            request=parameter_list
        )

        if r2_auth_res['status'] is 'fail':
            return r2_auth_res
        else:

            try:

                current_quiz = Quiz.objects.get(id=req_data['quiz_id'])

                all_question = Question.objects.filter(question_quiz=current_quiz).order_by('id')

                has_essay = False

                for one_question in all_question:
                    if one_question.question_type == 'Essay':
                        has_essay = True
                    data.append({
                        'question_id': one_question.id,
                        'question_text': one_question.question_text,
                        'question_type': one_question.question_type,
                        'op_a': one_question.question_op_a,
                        'op_b': one_question.question_op_b,
                        'op_c': one_question.question_op_c,
                        'op_d': one_question.question_op_d
                    })

                msg = 'Questions fetched successfully'
                log.error(msg)
                get_quiz_questions_res['quiz_title'] = current_quiz.quiz_desc
                get_quiz_questions_res['data'] = data
                get_quiz_questions_res['status'] = 'success'
                get_quiz_questions_res['has_essay'] = str(has_essay)
                get_quiz_questions_res['message'] = str(msg)
                return get_quiz_questions_res

            except Exception as ex:
                log.error('Error in get_quiz_questions API: fetching question: %s' % ex)
                get_quiz_questions_res['status'] = 'fail'
                get_quiz_questions_res['message'] = str(ex)
                return get_quiz_questions_res

    @staticmethod
    def submit_assignment(parameter_list):

        print('\n\nInside submit_assignment API: Submitting the assignment\n\n')
        log.info('Inside submit_assignment API: Submitting the assignment')

        submit_quiz_res = {}

        try:
            req_data = json.loads(parameter_list.POST.get('data'))
        except Exception as ex:
            print('Error in submit_assignment API: req_data: %s' % ex)
            log.error('Error in submit_assignment API: req_data: %s' % ex)
            submit_quiz_res['status'] = 'fail'
            submit_quiz_res['message'] = str(ex)
            return submit_quiz_res

        r2_auth_res = UserProfile.r2_auth(
            username=req_data['email'],
            password=req_data['password'],
            request=parameter_list
        )

        if r2_auth_res['status'] is 'fail':
            return r2_auth_res
        else:

            try:

                current_assignment = Assignment.objects.get(id=req_data['assign_id'])

                current_student = Student.objects.get(student_email=req_data['email'])

                if not AssignmentAnswer.objects.filter(
                    assignment=current_assignment,
                    student=current_student
                ).exists():

                    AssignmentAnswer.objects.create(
                        answer_text=req_data['ans_text'],
                        assignment=Assignment.objects.get(id=req_data['assign_id']),
                        student=current_student,
                        answer_seen=req_data['answer_seen'],
                        answer_attempt=req_data['answer_attempt']
                    ).save()

                    msg = 'Assignment submitted successfully'
                    print(msg)
                    log.error(msg)
                    submit_quiz_res['status'] = 'success'
                    submit_quiz_res['message'] = str(msg)
                    return submit_quiz_res

                else:

                    msg = 'Assignment already submitted'
                    print(msg)
                    log.error(msg)
                    submit_quiz_res['status'] = 'fail'
                    submit_quiz_res['message'] = str(msg)
                    return submit_quiz_res

            except Exception as ex:
                print('Error in submit_assignment API: submitting assignment: %s' % ex)
                log.error('Error in submit_assignment API: req_data: %s' % ex)
                submit_quiz_res['status'] = 'fail'
                submit_quiz_res['message'] = str(ex)
                return submit_quiz_res

    @staticmethod
    def get_student_assign_list(parameter_list):

        print('\n\nInside get_student_assign_list API: Submitting the assignment\n\n')
        log.info('Inside get_student_assign_list API: Submitting the assignment')

        get_student_assign_list_res = {}

        data = []

        try:
            req_data = json.loads(parameter_list.POST.get('data'))
        except Exception as ex:
            print('Error in get_student_assign_list API: req_data: %s' % ex)
            log.error('Error in get_student_assign_list API: req_data: %s' % ex)
            get_student_assign_list_res['status'] = 'fail'
            get_student_assign_list_res['message'] = str(ex)
            return get_student_assign_list_res

        r2_auth_res = UserProfile.r2_auth(
            username=req_data['email'],
            password=req_data['password'],
            request=parameter_list
        )

        if r2_auth_res['status'] is 'fail':
            return r2_auth_res
        else:

            try:

                current_student = Student.objects.get(student_email=req_data['email'])

                current_batch = current_student.student_batch_id

                all_assign = Assignment.objects.filter(batch=current_batch).order_by('-id')

                for one_assign in all_assign:
                    score = "0"

                    try:
                        current_ans = AssignmentAnswer.objects.get(
                            student=current_student,
                            assignment=one_assign
                        )
                    except Exception as ex:
                        score = 0

                    if not AssignmentAnswer.objects.filter(
                        student=current_student,
                        assignment=one_assign
                    ).exists():
                        status = 'take_now'
                    else:
                        score = str(current_ans.answer_seen + current_ans.answer_attempt + current_ans.answer_other_marks)
                        if current_ans.status == 'Pending':
                            status = 'pending_review'
                        else:
                            status = 'submitted'

                    data.append({
                        'title': one_assign.title,
                        'created_at': '%s' % R2DateTime.humanize_date(
                            datetime_from_utc_to_local(
                                one_assign.created_at
                            )
                        ),
                        'status': str(status),
                        'assign_id': str(one_assign.id),
                        'score': score
                    })

                msg = 'Assignment list fetched successfully'
                print(msg)
                log.info(msg)
                get_student_assign_list_res['status'] = 'success'
                get_student_assign_list_res['data'] = data
                get_student_assign_list_res['message'] = str(msg)
                return get_student_assign_list_res

            except Exception as ex:
                print('Error in get_student_assign_list API: getting assignment list: %s' % ex)
                log.error('Error in get_student_assign_list API: getting assignment list: %s' % ex)
                get_student_assign_list_res['status'] = 'fail'
                get_student_assign_list_res['message'] = str(ex)
                return get_student_assign_list_res

    @staticmethod
    def start_assignment(parameter_list):

        log.info('Inside start_assignment API: fetching questions')

        get_quiz_questions_res = {}

        data = []

        try:
            req_data = json.loads(parameter_list.POST.get('data'))
        except Exception as ex:
            log.error('Error in start_assignment API: req_data: %s' % ex)
            get_quiz_questions_res['status'] = 'fail'
            get_quiz_questions_res['message'] = str(ex)
            return get_quiz_questions_res

        r2_auth_res = UserProfile.r2_auth(
            username=req_data['email'],
            password=req_data['password'],
            request=parameter_list
        )

        if r2_auth_res['status'] is 'fail':
            return r2_auth_res
        else:

            try:

                current_assignment = Assignment.objects.get(id=req_data['ass_id'])

                data.append({
                    'ass_id': current_assignment.id,
                    'title': current_assignment.title,
                    'text': current_assignment.text,
                    'has_img': str(current_assignment.has_img),
                    'img_url': 'media/%s' % str(current_assignment.img_url),
                    'has_video': str(current_assignment.has_video),
                    'video_url': str(current_assignment.video_url),
                    'created_at': '%s' % R2DateTime.humanize_date(
                        datetime_from_utc_to_local(
                            current_assignment.created_at
                        )
                    )
                })

                msg = 'Assignment details fetched successfully!'
                log.info(msg)
                get_quiz_questions_res['status'] = 'success'
                get_quiz_questions_res['data'] = data
                get_quiz_questions_res['message'] = str(msg)
                return get_quiz_questions_res

            except Exception as ex:

                log.error('Error in start_assignment API: fetching assignment details: %s' % ex)
                get_quiz_questions_res['status'] = 'fail'
                get_quiz_questions_res['message'] = str(ex)
                return get_quiz_questions_res

    @staticmethod
    def get_application_list(parameter_list):

        log.info('Inside get_application_list API: fetching questions')

        get_quiz_questions_res = {}

        data = []

        try:
            req_data = json.loads(parameter_list.POST.get('data'))
        except Exception as ex:
            log.error('Error in get_application_list API: req_data: %s' % ex)
            get_quiz_questions_res['status'] = 'fail'
            get_quiz_questions_res['message'] = str(ex)
            return get_quiz_questions_res

        r2_auth_res = UserProfile.r2_auth(
            username=req_data['email'],
            password=req_data['password'],
            request=parameter_list
        )

        if r2_auth_res['status'] is 'fail':
            return r2_auth_res
        else:

            try:

                current_student = Student.objects.get(student_email=req_data['email'])

                all_topics = ApplicationTopic.objects.filter(batch=current_student.student_batch_id)

                for one_topic in all_topics:

                    if not Application.objects.filter(student=current_student, topic=one_topic).exists():
                        status = 'take_now'
                        score = 0
                    else:
                        current_app = Application.objects.get(student=current_student, topic=one_topic)
                        if current_app.app_status == 'Pending':
                            status = 'pending_review'
                            score = 0
                        else:
                            status = 'submitted'
                            score = current_app.app_seen + current_app.app_attempt + current_app.app_other_marks

                    data.append({
                        'title': str(one_topic.topic_text),
                        'created_at': '%s' % R2DateTime.humanize_date(
                            datetime_from_utc_to_local(
                                one_topic.topic_date
                            )
                        ),
                        'topic_id': str(one_topic.id),
                        'status': status,
                        'score': str(score)
                    })

                msg = 'Applications fetched successfully'
                log.error(msg)
                get_quiz_questions_res['status'] = 'success'
                get_quiz_questions_res['data'] = data
                get_quiz_questions_res['message'] = str(msg)
                return get_quiz_questions_res

            except Exception as ex:
                log.error('Error in get_application_list API: fetching appication topics: %s' % ex)
                get_quiz_questions_res['status'] = 'fail'
                get_quiz_questions_res['message'] = str(ex)
                return get_quiz_questions_res

    @staticmethod
    def submit_application(parameter_list):
        log.info('Inside submit_application API: fetching questions')

        submit_application_res = {}

        try:
            req_data = json.loads(parameter_list.POST.get('data'))
        except Exception as ex:
            log.error('Error in submit_application API: req_data: %s' % ex)
            submit_application_res['status'] = 'fail'
            submit_application_res['message'] = str(ex)
            return submit_application_res

        r2_auth_res = UserProfile.r2_auth(
            username=req_data['email'],
            password=req_data['password'],
            request=parameter_list
        )

        if r2_auth_res['status'] is 'fail':
            return r2_auth_res
        else:

            try:

                current_student = Student.objects.get(student_email=req_data['email'])

                current_topic = ApplicationTopic.objects.get(id=int(req_data['topic_id']))

                if not Application.objects.filter(
                    student=current_student,
                    topic=current_topic,
                ).exists():

                    date_applied = req_data['date_applied'].split('-')

                    Application.objects.create(
                        student=current_student,
                        topic=current_topic,
                        instance=req_data['instance'],
                        effect=req_data['effect'],
                        well=req_data['well'],
                        unexpected=req_data['unexpected'],
                        reflection=req_data['reflection'],
                        different=req_data['different'],
                        date_applied=datetime(int(date_applied[0]), int(date_applied[1]), int(date_applied[2])),
                        app_seen=int(req_data['app_seen']),
                        app_attempt=int(req_data['app_attempt'])
                    ).save()

                    msg = 'Application submitted successfully'
                    log.info('msg')
                    submit_application_res['status'] = 'success'
                    submit_application_res['message'] = str(msg)
                    return submit_application_res

                else:

                    msg = 'Application already submitted'
                    log.info('msg')
                    submit_application_res['status'] = 'fail'
                    submit_application_res['message'] = str(msg)
                    return submit_application_res

            except Exception as ex:
                log.error('Error in submit_application API: submitting application: %s' % ex)
                submit_application_res['status'] = 'fail'
                submit_application_res['message'] = str(ex)
                return submit_application_res

    @staticmethod
    def view_quiz_answers(parameter_list):

        log.info('Inside view_quiz_answers API: fetching question-answers')

        view_quiz_answers_res = {}

        data = []

        try:
            req_data = json.loads(parameter_list.POST.get('data'))
        except Exception as ex:
            log.error('Error in view_quiz_answers API: req_data: %s' % ex)
            view_quiz_answers_res['status'] = 'fail'
            view_quiz_answers_res['message'] = str(ex)
            return view_quiz_answers_res

        r2_auth_res = UserProfile.r2_auth(
            username=req_data['email'],
            password=req_data['password'],
            request=parameter_list
        )

        if r2_auth_res['status'] is 'fail':
            return r2_auth_res
        else:

            try:

                current_student = Student.objects.get(student_email=req_data['email'])

                current_quiz = Quiz.objects.get(id=req_data['quiz_id'])

                all_question = Question.objects.filter(question_quiz=current_quiz).order_by('id')

                has_essay = False

                total_score = 0

                for one_question in all_question:
                    if one_question.question_type == 'Essay':
                        has_essay = True

                    student_ans = Answer.objects.get(answer_student=current_student, answer_question=one_question)
                    sub_total = student_ans.answer_seen + student_ans.answer_attempt + student_ans.answer_other_marks
                    total_score = total_score + sub_total

                    def get_ans_switch(x):
                        if one_question.question_type is 'MCQ':
                            return {
                                one_question.question_op_a: 'A',
                                one_question.question_op_b: 'B',
                                one_question.question_op_c: 'C',
                                one_question.question_op_d: 'D'
                            }[x]
                        else:
                            return str(x)

                    data.append({
                        'question_id': one_question.id,
                        'question_text': one_question.question_text,
                        'question_type': one_question.question_type,
                        'op_a': one_question.question_op_a,
                        'op_b': one_question.question_op_b,
                        'op_c': one_question.question_op_c,
                        'op_d': one_question.question_op_d,
                        'correct_ans': one_question.question_correct_ans,
                        'student_ans': get_ans_switch(student_ans.answer_text)
                    })

                msg = 'Questions fetched successfully'
                log.error(msg)
                view_quiz_answers_res['quiz_title'] = current_quiz.quiz_desc
                view_quiz_answers_res['total_score'] = str(total_score)
                view_quiz_answers_res['data'] = data
                view_quiz_answers_res['status'] = 'success'
                view_quiz_answers_res['has_essay'] = str(has_essay)
                view_quiz_answers_res['message'] = str(msg)
                return view_quiz_answers_res

            except Exception as ex:
                log.error('Error in view_quiz_answers API: fetching question - answers: %s' % ex)
                view_quiz_answers_res['status'] = 'fail'
                view_quiz_answers_res['message'] = str(ex)
                return view_quiz_answers_res

    @staticmethod
    def view_app_answers(parameter_list):

        log.info('Inside view_app_answers API: fetching app-answers')

        view_app_answers_res = {}

        data = []

        try:
            req_data = json.loads(parameter_list.POST.get('data'))
        except Exception as ex:
            log.error('Error in view_app_answers API: req_data: %s' % ex)
            view_app_answers_res['status'] = 'fail'
            view_app_answers_res['message'] = str(ex)
            return view_app_answers_res

        r2_auth_res = UserProfile.r2_auth(
            username=req_data['email'],
            password=req_data['password'],
            request=parameter_list
        )

        if r2_auth_res['status'] is 'fail':
            return r2_auth_res
        else:

            try:

                current_student = Student.objects.get(student_email=req_data['email'])
                current_topic = ApplicationTopic.objects.get(id=req_data['topic_id'])

                current_app = Application.objects.get(student=current_student, topic=current_topic)

                data.append({
                    'instance': current_app.instance,
                    'effect': current_app.effect,
                    'well': current_app.well,
                    'unexpected': current_app.unexpected,
                    'reflection': current_app.reflection,
                    'different': current_app.different,
                    'date_applied': str(current_app.date_applied),
                    'total_marks': '%s' % str(current_app.app_seen + current_app.app_attempt + current_app.app_other_marks)
                })

                msg = 'Application fetched successfully'
                log.info(msg)
                view_app_answers_res['status'] = 'success'
                view_app_answers_res['data'] = data
                view_app_answers_res['message'] = str(msg)
                return view_app_answers_res
            except Exception as ex:
                log.error('Error in view_app_answers API: fetching app-answers: %s' % ex)
                view_app_answers_res['status'] = 'fail'
                view_app_answers_res['message'] = str(ex)
                return view_app_answers_res

    @staticmethod
    def view_assignment_ans(parameter_list):

        log.info('Inside view_assignment_ans API: fetching questions')

        view_assignment_ans_res = {}

        data = []

        try:
            req_data = json.loads(parameter_list.POST.get('data'))
        except Exception as ex:
            log.error('Error in view_assignment_ans API: req_data: %s' % ex)
            view_assignment_ans_res['status'] = 'fail'
            view_assignment_ans_res['message'] = str(ex)
            return view_assignment_ans_res

        r2_auth_res = UserProfile.r2_auth(
            username=req_data['email'],
            password=req_data['password'],
            request=parameter_list
        )

        if r2_auth_res['status'] is 'fail':
            return r2_auth_res
        else:

            try:

                current_student = Student.objects.get(student_email=req_data['email'])
                current_assignment = Assignment.objects.get(id=req_data['ass_id'])
                current_ass_ans = AssignmentAnswer.objects.get(assignment=current_assignment, student=current_student)

                data.append({
                    'ass_id': current_assignment.id,
                    'title': current_assignment.title,
                    'text': current_assignment.text,
                    'has_img': str(current_assignment.has_img),
                    'img_url': 'media/%s' % str(current_assignment.img_url),
                    'has_video': str(current_assignment.has_video),
                    'video_url': str(current_assignment.video_url),
                    'student_answer': current_ass_ans.answer_text,
                    'total_score': str(current_ass_ans.answer_seen + current_ass_ans.answer_attempt + current_ass_ans.answer_other_marks),
                    'created_at': '%s' % R2DateTime.humanize_date(
                        datetime_from_utc_to_local(
                            current_assignment.created_at
                        )
                    )
                })

                msg = 'Assignment answer fetched successfully!'
                log.info(msg)
                view_assignment_ans_res['status'] = 'success'
                view_assignment_ans_res['data'] = data
                view_assignment_ans_res['message'] = str(msg)
                return view_assignment_ans_res

            except Exception as ex:

                log.error('Error in view_assignment_ans API: fetching assignment answers: %s' % ex)
                view_assignment_ans_res['status'] = 'fail'
                view_assignment_ans_res['message'] = str(ex)
                return view_assignment_ans_res

    @staticmethod
    def share_post(parameter_list, post_id):

        log.info('Inside share_post API: fetching post details')

        share_post_res = {}

        data = {}

        try:

            current_post = Post.objects.get(id=post_id)

            data['title'] = str(current_post.post_title)
            data['text'] = current_post.post_text
            data['has_image'] = current_post.post_has_img
            data['image_url'] = str(current_post.post_img_url)
            data['has_video'] = current_post.post_has_video

            if current_post.post_video is not None:
                data['video_url'] = str(current_post.post_video).split('&')[0].split('?v=')[1]
            else:
                data['video_url'] = str(current_post.post_video)
            data['created_at'] = '%s' % R2DateTime.humanize_date(
                datetime_from_utc_to_local(
                    current_post.post_created_at
                )
            )

        except Exception as ex:
            log.error('Error in share_post API: fetching post details: %s' % ex)
            share_post_res['status'] = 'fail'
            share_post_res['data'] = data
            share_post_res['message'] = str(ex)
            return share_post_res

        share_post_res['message'] = 'Share post details fetched successfully'
        share_post_res['status'] = 'success'
        share_post_res['data'] = data
        log.info(share_post_res['message'])
        return share_post_res

    @staticmethod
    def get_leader_board_ranks(parameter_list):

        log.info('Inside view_assignment_ans API: fetching questions')

        get_leader_board_ranks_res = {}

        data = []

        try:
            req_data = json.loads(parameter_list.POST.get('data'))
        except Exception as ex:
            log.error('Error in view_assignment_ans API: req_data: %s' % ex)
            get_leader_board_ranks_res['status'] = 'fail'
            get_leader_board_ranks_res['message'] = str(ex)
            return get_leader_board_ranks_res

        r2_auth_res = UserProfile.r2_auth(
            username=req_data['email'],
            password=req_data['password'],
            request=parameter_list
        )

        if r2_auth_res['status'] is 'fail':
            return r2_auth_res
        else:

            data = []

            try:

                current_student = Student.objects.get(student_email=req_data['email'])
                current_student_data = {}
                current_batch = current_student.student_batch_id

                all_student = Student.objects.filter(student_batch_id=current_batch)

                for one_student in all_student:

                    student_marks_data = get_student_marks(
                        one_student=one_student,
                        current_student=current_student
                    )

                    if student_marks_data['status'] is 'fail':
                        return student_marks_data

                    sub_data = {
                        'user_id': str(one_student.id),
                        'user_name': '%s' % (
                            one_student.student_first_name
                        ),
                        # 'user_rank': '',
                        'user_points': student_marks_data['total'],
                        'current_user': str(student_marks_data['is_current_student']),
                        'user_img': str('media/%s' % one_student.student_picture_url),
                    }

                    data.append(sub_data)

                    if student_marks_data['is_current_student']:
                        current_student_data = sub_data

                data.sort(key=lambda x: x['user_points'], reverse=True)

                get_leader_board_ranks_res['message'] = str('Leader board rank fetched successfully')
                log.info(get_leader_board_ranks_res['message'])
                get_leader_board_ranks_res['status'] = 'success'
                get_leader_board_ranks_res['data'] = data
                return get_leader_board_ranks_res

            except Exception as ex:
                log.error('Error in view_assignment_ans API: req_data: %s' % ex)
                get_leader_board_ranks_res['status'] = 'fail'
                get_leader_board_ranks_res['message'] = str(ex)
                return get_leader_board_ranks_res

    @staticmethod
    def get_badge_list(parameter_list):

        log.info('Inside get_badge_list API: fetching badges')

        get_badge_list_res = {}

        data = []

        try:
            req_data = json.loads(parameter_list.POST.get('data'))
        except Exception as ex:
            log.error('Error in get_badge_list API: req_data: %s' % ex)
            get_badge_list_res['status'] = 'fail'
            get_badge_list_res['message'] = str(ex)
            return get_badge_list_res

        r2_auth_res = UserProfile.r2_auth(
            username=req_data['email'],
            password=req_data['password'],
            request=parameter_list
        )

        if r2_auth_res['status'] is 'fail':
            return r2_auth_res
        else:
            try:

                badge_list = []

                curremt_student = Student.objects.get(
                    student_email=req_data['email']
                )

                all_student_badge = StudentBadge.objects.filter(
                    student=curremt_student
                )

                for one_student_badge in all_student_badge:
                    badge_list.append({
                        'id': one_student_badge.badge.id,
                        'name': one_student_badge.badge.name,
                        'desc': one_student_badge.badge.desc,
                        'image': 'media/%s' % one_student_badge.badge.image
                    })

            except Exception as ex:
                log.error('Error in admin_view_badges API: fetching badges: %s' % ex)
                get_badge_list_res['status'] = 'fail'
                get_badge_list_res['message'] = str(ex)
                return get_badge_list_res

            get_badge_list_res['badge_list'] = badge_list
            get_badge_list_res['message'] = 'Badges fetched successfully'
            get_badge_list_res['status'] = 'success'
            log.info(get_badge_list_res['message'])
            return get_badge_list_res

    @staticmethod
    def boost_me_info(parameter_list):

        log.info('Inside boost_me_info API: fetching boost me info')

        get_badge_list_res = {}

        data = {}

        try:
            req_data = json.loads(parameter_list.POST.get('data'))
        except Exception as ex:
            log.error('Error in boost_me_info API: req_data: %s' % ex)
            get_badge_list_res['status'] = 'fail'
            get_badge_list_res['message'] = str(ex)
            return get_badge_list_res

        r2_auth_res = UserProfile.r2_auth(
            username=req_data['email'],
            password=req_data['password'],
            request=parameter_list
        )

        if r2_auth_res['status'] is 'fail':
            return r2_auth_res
        else:

            try:

                current_student = Student.objects.get(student_email=req_data['email'])

                data['student_name'] = '%s %s' % (
                    current_student.student_first_name,
                    current_student.student_last_name
                )

                marks_details = get_student_marks(current_student, current_student)

                data['score'] = marks_details['total']

                rank_details = get_student_rank_reuse(current_student)

                if rank_details['status'] != 'success':
                    data['rank'] = '-'
                else:
                    data['rank'] = rank_details['rank']

                data['student_image'] = 'media/%s' % current_student.student_picture_url
                data['company_image'] = 'media/%s' % current_student.student_batch_id.batch_company_logo

            except Exception as ex:
                log.error('Error in boost_me_info API: fetching boost me info: %s' % ex)
                get_badge_list_res['status'] = 'fail'
                get_badge_list_res['message'] = str(ex)
                return get_badge_list_res

            get_badge_list_res['message'] = 'Boost me details fetched successfully'
            get_badge_list_res['data'] = data
            get_badge_list_res['status'] = 'success'
            log.info(get_badge_list_res['message'])
            return get_badge_list_res

    # ------------------------
    # ------------------------
    # ----- ADMIN APIs -------
    # ------------------------
    # ------------------------

    @staticmethod
    def create_quiz(parameter_list):
        print('\n\nInside create_quiz API: Creating new Quiz\n\n')
        log.info('Inside create_quiz API: Creating new Quiz')

        create_quiz_res = {}

        try:
            req_data = json.loads(parameter_list.body.decode('utf-8'))
            req_data = req_data['data']

            # req_data = json.loads(parameter_list.POST.get('data'))
        except Exception as ex:
            print('Error in create_quiz API: req_data: %s' % ex)
            log.error('Error in create_quiz API: req_data: %s' % ex)
            create_quiz_res['status'] = 'fail'
            create_quiz_res['message'] = str(ex)
            return create_quiz_res

        # r2_auth_res = UserProfile.r2_auth(
        #     username=req_data['username'],
        #     password=req_data['password'],
        #     request=parameter_list
        # )
        #
        # if r2_auth_res['status'] is 'fail':
        #     return r2_auth_res
        # else:

        try:

            current_quiz = Quiz.objects.create(
                quiz_desc=req_data['data']['desc'],
                quiz_batch=Batch.objects.get(id=req_data['data']['batch_id'])
            )

            current_quiz.save()

        except Exception as ex:
            print('Error in create_quiz API: creating quiz: %s' % ex)
            log.error('Error in create_quiz API: creating quiz: %s' % ex)
            create_quiz_res['status'] = 'fail'
            create_quiz_res['message'] = str(ex)
            return create_quiz_res

        try:

            for one_question in req_data['data']['questions']:
                Question.objects.create(
                    question_quiz=current_quiz,
                    question_text=one_question['title'],
                    question_type=one_question['type'],
                    question_op_a=one_question['option_a'],
                    question_op_b=one_question['option_b'],
                    question_op_c=one_question['option_c'],
                    question_op_d=one_question['option_d'],
                    question_correct_ans=one_question['correct_ans']
                ).save()

        except Exception as ex:
            print('Error in create_quiz API: adding questions to quiz: %s' % ex)
            log.error('Error in create_quiz API: adding questions to quiz: %s' % ex)
            create_quiz_res['status'] = 'fail'
            create_quiz_res['message'] = str(ex)
            return create_quiz_res

        try:
            current_quiz.quiz_published = True
            current_quiz.save()
        except Exception as ex:
            print('Error in create_quiz API: publishing quiz: %s' % ex)
            log.error('Error in create_quiz API: publishing quiz: %s' % ex)
            create_quiz_res['status'] = 'fail'
            create_quiz_res['message'] = str(ex)
            return create_quiz_res

        all_students = Student.objects.filter(student_batch_id=current_quiz.quiz_batch)

        try:

            for one_student in all_students:
                Notification.objects.create(
                    notif_text='<strong>%s</strong>, You have a new quiz to solve in your batch.' % one_student.student_first_name,
                    notif_student=one_student,
                    notif_type='Admin',
                    notif_quiz=current_quiz,
                    redirect_to='Quiz'
                ).save()

                PushyAPI.prepare_notification(
                    student=one_student,
                    data_msg='New Quiz',
                    body_text='%s, You have a new quiz to solve in your batch.' % one_student.student_first_name
                )

        except Exception as ex:
            print('Error in create_quiz API: creating notification: %s' % ex)
            log.error('Error in create_quiz API: creating notification: %s' % ex)
            create_quiz_res['status'] = 'fail'
            create_quiz_res['message'] = str(ex)
            return create_quiz_res

        msg = 'Quiz created, published and notification created successfully'
        print(msg)
        log.info(msg)
        create_quiz_res['status'] = 'success'
        create_quiz_res['message'] = str(msg)
        return create_quiz_res

    @staticmethod
    def add_batch(parameter_list):
        print('\n\nInside add_batch API: Adding new Batch\n\n')
        log.info('Inside add_batch API: Adding new Batch')

        add_batch_res = {}

        try:
            req_data = json.loads(parameter_list.body.decode('utf-8'))
            req_data = req_data['data']

        except Exception as ex:
            print('Error in add_batch API: req_data: %s' % ex)
            log.error('Error in add_batch API: req_data: %s' % ex)
            add_batch_res['status'] = 'fail'
            add_batch_res['message'] = str(ex)
            return add_batch_res

        # r2_auth_res = UserProfile.r2_auth(
        #     username=req_data['username'],
        #     password=req_data['password'],
        #     request=parameter_list
        # )
        #
        # if r2_auth_res['status'] is 'fail':
        #     return r2_auth_res
        # else:

        try:

            current_batch = Batch.objects.create(
                batch_desc=req_data['batch_desc'],
                batch_company_name=req_data['company_name'],
                batch_company_logo='test',
                batch_name=req_data['batch_name']
            )

            current_batch.save()

            try:

                req_image = req_data['company_logo']
                req_image = req_image.replace(' ', '+')

                im = Image.open(BytesIO(base64.b64decode(req_image)))
                im.save('media/batch_company_logo/temp/post_pic.png', 'PNG')
                temp_post_img = File(open('media/batch_company_logo/temp/post_pic.png', 'rb'))
                temp_post_img.name = 'image.png'

                current_batch.batch_company_logo = temp_post_img
                current_batch.save()

            except Exception as ex:
                print('Error in add_batch API: uploading image: %s' % ex)
                log.error('Error in add_batch API: uploading image: %s' % ex)
                add_batch_res['status'] = 'fail'
                add_batch_res['message'] = str(ex)
                return add_batch_res

            msg = 'Batch added successfully'
            print(msg)
            log.info(msg)
            add_batch_res['status'] = 'success'
            add_batch_res['message'] = str(msg)
            return add_batch_res

        except Exception as ex:
            print('Error in add_batch API: creating new batch: %s' % ex)
            log.error('Error in add_batch API: creating new batch: %s' % ex)
            add_batch_res['status'] = 'fail'
            add_batch_res['message'] = str(ex)
            return add_batch_res

    @staticmethod
    def signup(parameter_list):
        print('\n\nInside signup API: Signing up new student\n\n')
        log.info('Inside signup API: Signing up new student')
        signup_res = {}

        try:
            req_data = json.loads(parameter_list.POST.get('data'))
        except Exception as ex:
            print('Error in signup API: req_data: %s' % ex)
            log.error('Error in signup API: req_data: %s' % ex)
            signup_res['status'] = 'fail'
            signup_res['message'] = str(ex)
            return signup_res

        try:

            if parameter_list.user.is_superuser:
                print('\n\n:::is a super user:::')
                log.info(':::is a super user:::')
            else:
                print('\n\n:::is not a super user:::')
                log.info(':::is not a super user:::')

            if User.objects.filter(username=req_data['email']).exists():
                ex = 'Error in signup API: This student already exists'
                print('%s' % ex)
                log.error('%s' % ex)
                signup_res['status'] = 'fail'
                signup_res['message'] = str(ex)
                return signup_res

            else:
                try:
                    User.objects.create_user(
                        username=req_data['email'],
                        email=req_data['email'],
                        first_name=req_data['first_name'],
                        last_name=req_data['last_name'],
                        password=req_data['phone_number'],
                    ).save()
                except Exception as ex:
                    print('Error in signup API create admin user: %s' % ex)
                    log.error('Error in signup API create admin user: %s' % ex)
                    signup_res['status'] = 'fail'
                    signup_res['message'] = str(ex)
                    return signup_res

                try:
                    Student.objects.create(
                        student_user_id=User.objects.get(username=req_data['email']),
                        student_password=req_data['phone_number'],
                        student_picture_url=req_data['picture_url'],
                        student_create_at=now(),
                        student_email=req_data['email'],
                        student_first_name=req_data['first_name'],
                        student_last_name=req_data['last_name'],
                        student_batch_id=Batch.objects.get(id=req_data['batch_id'])
                    ).save()
                except Exception as ex:
                    print('Error in signup API create student: %s' % ex)
                    log.error('Error in signup API create student: %s' % ex)
                    signup_res['status'] = 'fail'
                    signup_res['message'] = str(ex)
                    return signup_res

        except Exception as ex:
            print('Error in signup API : %s' % ex)
            log.error('Error in signup API : %s' % ex)
            signup_res['status'] = 'fail'
            signup_res['message'] = str(ex)
            return signup_res

        signup_res['status'] = 'success'
        signup_res['message'] = str('Student created successfully!')
        return signup_res

    @staticmethod
    def get_all_students(parameter_list):
        print('\n\nInside get_all_students API: Getting all student info\n\n')
        log.info('Inside get_all_students API: Getting all student info')
        get_all_stud_res = {}

        try:
            req_data = json.loads(parameter_list.POST.get('data'))
        except Exception as ex:
            print('Error in add_comment API: req_data: %s' % ex)
            log.error('Error in add_comment API: req_data: %s' % ex)
            get_all_stud_res['status'] = 'fail'
            get_all_stud_res['message'] = str(ex)
            return get_all_stud_res

        try:
            data = []
            all_student = Student.objects.filter()
            for one_student in all_student:

                data.append({
                    'student_id': str(one_student.id),
                    'student_picture_url': str(one_student.student_picture_url),
                    'student_create_at': str(one_student.student_create_at),
                    'student_first_name': str(one_student.student_first_name),
                    'student_last_name': str(one_student.student_last_name),
                    'student_batch_id': str(one_student.student_batch_id),
                    'student_email': str(one_student.student_email),
                    'student_password': one_student.student_password
                })

            get_all_stud_res['data'] = data
            get_all_stud_res['status'] = 'success'

        except Exception as ex:
            print('Error in get_all_students(): %s' % ex)
            log.error('Error in get_all_students(): %s' % ex)
            get_all_stud_res['data'] = ''
            get_all_stud_res['status'] = 'fail'
            get_all_stud_res['message'] = str(ex)
            return get_all_stud_res

        print('Student details fetched successfully')
        log.info('Student details fetched successfully')
        get_all_stud_res['data'] = data
        get_all_stud_res['status'] = 'success'
        get_all_stud_res['message'] = 'Student details fetched successfully'
        return get_all_stud_res

    @staticmethod
    def delete_student(parameter_list):
        print('\n\nInside delete_student API: Deleting Student\n\n')
        log.info('Inside delete_student API: Deleting Student')

        update_student_res = {}

        try:
            req_data = json.loads(parameter_list.body.decode('utf-8'))
            req_data = req_data['data']

            # req_data = json.loads(parameter_list.POST.get('data'))
        except Exception as ex:
            print('Error in delete_student API: req_data: %s' % ex)
            log.error('Error in delete_student API: req_data: %s' % ex)
            update_student_res['status'] = 'fail'
            update_student_res['message'] = str(ex)
            return update_student_res

        try:
            User.objects.get(username=req_data['email']).delete()

            msg = 'Student deleted successfully'
            print(msg)
            log.info(msg)
            update_student_res['status'] = 'success'
            update_student_res['message'] = str(msg)
            return update_student_res

        except Exception as ex:
            print('Error in delete_student API: req_data: %s' % ex)
            log.error('Error in delete_student API: req_data: %s' % ex)
            update_student_res['status'] = 'fail'
            update_student_res['message'] = str(ex)
            return update_student_res

    @staticmethod
    def get_all_batches():

        print('\n\nInside get_all_batches API: Getting batch list\n\n')
        log.info('Inside get_all_batches API: Getting batch list')

        get_all_batches_res = {}

        data = []

        # try:
        #     # req_data = json.loads(parameter_list.body.decode('utf-8'))
        #     # req_data = req_data['data']
        #
        #     req_data = json.loads(parameter_list.POST.get('data'))
        # except Exception as ex:
        #     print('Error in get_all_batches API: req_data: %s' % ex)
        #     log.error('Error in get_all_batches API: req_data: %s' % ex)
        #     get_all_batches_res['status'] = 'fail'
        #     get_all_batches_res['message'] = str(ex)
        #     return get_all_batches_res

        # r2_auth_res = UserProfile.r2_auth(
        #     username=req_data['username'],
        #     password=req_data['password'],
        #     request=parameter_list
        # )

        # if r2_auth_res['status'] is 'fail':
        #     return r2_auth_res
        # else:

        try:

            all_batches = Batch.objects.filter().order_by('-id')

            for one_batch in all_batches:
                data.append({
                    "id": str(one_batch.id),
                    "desc": one_batch.batch_desc,
                    "create_at": str(one_batch.batch_create_at),
                    "company_name": one_batch.batch_company_name,
                    "company_logo": str(one_batch.batch_company_logo),
                    "batch_name": str(one_batch.batch_name)
                })

            msg = 'Batch data fetched successfully'
            print(msg)
            log.info(msg)
            get_all_batches_res['data'] = data
            get_all_batches_res['message'] = msg
            get_all_batches_res['status'] = 'success'
            return get_all_batches_res

        except Exception as ex:

            print('Error in get_all_batches API: fetching data: %s' % ex)
            log.error('Error in get_all_batches API: fetching data: %s' % ex)
            get_all_batches_res['data'] = data
            get_all_batches_res['message'] = 'Batch data cold not be fetched'
            get_all_batches_res['status'] = 'success'
            return get_all_batches_res

    @staticmethod
    def update_batch(parameter_list):
        print('\n\nInside update_batch API: Getting batch list\n\n')
        log.info('Inside update_batch API: Getting batch list')

        update_batch_res = {}

        try:
            req_data = json.loads(parameter_list.body.decode('utf-8'))
            req_data = req_data['data']
        except Exception as ex:
            print('Error in update_batch API: req_data: %s' % ex)
            log.error('Error in update_batch API: req_data: %s' % ex)
            update_batch_res['status'] = 'fail'
            update_batch_res['message'] = str(ex)
            return update_batch_res

        # r2_auth_res = UserProfile.r2_auth(
        #     username=req_data['username'],
        #     password=req_data['password'],
        #     request=parameter_list
        # )

        # if r2_auth_res['status'] is 'fail':
        #     return r2_auth_res
        # else:

        try:

            current_batch = Batch.objects.get(id=req_data['batch_id'])

            current_batch.batch_desc = req_data['batch_desc']
            current_batch.batch_company_name = req_data['company_name']
            current_batch.batch_name = req_data['batch_name']

            if req_data['company_logo'] != 'no image':

                try:

                    req_image = req_data['company_logo']
                    req_image = req_image.replace(' ', '+')

                    im = Image.open(BytesIO(base64.b64decode(req_image)))
                    im.save('media/batch_company_logo/temp/post_pic.png', 'PNG')
                    temp_post_img = File(open('media/batch_company_logo/temp/post_pic.png', 'rb'))
                    temp_post_img.name = 'image.png'

                    current_batch.batch_company_logo = temp_post_img

                except Exception as ex:
                    print('Error in update_batch API: uploading image: %s' % ex)
                    log.error('Error in update_batch API: uploading image: %s' % ex)
                    update_batch_res['status'] = 'fail'
                    update_batch_res['message'] = str(ex)
                    return update_batch_res

            current_batch.save()

            msg = 'Batch updated successfully'
            print(msg)
            log.info(msg)
            update_batch_res['status'] = 'success'
            update_batch_res['new_logo'] = str(current_batch.batch_company_logo)
            update_batch_res['message'] = str(msg)
            update_batch_res['new_company_logo'] = current_batch.batch_company_name
            return update_batch_res

        except Exception as ex:
            print('Error in update_batch API: updating batch: %s' % ex)
            log.error('Error in update_batch API: updating batch: %s' % ex)
            update_batch_res['status'] = 'fail'
            update_batch_res['message'] = str(ex)
            return update_batch_res

    @staticmethod
    def delete_batch(parameter_list):
        print('\n\nInside delete_batch API: Deleting batch\n\n')
        log.info('Inside delete_batch API: Deleting batch')

        delete_batch_res = {}

        try:
            req_data = json.loads(parameter_list.body.decode('utf-8'))
            req_data = req_data['data']
        except Exception as ex:
            print('Error in delete_batch API: req_data: %s' % ex)
            log.error('Error in delete_batch API: req_data: %s' % ex)
            delete_batch_res['status'] = 'fail'
            delete_batch_res['message'] = str(ex)
            return delete_batch_res

        # r2_auth_res = UserProfile.r2_auth(
        #     username=req_data['username'],
        #     password=req_data['password'],
        #     request=parameter_list
        # )
        #
        # if r2_auth_res['status'] is 'fail':
        #     return r2_auth_res
        # else:
        try:
            Batch.objects.filter(id=req_data['batch_id']).delete()

            msg = 'Batch deleted successfully'
            print(msg)
            log.info(msg)
            delete_batch_res['status'] = 'success'
            delete_batch_res['message'] = str(msg)
            return delete_batch_res

        except Exception as ex:
            print('Error in delete_batch API: deleting batch: %s' % ex)
            log.error('Error in delete_batch API: deleting batch: %s' % ex)
            delete_batch_res['status'] = 'fail'
            delete_batch_res['message'] = str(ex)
            return delete_batch_res

    @staticmethod
    def get_admin_counts(parameter_list):

        print('\n\nInside get_admin_counts API: Getting Admin Counts\n\n')
        log.info('Inside get_admin_counts API: Getting Admin Counts')

        get_admin_counts_res = {}

        try:
            req_data = json.loads(parameter_list.body.decode('utf-8'))
            req_data = req_data['data']

            # req_data = json.loads(parameter_list.POST.get('data'))

            # print('\n\n\n\n\n parameter_list value: ')
            # print(parameter_list.META)

        except Exception as ex:
            print('Error in get_admin_counts API: req_data: %s' % ex)
            log.error('Error in get_admin_counts API: req_data: %s' % ex)
            get_admin_counts_res['status'] = 'fail'
            get_admin_counts_res['message'] = str(ex)
            return get_admin_counts_res

        r2_auth_res = UserProfile.r2_auth(
            username=req_data['username'],
            password=req_data['password'],
            request=parameter_list
        )

        if r2_auth_res['status'] is 'fail':
            return r2_auth_res
        else:

            try:

                get_admin_counts_res['batch_count'] = Batch.objects.filter().count()
                get_admin_counts_res['student_count'] = Student.objects.filter().count()
                get_admin_counts_res['quiz_count'] = Quiz.objects.filter().count()
                get_admin_counts_res['post_count'] = Post.objects.filter().count()
                get_admin_counts_res['ass_count'] = Assignment.objects.filter().count()
                get_admin_counts_res['app_count'] = Application.objects.filter().count()
                get_admin_counts_res['app_topic_count'] = ApplicationTopic.objects.filter().count()
                get_admin_counts_res['badge_count'] = Badge.objects.filter().count()

                msg = 'Admin counts fetched successfully'
                print(msg)
                log.info(msg)
                get_admin_counts_res['status'] = 'success'
                get_admin_counts_res['message'] = str(msg)
                return get_admin_counts_res

            except Exception as ex:
                print('Error in get_admin_counts API: getting counts: %s' % ex)
                log.error('Error in get_admin_counts API: getting counts: %s' % ex)
                get_admin_counts_res['status'] = 'fail'
                get_admin_counts_res['message'] = str(ex)
                return get_admin_counts_res

    @staticmethod
    def get_quiz_by_batch_admin(parameter_list):

        print('\n\nInside get_quiz_by_batch API: Getting quiz list batch\n\n')
        log.info('Inside get_quiz_by_batch API: Getting quiz list batch')

        get_quiz_by_batch_res = {}

        data = []

        try:
            req_data = json.loads(parameter_list.body.decode('utf-8'))
            req_data = req_data['data']

            # req_data = json.loads(parameter_list.POST.get('data'))

        except Exception as ex:
            print('Error in get_quiz_by_batch API: req_data: %s' % ex)
            log.error('Error in get_quiz_by_batch API: req_data: %s' % ex)
            get_quiz_by_batch_res['status'] = 'fail'
            get_quiz_by_batch_res['message'] = str(ex)
            return get_quiz_by_batch_res

        # r2_auth_res = UserProfile.r2_auth(
        #     username=req_data['username'],
        #     password=req_data['password'],
        #     request=parameter_list
        # )
        #
        # if r2_auth_res['status'] is 'fail':
        #     return r2_auth_res
        # else:

        try:

            current_batch = Batch.objects.get(id=req_data['batch_id'])

            all_quiz = Quiz.objects.filter(quiz_batch=current_batch)

            for one_quiz in all_quiz:

                data.append({
                    'quiz_id': one_quiz.id,
                    'quiz_desc': one_quiz.quiz_desc,
                    'quiz_created_at': str(one_quiz.quiz_created_at),
                    'quiz_published': one_quiz.quiz_published
                })

            msg = 'Quiz list fetched successfully'
            print(msg)
            log.info(msg)
            get_quiz_by_batch_res['data'] = data
            get_quiz_by_batch_res['status'] = 'success'
            get_quiz_by_batch_res['message'] = str(msg)
            return get_quiz_by_batch_res

        except Exception as ex:
            print('Error in get_quiz_by_batch API: fetching quiz list: %s' % ex)
            log.error('Error in get_quiz_by_batch API: fetching quiz list: %s' % ex)
            get_quiz_by_batch_res['status'] = 'fail'
            get_quiz_by_batch_res['message'] = str(ex)
            return get_quiz_by_batch_res

    @staticmethod
    def get_question_by_quiz_admin(parameter_list):
        print('\n\nInside get_question_by_quiz_admin API: getting answer list\n\n')
        log.info('Inside get_question_by_quiz_admin API: getting answer list')

        get_question_by_quiz_admin_res = {}

        questions = []

        try:
            req_data = json.loads(parameter_list.body.decode('utf-8'))
            req_data = req_data['data']

            # req_data = json.loads(parameter_list.POST.get('data'))

        except Exception as ex:
            print('Error in get_question_by_quiz_admin API: req_data: %s' % ex)
            log.error('Error in get_question_by_quiz_admin API: req_data: %s' % ex)
            get_question_by_quiz_admin_res['status'] = 'fail'
            get_question_by_quiz_admin_res['message'] = str(ex)
            return get_question_by_quiz_admin_res

        # r2_auth_res = UserProfile.r2_auth(
        #     username=req_data['username'],
        #     password=req_data['password'],
        #     request=parameter_list
        # )
        #
        # if r2_auth_res['status'] is 'fail':
        #     return r2_auth_res
        # else:

        current_quiz = Quiz.objects.get(id=req_data['quiz_id'])

        all_questions = Question.objects.filter(question_quiz=current_quiz).order_by('id')

        for one_question in all_questions:

            try:

                answers = []

                all_answers = Answer.objects.filter(answer_question=one_question).order_by('-id')

                for one_answer in all_answers:

                    answers.append({
                        'student_id': one_answer.answer_student.id,
                        'answer_id': one_answer.id,
                        'student_name': '%s %s' % (
                            one_answer.answer_student.student_first_name,
                            one_answer.answer_student.student_last_name
                        ),
                        'student_ans': one_answer.answer_text,
                        'answer_status': one_answer.answer_status,
                        'answer_seen': one_answer.answer_seen,
                        'answer_attempt': one_answer.answer_attempt,
                        'other_marks': one_answer.answer_other_marks
                    })

            except Exception as ex:
                print('Error in get_question_by_quiz_admin API: fetching answer list: %s' % ex)
                log.error('Error in get_question_by_quiz_admin API: fetching answer list: %s' % ex)
                get_question_by_quiz_admin_res['status'] = 'fail'
                get_question_by_quiz_admin_res['message'] = str(ex)
                return get_question_by_quiz_admin_res

            try:

                questions.append({
                    'question_id': one_question.id,
                    'question_text': one_question.question_text,
                    'question_type': one_question.question_type,
                    'question_op_a': one_question.question_op_a,
                    'question_op_b': one_question.question_op_b,
                    'question_op_c': one_question.question_op_c,
                    'question_op_d': one_question.question_op_d,
                    'question_correct_ans': one_question.question_correct_ans,
                    'answers': answers
                })

            except Exception as ex:
                print('Error in get_question_by_quiz_admin API: fetching question list: %s' % ex)
                log.error('Error in get_question_by_quiz_admin API: fetching question list: %s' % ex)
                get_question_by_quiz_admin_res['status'] = 'fail'
                get_question_by_quiz_admin_res['message'] = str(ex)
                return get_question_by_quiz_admin_res

        msg = 'Answer list fetched successfully'
        print(msg)
        log.info(msg)
        get_question_by_quiz_admin_res['questions'] = questions
        get_question_by_quiz_admin_res['status'] = 'success'
        get_question_by_quiz_admin_res['message'] = str(msg)
        return get_question_by_quiz_admin_res

    @staticmethod
    def submit_quiz_review(parameter_list):

        print('\n\nInside submit_quiz_review API: submitting review\n\n')
        log.info('Inside submit_quiz_review API: submitting review')

        submit_quiz_review_res = {}

        try:
            req_data = json.loads(parameter_list.body.decode('utf-8'))
            req_data = req_data['data']

            # req_data = json.loads(parameter_list.POST.get('data'))

        except Exception as ex:
            print('Error in submit_quiz_review API: req_data: %s' % ex)
            log.error('Error in submit_quiz_review API: req_data: %s' % ex)
            submit_quiz_review_res['status'] = 'fail'
            submit_quiz_review_res['message'] = str(ex)
            return submit_quiz_review_res

        # r2_auth_res = UserProfile.r2_auth(
        #     username=req_data['username'],
        #     password=req_data['password'],
        #     request=parameter_list
        # )
        #
        # if r2_auth_res['status'] is 'fail':
        #     return r2_auth_res
        # else:

        submitted_review = req_data['answers']

        try:

            for one_review in submitted_review:

                answer_to_update = Answer.objects.get(id=one_review['answer_id'])

                answer_to_update.answer_status = one_review['answer_status']
                answer_to_update.answer_other_marks = one_review['other_marks']

                answer_to_update.save()

            msg = 'Answers submitted successfully'
            print(msg)
            log.info(msg)
            submit_quiz_review_res['status'] = 'success'
            submit_quiz_review_res['message'] = str(msg)
            return submit_quiz_review_res

        except Exception as ex:
            print('Error in submit_quiz_review API: updating answers: %s' % ex)
            log.error('Error in submit_quiz_review API: updating answers: %s' % ex)
            submit_quiz_review_res['status'] = 'fail'
            submit_quiz_review_res['message'] = str(ex)
            return submit_quiz_review_res

    @staticmethod
    def get_students():

        log.info('Inside get_students API: Getting all student info')
        get_students_res = {}

        try:
            data = []
            all_student = Student.objects.filter().order_by('-student_create_at')

            all_badges = Badge.objects.all()

            for one_student in all_student:

                student_marks = get_student_marks(one_student, one_student)

                current_batch = one_student.student_batch_id

                all_quiz = Quiz.objects.filter(quiz_batch=current_batch)

                total_quiz_questions = 0

                for one_quiz in all_quiz:
                    total_quiz_questions = total_quiz_questions + Question.objects.filter(question_quiz=one_quiz).count()

                total_assign = Assignment.objects.filter(batch=current_batch).count()

                total_topic = ApplicationTopic.objects.filter(batch=current_batch).count()

                badge_list = []

                for one_badge in all_badges:
                    badge_list.append({
                        'id': one_badge.id,
                        'name': one_badge.name,
                        'has': StudentBadge.objects.filter(student=one_student, badge=one_badge).exists()
                    })

                data.append({
                    'id': str(one_student.id),
                    'picture_url': str(one_student.student_picture_url),
                    'first_name': str(one_student.student_first_name),
                    'last_name': str(one_student.student_last_name),
                    'full_name': '%s %s' % (
                        str(one_student.student_first_name),
                        str(one_student.student_last_name)
                    ),
                    'batch_id': str(one_student.student_batch_id.id),
                    'batch_name': str(one_student.student_batch_id.batch_name),
                    'email': str(one_student.student_email),
                    'device': str(one_student.student_device_type),
                    'os_version': str(one_student.student_os_version),
                    'app_version': str(one_student.student_app_version),
                    'create_at': str(one_student.student_create_at),
                    'password': one_student.student_password,
                    'quiz_marks': student_marks['quiz'],
                    'ass_marks': student_marks['ass'],
                    'app_marks': student_marks['app'],
                    'total_marks': student_marks['total'],
                    'quiz_outof': total_quiz_questions * QUIZ_QUESTION_OUT_OF,
                    'app_outof': total_topic * APPLICATION_OUT_OF,
                    'ass_outof': total_assign * ASSIGNMENT_OUT_OF,
                    'badge_list': badge_list
                })

            get_students_res['data'] = data
            get_students_res['status'] = 'success'

        except Exception as ex:
            print('Error in get_students(): %s' % ex)
            log.error('Error in get_students(): %s' % ex)
            get_students_res['data'] = ''
            get_students_res['status'] = 'fail'
            get_students_res['message'] = str(ex)
            return get_students_res

        print('Student details fetched successfully')
        log.info('Student details fetched successfully')
        get_students_res['data'] = data
        get_students_res['status'] = 'success'
        get_students_res['message'] = 'Student details fetched successfully'
        return get_students_res

    @staticmethod
    def edit_student(parameter_list):

        print('\n\nInside edit_student API: editing student\n\n')
        log.info('Inside edit_student API: editing student')

        edit_student_res = {}

        try:
            req_data = json.loads(parameter_list.body.decode('utf-8'))
            req_data = req_data['data']

            # req_data = json.loads(parameter_list.POST.get('data'))

        except Exception as ex:
            print('Error in edit_student API: req_data: %s' % ex)
            log.error('Error in edit_student API: req_data: %s' % ex)
            edit_student_res['status'] = 'fail'
            edit_student_res['message'] = str(ex)
            return edit_student_res

        try:

            current_student = Student.objects.get(id=req_data['id'])

            current_student.student_email = req_data['email']
            current_student.student_first_name = req_data['first_name']
            current_student.student_last_name = req_data['last_name']
            current_student.student_batch_id = Batch.objects.get(id=req_data['batch_id'])
            current_student.student_device_type = req_data['device_type']
            current_student.student_os_version = req_data['os_version']
            current_student.student_app_version = req_data['app_version']
            current_student.student_password = req_data['password']

            current_student.save()

        except Exception as ex:
            print('Error in edit_student API: editing Student: %s' % ex)
            log.error('Error in edit_student API: editing Student: %s' % ex)
            edit_student_res['status'] = 'fail'
            edit_student_res['message'] = str(ex)
            return edit_student_res

        if req_data['profile_pic'] != 'no image':

            try:

                req_image = req_data['profile_pic']
                req_image = req_image.replace(' ', '+')

                im = Image.open(BytesIO(base64.b64decode(req_image)))
                im.save('media/student_profile_picture/temp/student_pic.png', 'PNG')
                temp_post_img = File(open('media/student_profile_picture/temp/student_pic.png', 'rb'))
                temp_post_img.name = 'image.png'

                current_student.student_picture_url = temp_post_img

                current_student.save()

            except Exception as ex:
                print('Error in edit_student API: uploading image: %s' % ex)
                log.error('Error in edit_student API: uploading image: %s' % ex)
                edit_student_res['status'] = 'fail'
                edit_student_res['message'] = str(ex)
                return edit_student_res

        try:

            auth_user = User.objects.get(username=req_data['email'])
            auth_user.set_password(req_data['password'])
            auth_user.save()

        except Exception as ex:
            print('Error in edit_student API: updating password: %s' % ex)
            log.error('Error in edit_student API: updating password: %s' % ex)
            edit_student_res['status'] = 'fail'
            edit_student_res['message'] = str(ex)
            return edit_student_res

        msg = 'Student Updated successfully'
        log.info(msg)
        edit_student_res['status'] = 'success'
        edit_student_res['message'] = str(msg)
        return edit_student_res

    @staticmethod
    def add_student(parameter_list):
        print('\n\nInside add_student API: editing student\n\n')
        log.info('Inside add_student API: editing student')

        add_student_res = {}

        try:
            req_data = json.loads(parameter_list.body.decode('utf-8'))
            req_data = req_data['data']

            # req_data = json.loads(parameter_list.POST.get('data'))

        except Exception as ex:
            print('Error in add_student API: req_data: %s' % ex)
            log.error('Error in add_student API: req_data: %s' % ex)
            add_student_res['status'] = 'fail'
            add_student_res['message'] = str(ex)
            return add_student_res

        if User.objects.filter(username=req_data['email']).exists():
            ex = 'Error in add_student API: This student already exists'
            print('%s' % ex)
            log.error('%s' % ex)
            add_student_res['status'] = 'fail'
            add_student_res['message'] = str(ex)
            return add_student_res

        else:
            try:
                User.objects.create_user(
                    username=req_data['email'],
                    email=req_data['email'],
                    first_name=req_data['first_name'],
                    last_name=req_data['last_name'],
                    password=req_data['password'],
                ).save()
            except Exception as ex:
                print('Error in add_student API create admin user: %s' % ex)
                log.error('Error in signup API create admin user: %s' % ex)
                add_student_res['status'] = 'fail'
                add_student_res['message'] = str(ex)
                return add_student_res

            try:
                current_student = Student.objects.create(
                    student_user_id=User.objects.get(username=req_data['email']),
                    student_password=req_data['password'],
                    student_create_at=now(),
                    student_email=req_data['email'],
                    student_first_name=req_data['first_name'],
                    student_last_name=req_data['last_name'],
                    student_batch_id=Batch.objects.get(id=req_data['batch_id'])
                )

                current_student.save()

            except Exception as ex:
                print('Error in add_student API create student: %s' % ex)
                log.error('Error in add_student API create student: %s' % ex)
                add_student_res['status'] = 'fail'
                add_student_res['message'] = str(ex)
                return add_student_res

            if req_data['profile_pic'] != 'no image':

                try:

                    req_image = req_data['profile_pic']
                    req_image = req_image.replace(' ', '+')

                    im = Image.open(BytesIO(base64.b64decode(req_image)))
                    im.save('media/student_profile_picture/temp/student_pic.png', 'PNG')
                    temp_post_img = File(open('media/student_profile_picture/temp/student_pic.png', 'rb'))
                    temp_post_img.name = 'image.png'

                    current_student.student_picture_url = temp_post_img

                    current_student.save()

                except Exception as ex:
                    print('Error in add_student API: uploading image: %s' % ex)
                    log.error('Error in add_student API: uploading image: %s' % ex)
                    add_student_res['status'] = 'fail'
                    add_student_res['message'] = str(ex)
                    return add_student_res

        msg = 'Student added successfully'
        log.info(msg)
        add_student_res['status'] = 'success'
        add_student_res['message'] = str(msg)
        return add_student_res

    @staticmethod
    def admin_get_posts():

        print('\n\nInside admin_get_posts API: Getting all posts\n\n')
        log.info('Inside admin_get_posts API: Getting all posts')

        admin_get_posts_res = {}

        data = []

        try:

            all_posts = Post.objects.filter().order_by('-post_created_at')

            for one_post in all_posts:
                if one_post.post_is_enabled:
                    like_count = Like.objects.filter(like_post=one_post).count()

                    comment_count = Comment.objects.filter(comment_post=one_post, comment_is_enabled=True).count()

                    data.append({
                        'post_id': one_post.id,
                        'created_at': '%s' % R2DateTime.humanize_date(
                            datetime_from_utc_to_local(
                                one_post.post_created_at
                            )
                        ),
                        'text': str(one_post.post_text).replace("<p>", "").replace("</p>", ""),
                        'has_img': str(one_post.post_has_img),
                        'img_url': str('media/%s' % one_post.post_img_url),
                        'has_video': str(one_post.post_has_video),
                        'video_url': str(one_post.post_video),
                        'like_count': str(like_count),
                        'comment_count': str(comment_count),
                        'title': str(one_post.post_title).replace("<p>", "").replace("</p>", ""),
                        'batch_name': str(one_post.post_batch_id.batch_name),
                        'batch_id': str(one_post.post_batch_id.id)
                    })

        except Exception as ex:
            print('Error in admin_get_posts API: fetch posts: %s' % ex)
            log.error('Error in admin_get_posts API: fetch posts: %s' % ex)
            admin_get_posts_res['status'] = 'fail'
            admin_get_posts_res['message'] = str(ex)
            return admin_get_posts_res

        msg = 'Post successfully fetched'
        print(msg)
        log.info(msg)
        admin_get_posts_res['status'] = 'success'
        admin_get_posts_res['message'] = str(msg)
        admin_get_posts_res['data'] = data
        return admin_get_posts_res

    @staticmethod
    def admin_login(parameter_list):

        admin_login_res = {}

        try:
            req_data = json.loads(parameter_list.POST.get('data'))
        except Exception as ex:
            log.error('Error in admin_login API: req_data: %s' % ex)
            admin_login_res['status'] = 'fail'
            admin_login_res['message'] = str(ex)
            return admin_login_res

        r2_auth_res = UserProfile.r2_auth(
            username=req_data['username'],
            password=req_data['password'],
            request=parameter_list
        )

        if r2_auth_res['status'] is 'fail':
            log.error('Error in admin_login API: logging in')
            admin_login_res['status'] = 'fail'
            admin_login_res['message'] = str('Error in admin_login API: logging in')
            return admin_login_res
        else:
            log.info('logged in successfully')
            admin_login_res['status'] = 'success'
            admin_login_res['message'] = str('logged in successfully')
            return admin_login_res

    @staticmethod
    def admin_add_post(parameter_list):

        print('\n\nInside admin_add_post API: Getting all posts\n\n')
        log.info('Inside admin_add_post API: Getting all posts')

        admin_add_post_res = {}

        try:
            req_data = json.loads(parameter_list.body.decode('utf-8'))
            req_data = req_data['data']

            # req_data = json.loads(parameter_list.POST.get('data'))

        except Exception as ex:
            print('Error in admin_add_post API: req_data: %s' % ex)
            log.error('Error in admin_add_post API: req_data: %s' % ex)
            admin_add_post_res['status'] = 'fail'
            admin_add_post_res['message'] = str(ex)
            return admin_add_post_res

        try:

            if req_data['image'] != 'no image':

                req_image = req_data['image']
                req_image = req_image.replace(' ', '+')

                im = Image.open(BytesIO(base64.b64decode(req_image)))
                im.save('media/post_image/temp/post_pic.png', 'PNG')
                temp_post_img = File(open('media/post_image/temp/post_pic.png', 'rb'))
                temp_post_img.name = 'image.png'

            for batch in req_data['batches']:

                print('\n\n\n video url: ')
                print(req_data['video_url'])

                new_post = Post.objects.create(
                    post_title=req_data['title'],
                    post_text=req_data['text'],
                    post_batch_id=Batch.objects.get(id=batch['id']),
                    post_has_img=req_data['has_img'],
                    post_video=req_data['video_url'],
                    post_has_video=req_data['has_video']
                )
                new_post.save()

                if req_data['image'] != 'no image':

                    new_post.post_img_url = temp_post_img
                    new_post.save()

            msg = 'Post added successfully'
            print(msg)
            log.error(msg)
            admin_add_post_res['status'] = 'success'
            admin_add_post_res['message'] = str(msg)
            return admin_add_post_res

        except Exception as ex:
            print('Error in admin_add_post API: adding new post: %s' % ex)
            log.error('Error in admin_add_post API: adding new post: %s' % ex)
            admin_add_post_res['status'] = 'fail'
            admin_add_post_res['message'] = str(ex)
            return admin_add_post_res

    @staticmethod
    def admin_udpate_post(parameter_list):

        print('\n\nInside admin_udpate_post API: Getting all posts\n\n')
        log.info('Inside admin_udpate_post API: Getting all posts')

        admin_udpate_post_res = {}

        try:
            req_data = json.loads(parameter_list.body.decode('utf-8'))
            req_data = req_data['data']

            # req_data = json.loads(parameter_list.POST.get('data'))

        except Exception as ex:
            print('Error in admin_udpate_post API: req_data: %s' % ex)
            log.error('Error in admin_udpate_post API: req_data: %s' % ex)
            admin_udpate_post_res['status'] = 'fail'
            admin_udpate_post_res['message'] = str(ex)
            return admin_udpate_post_res

        try:

            current_post = Post.objects.get(id=req_data['post_id'])
            current_post.post_title = req_data['post_title']
            current_post.post_text = req_data['post_text']

            if req_data['video_url'] != 'no video':
                current_post.post_video = req_data['video_url']

            current_post.save()

            if req_data['img_url'] != 'no image':

                req_image = req_data['img_url']
                req_image = req_image.replace(' ', '+')

                im = Image.open(BytesIO(base64.b64decode(req_image)))
                im.save('media/post_image/temp/post_pic.png', 'PNG')
                temp_post_img = File(open('media/post_image/temp/post_pic.png', 'rb'))
                temp_post_img.name = 'image.png'

                current_post.post_img_url = temp_post_img
                current_post.save()

            msg = 'Post updated successfully'
            print(msg)
            log.error(msg)
            admin_udpate_post_res['status'] = 'success'
            admin_udpate_post_res['message'] = str(msg)
            return admin_udpate_post_res

        except Exception as ex:
            print('Error in admin_udpate_post API: updating post: %s' % ex)
            log.error('Error in admin_udpate_post API: updating post: %s' % ex)
            admin_udpate_post_res['status'] = 'fail'
            admin_udpate_post_res['message'] = str(ex)
            return admin_udpate_post_res

    @staticmethod
    def admin_get_assign_ans(parameter_list):

        print('\n\nInside admin_get_assign_ans API: Getting all assign answers\n\n')
        log.info('Inside admin_get_assign_ans API: Getting all assign answers')

        admin_udpate_post_res = {}

        assings = []

        try:
            req_data = json.loads(parameter_list.body.decode('utf-8'))
            req_data = req_data['data']

            # req_data = json.loads(parameter_list.POST.get('data'))

        except Exception as ex:
            print('Error in admin_get_assign_ans API: req_data: %s' % ex)
            log.error('Error in admin_get_assign_ans API: req_data: %s' % ex)
            admin_udpate_post_res['status'] = 'fail'
            admin_udpate_post_res['message'] = str(ex)
            return admin_udpate_post_res

        try:

            all_ass = Assignment.objects.filter(
                batch=Batch.objects.get(id=req_data['batch_id'])
            ).order_by('-id')

            for one_ass in all_ass:

                ass_ans = []

                all_ans = AssignmentAnswer.objects.filter(assignment=one_ass).order_by('-id')

                for one_ans in all_ans:
                    ass_ans.append({
                        'ans_id': one_ans.id,
                        'student_img': str(one_ans.student.student_picture_url),
                        'student_first_name': one_ans.student.student_first_name,
                        'student_last_name': one_ans.student.student_last_name,
                        'student_ans': one_ans.answer_text,
                        'student_marks': one_ans.answer_other_marks,
                        'submitted_at': '%s' % R2DateTime.humanize_date(
                            datetime_from_utc_to_local(
                                one_ans.submitted_at
                            )
                        ),
                        'student_id': str(one_ans.student.id)
                    })

                assings.append({
                    'ass_id': one_ass.id,
                    'ass_title': one_ass.title,
                    'ass_text': one_ass.text,
                    'ass_ans': ass_ans,
                    'ass_img': str(one_ass.img_url),
                    'ass_video': one_ass.video_url
                })

            msg = 'Assignment answers fetched successfully!'
            print(msg)
            log.info(msg)
            admin_udpate_post_res['status'] = 'success'
            admin_udpate_post_res['data'] = assings
            admin_udpate_post_res['message'] = str(msg)
            return admin_udpate_post_res

        except Exception as ex:
            print('Error in admin_get_assign_ans API: getting ans: %s' % ex)
            log.error('Error in admin_get_assign_ans API: getting ans: %s' % ex)
            admin_udpate_post_res['status'] = 'fail'
            admin_udpate_post_res['message'] = str(ex)
            return admin_udpate_post_res

    @staticmethod
    def admin_review_assign(parameter_list):

        print('\n\nInside admin_review_assign API: reviewing assignment answers\n\n')
        log.info('Inside admin_review_assign API: reviewing assignment answers')

        admin_review_assign_res = {}

        try:
            req_data = json.loads(parameter_list.body.decode('utf-8'))
            req_data = req_data['data']

            # req_data = json.loads(parameter_list.POST.get('data'))

        except Exception as ex:
            print('Error in admin_review_assign API: req_data: %s' % ex)
            log.error('Error in admin_review_assign API: req_data: %s' % ex)
            admin_review_assign_res['status'] = 'fail'
            admin_review_assign_res['message'] = str(ex)
            return admin_review_assign_res

        try:

            for one_ans in req_data['ans']:
                current_ans = AssignmentAnswer.objects.get(id=one_ans['ans_id'])
                current_ans.answer_other_marks = one_ans['marks']
                current_ans.status = 'Checked'
                current_ans.save()

                current_student = Student.objects.get(id=one_ans['student_id'])

                if not Notification.objects.filter(
                    notif_review_assignment=current_ans,
                    notif_student=current_student
                ).exists():
                    Notification.objects.create(
                        notif_text='Your Assignment <strong>%s</strong> has been reviewed.' % current_ans.assignment.title,
                        notif_review_assignment=current_ans,
                        notif_student=current_student,
                        redirect_to='Assignment'
                    ).save()

                    PushyAPI.prepare_notification(
                        student=current_student,
                        data_msg='Review Assignment',
                        body_text='%s, your Assignment: \"%s\" has been reviewed.' % (
                            current_student.student_first_name,
                            current_ans.assignment.title
                        )
                    )

            msg = 'Answers reviewed successfully'
            print(msg)
            log.error(msg)
            admin_review_assign_res['status'] = 'success'
            admin_review_assign_res['message'] = str(msg)
            return admin_review_assign_res

        except Exception as ex:
            print('Error in admin_review_assign API: reviewing assignment: %s' % ex)
            log.error('Error in admin_review_assign API: reviewing assignment: %s' % ex)
            admin_review_assign_res['status'] = 'fail'
            admin_review_assign_res['message'] = str(ex)
            return admin_review_assign_res

    @staticmethod
    def admin_get_topics(parameter_list):

        print('\n\nInside admin_get_topics API: fetching topics\n\n')
        log.info('Inside admin_get_topics API: fetching topics')

        admin_review_assign_res = {}

        data = []

        try:
            req_data = json.loads(parameter_list.body.decode('utf-8'))
            req_data = req_data['data']

            # req_data = json.loads(parameter_list.POST.get('data'))

        except Exception as ex:
            print('Error in admin_get_topics API: req_data: %s' % ex)
            log.error('Error in admin_get_topics API: req_data: %s' % ex)
            admin_review_assign_res['status'] = 'fail'
            admin_review_assign_res['message'] = str(ex)
            return admin_review_assign_res

        try:

            current_batch = Batch.objects.get(id=req_data['batch_id'])

            all_topics = ApplicationTopic.objects.filter(batch=current_batch).order_by('-id')

            for one_topic in all_topics:
                data.append({
                    'topic_id': one_topic.id,
                    'topic_text': one_topic.topic_text,
                    'topic_desc': one_topic.topic_desc
                })

            msg = 'Topics fetched successfully'
            print(msg)
            log.error(msg)
            admin_review_assign_res['status'] = 'success'
            admin_review_assign_res['data'] = data
            admin_review_assign_res['message'] = str(msg)
            return admin_review_assign_res

        except Exception as ex:
            print('Error in admin_get_topics API: req_data: %s' % ex)
            log.error('Error in admin_get_topics API: req_data: %s' % ex)
            admin_review_assign_res['status'] = 'fail'
            admin_review_assign_res['message'] = str(ex)
            return admin_review_assign_res

    @staticmethod
    def admin_get_appls(parameter_list):

        print('\n\nInside admin_get_topics API: fetching topics\n\n')
        log.info('Inside admin_get_topics API: fetching topics')

        admin_review_assign_res = {}

        data = []

        try:
            req_data = json.loads(parameter_list.body.decode('utf-8'))
            req_data = req_data['data']

            # req_data = json.loads(parameter_list.POST.get('data'))

        except Exception as ex:
            print('Error in admin_get_topics API: req_data: %s' % ex)
            log.error('Error in admin_get_topics API: req_data: %s' % ex)
            admin_review_assign_res['status'] = 'fail'
            admin_review_assign_res['message'] = str(ex)
            return admin_review_assign_res

        try:

            current_topic = ApplicationTopic.objects.get(id=req_data['topic_id'])

            all_appli = Application.objects.filter(topic=current_topic).order_by('-id')

            for one_appli in all_appli:
                data.append({
                    'app_id': one_appli.id,
                    'instance': one_appli.instance,
                    'effect': one_appli.effect,
                    'well': one_appli.well,
                    'unexpected': one_appli.unexpected,
                    'reflection': one_appli.reflection,
                    'different': one_appli.different,
                    'app_seen': one_appli.app_seen,
                    'app_attempt': one_appli.app_attempt,
                    'app_other_marks': one_appli.app_other_marks,
                    'student_id': one_appli.student.id,
                    'student_name': '%s %s' % (one_appli.student.student_first_name, one_appli.student.student_last_name),
                    'student_img': str(one_appli.student.student_picture_url)
                })

            msg = 'Applications fetched successfully'
            print(msg)
            log.error(msg)
            admin_review_assign_res['status'] = 'success'
            admin_review_assign_res['data'] = data
            admin_review_assign_res['message'] = str(msg)
            return admin_review_assign_res

        except Exception as ex:
            print('Error in admin_get_topics API: fetching app list: %s' % ex)
            log.error('Error in admin_get_topics API: fetching app list: %s' % ex)
            admin_review_assign_res['status'] = 'fail'
            admin_review_assign_res['message'] = str(ex)
            return admin_review_assign_res

    @staticmethod
    def admin_review_application(parameter_list):

        print('\n\nInside admin_review_application API: fetching topics\n\n')
        log.info('Inside admin_review_application API: fetching topics')

        admin_review_assign_res = {}

        try:
            req_data = json.loads(parameter_list.body.decode('utf-8'))
            req_data = req_data['data']

            # req_data = json.loads(parameter_list.POST.get('data'))

        except Exception as ex:
            print('Error in admin_review_application API: req_data: %s' % ex)
            log.error('Error in admin_review_application API: req_data: %s' % ex)
            admin_review_assign_res['status'] = 'fail'
            admin_review_assign_res['message'] = str(ex)
            return admin_review_assign_res

        try:

            for one_app in req_data['app_result']:
                current_app = Application.objects.get(id=one_app['app_id'])
                current_app.app_other_marks = one_app['marks']
                current_app.app_status = 'Checked'
                current_app.save()

                current_student = Student.objects.get(id=one_app['student_id'])

                if not Notification.objects.filter(
                    notif_review_app=current_app,
                    notif_student=current_student
                ).exists():
                    Notification.objects.create(
                        notif_text='Your Application: \"<strong>%s</strong>\" has been reviewed.' % current_app.topic.topic_text,
                        notif_review_app=current_app,
                        notif_student=current_student,
                        redirect_to='Application'
                    ).save()

                    PushyAPI.prepare_notification(
                        student=current_student,
                        data_msg='Review Application',
                        body_text='%s, your Application: \"%s\" has been reviewed.' % (
                            current_student.student_first_name,
                            current_app.topic.topic_text
                        )
                    )

            msg = 'Application reviewed successfully'
            print(msg)
            log.error(msg)
            admin_review_assign_res['status'] = 'success'
            admin_review_assign_res['message'] = str(msg)
            return admin_review_assign_res

        except Exception as ex:
            print('Error in admin_review_application API: upd: %s' % ex)
            log.error('Error in admin_review_application API: upd: %s' % ex)
            admin_review_assign_res['status'] = 'fail'
            admin_review_assign_res['message'] = str(ex)
            return admin_review_assign_res

    @staticmethod
    def admin_delete_post(parameter_list):

        print('\n\nInside admin_delete_post API: deleting post\n\n')
        log.info('Inside admin_delete_post API: deleting post')

        admin_delete_post_res = {}

        try:
            req_data = json.loads(parameter_list.body.decode('utf-8'))
            req_data = req_data['data']

            # req_data = json.loads(parameter_list.POST.get('data'))

        except Exception as ex:
            print('Error in admin_delete_post API: req_data: %s' % ex)
            log.error('Error in admin_delete_post API: req_data: %s' % ex)
            admin_delete_post_res['status'] = 'fail'
            admin_delete_post_res['message'] = str(ex)
            return admin_delete_post_res

        try:

            Post.objects.get(id=req_data['post_id']).delete()

        except Exception as ex:
            print('Error in admin_delete_post API: deleting post: %s' % ex)
            log.error('Error in admin_delete_post API: deleting post: %s' % ex)
            admin_delete_post_res['status'] = 'fail'
            admin_delete_post_res['message'] = str(ex)
            return admin_delete_post_res

        msg = 'Post has been deleted succesfully'

        print(msg)
        log.info(msg)
        admin_delete_post_res['status'] = 'success'
        admin_delete_post_res['message'] = str(msg)
        return admin_delete_post_res

    @staticmethod
    def admin_batch_performance(parameter_list):

        print('\n\nInside admin_batch_performance API: deleting post\n\n')
        log.info('Inside admin_batch_performance API: deleting post')

        admin_batch_performance_res = {}

        try:
            req_data = json.loads(parameter_list.body.decode('utf-8'))
            req_data = req_data['data']

            # req_data = json.loads(parameter_list.POST.get('data'))

        except Exception as ex:
            print('Error in admin_batch_performance API: req_data: %s' % ex)
            log.error('Error in admin_batch_performance API: req_data: %s' % ex)
            admin_batch_performance_res['status'] = 'fail'
            admin_batch_performance_res['message'] = str(ex)
            return admin_batch_performance_res

        try:

            data = []

            current_batch = Batch.objects.filter(id=req_data['batch_id'])
            column_names = ['Name', 'Total Score']

            all_student = Student.objects.filter(student_batch_id=current_batch)

            student_assigns = Assignment.objects.filter(batch=current_batch).order_by('id')

            for one_student_assign in student_assigns:
                column_name = 'Assign' + str(one_student_assign.id) + ': ' + one_student_assign.title
                column_names.append(column_name)

            student_app_topic = ApplicationTopic.objects.filter(batch=current_batch).order_by('id')

            for one_student_app_topic in student_app_topic:
                column_name = 'App' + str(one_student_app_topic.id) + ': ' + one_student_app_topic.topic_text
                column_names.append(column_name)

            student_quizzes = Quiz.objects.filter(quiz_batch=current_batch).order_by('id')

            for one_student_quiz in student_quizzes:
                column_name = 'Quiz' + str(one_student_quiz.id) + ': ' + one_student_quiz.quiz_desc
                column_names.append(column_name)

            for one_student in all_student:

                student_marks = get_student_marks(one_student, one_student)

                current_batch = one_student.student_batch_id

                all_quiz = Quiz.objects.filter(quiz_batch=current_batch)

                total_quiz_questions = 0

                for one_quiz in all_quiz:
                    total_quiz_questions = total_quiz_questions + Question.objects.filter(question_quiz=one_quiz).count()

                total_assign = Assignment.objects.filter(batch=current_batch).count()

                total_topic = ApplicationTopic.objects.filter(batch=current_batch).count()

                # START OF ASSIGNMENT MARKS LIST

                ans_marks_list = []

                for one_student_assign in student_assigns:

                    if AssignmentAnswer.objects.filter(assignment=one_student_assign, student=one_student).exists():
                        assign_ans = AssignmentAnswer.objects.get(assignment=one_student_assign, student=one_student)

                        # 'Assign' + str(one_student_assign.id) + ' : ' +
                        ans_marks_list.append({
                            'marks': str(int(assign_ans.answer_seen) + int(assign_ans.answer_attempt) + int(assign_ans.answer_other_marks)),
                            'out_of': '10'
                            # 'out_of': str(total_assign * 10)
                        })
                    else:
                        ans_marks_list.append({
                            'marks': '-',
                            'out_of': '-'
                        })

                # END OF ASSIGNMENT MARKS LIST

                # START OF APPLICATION MARKS LIST

                for one_student_app_topic in student_app_topic:

                    if Application.objects.filter(topic=one_student_app_topic, student=one_student).exists():
                        app_ans = Application.objects.get(topic=one_student_app_topic, student=one_student)
                        ans_marks_list.append({
                            'marks': str(app_ans.app_seen + app_ans.app_attempt + app_ans.app_other_marks),
                            'out_of': '10'
                            # 'out_of': str(total_topic * 10)
                        })
                    else:
                        ans_marks_list.append({
                            'marks': '-',
                            'out_of': '-'
                        })

                # END OF APPLICATION MARKS LIST

                # START OF QUIZ MARKS LIST

                for one_student_quiz in student_quizzes:

                    _total_quiz_questions = Question.objects.filter(question_quiz=one_student_quiz).count()

                    student_questions = Question.objects.filter(question_quiz=one_student_quiz)

                    student_quiz_marks = 0

                    for one_student_questions in student_questions:

                        if Answer.objects.filter(answer_question=one_student_questions, answer_student=one_student).exists():
                            quiz_ans = Answer.objects.get(answer_question=one_student_questions, answer_student=one_student)
                            student_quiz_marks = student_quiz_marks + quiz_ans.answer_seen + quiz_ans.answer_attempt + quiz_ans.answer_other_marks

                    if student_quiz_marks is 0:
                        ans_marks_list.append({
                            'marks': '-',
                            'out_of': '-'
                        })
                    else:
                        ans_marks_list.append({
                            'marks': str(student_quiz_marks),
                            'out_of': str(_total_quiz_questions * 5)
                        })

                # END OF QUIZ MARKS LIST

                data.append({
                    'id': str(one_student.id),
                    'picture_url': str(one_student.student_picture_url),
                    'first_name': str(one_student.student_first_name),
                    'last_name': str(one_student.student_last_name),
                    'full_name': '%s %s' % (
                        str(one_student.student_first_name),
                        str(one_student.student_last_name)
                    ),
                    'batch_id': str(one_student.student_batch_id.id),
                    'batch_name': str(one_student.student_batch_id.batch_name),
                    'email': str(one_student.student_email),
                    'device': str(one_student.student_device_type),
                    'os_version': str(one_student.student_os_version),
                    'app_version': str(one_student.student_app_version),
                    'create_at': str(one_student.student_create_at),
                    'password': one_student.student_password,
                    'quiz_marks': student_marks['quiz'],
                    'ass_marks': student_marks['ass'],
                    'app_marks': student_marks['app'],
                    'total_marks': student_marks['total'],
                    'quiz_outof': total_quiz_questions * QUIZ_QUESTION_OUT_OF,
                    'app_outof': total_topic * APPLICATION_OUT_OF,
                    'ass_outof': total_assign * ASSIGNMENT_OUT_OF,
                    'total_outof': (total_quiz_questions * QUIZ_QUESTION_OUT_OF) + (total_topic * APPLICATION_OUT_OF) + (total_assign * ASSIGNMENT_OUT_OF),
                    'ans_marks_list': ans_marks_list
                })

        except Exception as ex:
            print('Error in admin_batch_performance(): %s' % ex)
            log.error('Error in admin_batch_performance(): %s' % ex)
            admin_batch_performance_res['data'] = ''
            admin_batch_performance_res['status'] = 'fail'
            admin_batch_performance_res['message'] = str(ex)
            return admin_batch_performance_res

        print('Student details fetched successfully')
        log.info('Student details fetched successfully')
        admin_batch_performance_res['column_names'] = column_names
        admin_batch_performance_res['data'] = data
        admin_batch_performance_res['status'] = 'success'
        admin_batch_performance_res['message'] = 'Student details fetched successfully'
        return admin_batch_performance_res

    @staticmethod
    def get_quiz_quest_to_choose(parameter_list):
        log.info('Inside get_quiz_quest_to_choose API: fetching questions')

        get_quiz_questions_res = {}

        # data = []
        #
        # try:
        #     req_data = json.loads(parameter_list.body.decode('utf-8'))
        #     req_data = req_data['data']
        #
        #     # req_data = json.loads(parameter_list.POST.get('data'))
        # except Exception as ex:
        #     log.error('Error in get_quiz_quest_to_choose API: req_data: %s' % ex)
        #     get_quiz_questions_res['status'] = 'fail'
        #     get_quiz_questions_res['message'] = str(ex)
        #     return get_quiz_questions_res

        try:

            all_quiz = Quiz.objects.filter()

            quiz_list = []

            for current_quiz in all_quiz:

                # current_quiz = Quiz.objects.get(id=req_data['quiz_id'])

                all_question = Question.objects.filter(question_quiz=current_quiz).order_by('id')

                question_list = []

                for one_question in all_question:

                    question_list.append({
                        # 'question_id': one_question.id,
                        'title': one_question.question_text,
                        'type': one_question.question_type,
                        'option_a': one_question.question_op_a,
                        'option_b': one_question.question_op_b,
                        'option_c': one_question.question_op_c,
                        'option_d': one_question.question_op_d,
                        'correct_ans': one_question.question_correct_ans
                    })

                quiz_list.append({
                    'title': current_quiz.quiz_desc,
                    'questions': question_list
                })

            msg = 'Questions fetched successfully'
            log.info(msg)
            get_quiz_questions_res['data'] = quiz_list
            get_quiz_questions_res['status'] = 'success'
            get_quiz_questions_res['message'] = str(msg)
            return get_quiz_questions_res

        except Exception as ex:
            log.error('Error in get_quiz_quest_to_choose API: fetching question: %s' % ex)
            get_quiz_questions_res['status'] = 'fail'
            get_quiz_questions_res['message'] = str(ex)
            return get_quiz_questions_res

    @staticmethod
    def admin_view_badges(parameter_list):
        log.info('Inside admin_view_badges API: fetching badges')

        admin_view_badges_res = {}

        try:

            badge_list = []

            all_badge = Badge.objects.filter()

            for one_badge in all_badge:
                badge_list.append({
                    'id': one_badge.id,
                    'name': one_badge.name,
                    'desc': one_badge.desc,
                    'image': str(one_badge.image)
                })

        except Exception as ex:
            log.error('Error in admin_view_badges API: fetching badges: %s' % ex)
            admin_view_badges_res['status'] = 'fail'
            admin_view_badges_res['message'] = str(ex)
            return admin_view_badges_res

        admin_view_badges_res['badge_list'] = badge_list
        admin_view_badges_res['message'] = 'Badges fetched successfully'
        admin_view_badges_res['status'] = 'success'
        log.info(admin_view_badges_res['message'])
        return admin_view_badges_res

    @staticmethod
    def admin_add_badge(parameter_list):
        log.info('Inside admin_add_badge API: adding badges')

        admin_add_badge_res = {}

        data = []

        try:
            req_data = json.loads(parameter_list.body.decode('utf-8'))
            req_data = req_data['data']

            # req_data = json.loads(parameter_list.POST.get('data'))
        except Exception as ex:
            log.error('Error in admin_add_badge API: req_data: %s' % ex)
            admin_add_badge_res['status'] = 'fail'
            admin_add_badge_res['message'] = str(ex)
            return admin_add_badge_res

        try:

            new_badge = Badge.objects.create(
                name=req_data['name'],
                desc=req_data['desc']
            )
            new_badge.save()

        except Exception as ex:
            log.error('Error in admin_add_badge API: adding badges: %s' % ex)
            admin_add_badge_res['status'] = 'fail'
            admin_add_badge_res['message'] = str(ex)
            return admin_add_badge_res

        try:

            req_image = req_data['image']
            req_image = req_image.replace(' ', '+')

            im = Image.open(BytesIO(base64.b64decode(req_image)))
            im.save('media/badge_image/temp/badge_image.png', 'PNG')
            temp_post_img = File(open('media/badge_image/temp/badge_image.png', 'rb'))
            temp_post_img.name = 'image.png'

            new_badge.image = temp_post_img
            new_badge.save()

        except Exception as ex:
            print('Error in admin_add_badge API: uploading image: %s' % ex)
            log.error('Error in admin_add_badge API: uploading image: %s' % ex)
            admin_add_badge_res['status'] = 'fail'
            admin_add_badge_res['message'] = str(ex)
            return admin_add_badge_res

        admin_add_badge_res['message'] = 'Badges added successfully'
        admin_add_badge_res['status'] = 'success'
        log.info(admin_add_badge_res['message'])
        return admin_add_badge_res

    @staticmethod
    def update_student_badges(parameter_list):
        log.info('Inside update_student_badges API: updating student badges')

        update_student_badges_res = {}

        data = []

        try:
            req_data = json.loads(parameter_list.body.decode('utf-8'))
            req_data = req_data['data']

            # req_data = json.loads(parameter_list.POST.get('data'))
        except Exception as ex:
            log.error('Error in update_student_badges API: req_data: %s' % ex)
            update_student_badges_res['status'] = 'fail'
            update_student_badges_res['message'] = str(ex)
            return update_student_badges_res

        try:

            current_student = Student.objects.get(id=req_data['student_id'])

            for one_badge in req_data['badge_list']:

                if one_badge['has']:

                    current_badge = Badge.objects.get(id=one_badge['id'])

                    if not StudentBadge.objects.filter(
                        student=current_student,
                        badge=current_badge
                    ).exists():
                        StudentBadge.objects.create(
                            student=current_student,
                            badge=current_badge
                        ).save()

                if not one_badge['has']:

                    current_badge = Badge.objects.get(id=one_badge['id'])

                    if StudentBadge.objects.filter(
                        student=current_student,
                        badge=current_badge
                    ).exists():
                        StudentBadge.objects.get(
                            student=current_student,
                            badge=current_badge
                        ).delete()

        except Exception as ex:
            log.error('Error in update_student_badges API: updating student badge: %s' % ex)
            update_student_badges_res['status'] = 'fail'
            update_student_badges_res['message'] = str(ex)
            return update_student_badges_res

        update_student_badges_res['message'] = 'Student Badges updated successfully'
        log.info(update_student_badges_res['message'])
        update_student_badges_res['status'] = 'success'
        return update_student_badges_res
