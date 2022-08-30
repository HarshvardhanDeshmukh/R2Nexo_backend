import json
import urllib.request
import urllib.parse

from r2.logger import log


class PushyAPI:
    @staticmethod
    def send_push_notification(data, notification, tokens):
        # Insert your Pushy Secret API Key here
        api_key = '65c36d5d2066e5e440a2c4da699d49c2df04eb97b23562794feb8bd2c7c59ebb'

        # Set URL to Send Notifications API endpoint
        req = urllib.request.Request('https://api.pushy.me/push?api_key=' + api_key)

        # Set Content-Type header since we're sending JSON
        req.add_header('Content-Type', 'application/json')

        # Actually send the push
        try:
            # Set json data
            json_data = dict()
            json_data['data'] = data
            json_data['tokens'] = tokens
            json_data['notification'] = notification
            json_data2 = json.dumps(json_data).encode('utf8')
            req.add_header('Content-Length', len(json_data2))
            print("JSON Data 2: %s" % json_data2)
            response = urllib.request.urlopen(req, json_data2)

            log.info('Response from Pushy API: %s ' % response)

        except Exception as e:
            print("Error in sending notification. Error in Pushy: %s" % str(e))

    @staticmethod
    def prepare_notification(student, data_msg, body_text):

        if student.student_device_token is not None:

            pushy_data = {
                'message': body_text,
            }

            try:

                from r2_app.models import Notification
                unread_count = Notification.objects.filter(
                    notif_student=student,
                    notif_read=False
                ).count()
                PushyAPI.send_push_notification(
                    data=pushy_data,
                    notification={
                        'body': body_text,
                        'sound': 'ping.aiff',
                        'badge': unread_count
                    },
                    tokens=[str(student.student_device_token)]
                )
            except Exception as ex:
                log.error('%s: Unable to send push notification: %s ' % (data_msg, ex))
