from pyfcm import FCMNotification

push_service = FCMNotification(api_key="AAAAm7WZSgs:APA91bEtIkVJdK_dVnRvfHrnRgQm5y3WL5bdhm4WNvarrBQWYELpcS-Gjr3C8u5iLX0GkT79b3jVWHu5EGPKP6tvr6zrC7w0xjiiX-vo7In8MUNdrDqzZnY9_M5PErhHWLREr5arBBBi")

registration_id = "f1oLvxtvIN8:APA91bHVrK_Qcz22fVlnITN6DTf6z2AOqxxxvDsh8uInUap_wmAi9f_F8MIbrWEHxMpfiH-n_WIxfWg_IF1QGmV89Jz45rSKweB6Rq7QB5x5VGGKi_YtE-D-0BobctikxdIhAy6vMCAh"
message_title = "Deutchland deutchland"
message_body = "Uber Alles"
result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title, message_body=message_body)
print (result)