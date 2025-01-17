from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
import json

# ? sandbox merchant
if settings.SANDBOX:
    sandbox = 'sandbox'
else:
    sandbox = 'www'

ZP_API_REQUEST = f"https://www.zarinpal.com/pg/rest/WebGate/PaymentRequest.json"
ZP_API_VERIFY = f"https://www.zarinpal.com/pg/rest/WebGate/PaymentVerification.json"
ZP_API_STARTPAY = f"https://www.zarinpal.com/pg/StartPay/"

amount = 1000000
description = "توضیحات مربوط به تراکنش را در این قسمت وارد کنید"  
phone = '09146692159'
CallbackURL = 'http://127.0.0.1:8000/verify/'


class SendRequestView(APIView):
    def get(self, request, *args, **kwargs):
        data = {
            "MerchantID": settings.MERCHANT,
            "Amount": amount,
            "Description": description,
            "Phone": phone,
            "CallbackURL": CallbackURL,
            "ff": "DDD"
        }
        data = json.dumps(data)
        headers = {'content-type': 'application/json', 'content-length': str(len(data))}
        try:
            response = requests.post(ZP_API_REQUEST, data=data, headers=headers, timeout=10)
            if response.status_code == 200:
                response_data = response.json()
                if response_data['Status'] == 100:
                    return Response({'status': 200, 'url': ZP_API_STARTPAY + str(response_data['Authority']),'D':'DDD','authority': response_data['Authority']}, status=status.HTTP_200_OK)
                else:
                    return Response({'status': False, 'code': str(response_data['Status'])},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'status': False, 'code': 'unknown error', 'response': response.text},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except requests.exceptions.Timeout:
            return Response({'status': False, 'code': 'timeout'}, status=status.HTTP_408_REQUEST_TIMEOUT)
        except requests.exceptions.ConnectionError:
            return Response({'status': False, 'code': 'connection error'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

class VerifyView(APIView):
    def get(self, request, *args, **kwargs):
        authority = request.data.get('authority')
        if not authority:
            return Response({'status': False, 'code': 'missing authority'}, status=status.HTTP_400_BAD_REQUEST)

        data = {
            "MerchantID": settings.MERCHANT,
            "Amount": amount,
            "Authority": authority,
            "FF": "DDD"
        }
        data = json.dumps(data)
        headers = {'content-type': 'application/json', 'content-length': str(len(data))}

        try:
            response = requests.post(ZP_API_VERIFY, data=data, headers=headers)

            if response.status_code == 200:
                response_data = response.json()
                if response_data['Status'] == 100:
                    return Response({'status': True, 'RefID': response_data['RefID']}, status=status.HTTP_200_OK)
                else:
                    return Response({'status': False, 'code': str(response_data['Status'])}, status=status.HTTP_400_BAD_REQUEST)

            return Response({'status': False, 'code': 'unknown error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except requests.exceptions.Timeout:
            return Response({'status': False, 'code': 'timeout'}, status=status.HTTP_408_REQUEST_TIMEOUT)
        except requests.exceptions.ConnectionError:
            return Response({'status': False, 'code': 'connection error'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
