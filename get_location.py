from pyicloud import PyiCloudService
import sys
import time

DEVICE_NUMBER = 2
#以下は接続するicloudのアカウントとパスワードを記載します。
api = PyiCloudService('************', '***********')

#ここから2段認証を実施する。
if api.requires_2fa:
    import click
    print ("Two-factor authentication required. Your trusted devices are:")

    devices = api.trusted_devices
    for i, device in enumerate(devices):
        print ("  %s: %s" % (i, device.get('deviceName',
            "SMS to %s" % device.get('phoneNumber'))))

    device = click.prompt('Which device would you like to use?', default=0)
    device = devices[device]
    if not api.send_verification_code(device):
        print ("Failed to send verification code")
        sys.exit(1)

    code = click.prompt('Please enter validation code')
    if not api.validate_verification_code(device, code):
        print ("Failed to verify verification code")
        sys.exit(1)

def get_oauth():
    auth = api.devices[DEVICE_NUMBER].location()
    return auth

if __name__ == '__main__':
    auth = str(get_oauth())
    eval_auth = eval(auth)
    is0 = auth.find('isOld')
    pst = auth.find('positionType')
    lat = eval_auth['latitude']
    lon = eval_auth['longitude']
    print(lat, lon)
    time.sleep(5)
    auth = str(get_oauth())
    eval_auth = eval(auth)
    is0 = auth.find('isOld')
    pst = auth.find('positionType')
    lat = eval_auth['latitude']
    lon = eval_auth['longitude']
    print(lat, lon)
    

# https://nllllll.com/python/python-pyicloud/