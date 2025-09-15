# payment, views.py:
from rest_framework.response import Response
from rest_framework import status, viewsets, generics, permissions

import uuid
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponseRedirect
from sslcommerz_lib import SSLCOMMERZ 
from datetime import datetime
from rest_framework.decorators import api_view, action
import os
from django.utils import timezone
from .models import Payment
from .serializers import PaymentSerializer
from drf_yasg.utils import swagger_auto_schema
import logging
from django.contrib.auth import get_user_model

User = get_user_model()

logger = logging.getLogger(__name__)

class IsOwnerOrStaff(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or staff to view it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return obj.user == request.user or request.user.is_staff
        
        # Write permissions are only allowed to the staff.
        return request.user.is_staff
    
class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing payments.
    - Staff users can see all payments.
    - Regular users can only see their own payments.
    """
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Check if this is a schema generation request
        if getattr(self, 'swagger_fake_view', False):
            # Return an empty queryset for schema generation
            return Payment.objects.none()
            
        user = self.request.user
        if user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(user=user)
    
    def retrieve(self, request, *args, **kwargs):
        """
        Override to use transaction_id instead of pk
        """
        # Check if this is a schema generation request
        if getattr(self, 'swagger_fake_view', False):
            # Return an empty response for schema generation
            return Response({})
            
        transaction_id = kwargs.get('pk')
        queryset = self.get_queryset().filter(transaction_id=transaction_id)
        payment = get_object_or_404(queryset)
        serializer = self.get_serializer(payment)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_description="Get only the current user's payments",
        responses={200: PaymentSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def my_payments(self, request):
        """
        Get only the current user's payments
        """
        # Check if this is a schema generation request
        if getattr(self, 'swagger_fake_view', False):
            # Return an empty response for schema generation
            return Response({})
            
        payments = Payment.objects.filter(user=request.user)
        serializer = self.get_serializer(payments, many=True)
        return Response(serializer.data)

"""
List All Payments: GET /api/v1/payments/
Get Payment by Transaction ID: GET /api/v1/payments/{transaction_id}/
Get Current User's Payments (Custom Action): GET /api/v1/payments/my_payments/
"""


class PaymentListAPIView(generics.ListAPIView):
    """
    API endpoint for listing payments.
    - Staff users can see all payments.
    - Regular users can only see their own payments.
    """
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(user=user)

class PaymentDetailAPIView(generics.RetrieveAPIView):
    """
    API endpoint for retrieving a specific payment.
    - Staff users can see any payment.
    - Regular users can only see their own payments.
    """
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrStaff]
    queryset = Payment.objects.all()
    lookup_field = 'transaction_id'    
    

@api_view(['POST'])
def initiate_payment(request):
    user = request.user
    amount = request.data.get("amount")
    #order_id= request.data.get("orderId")
    num_items = request.data.get("numItems")
    unique_id = uuid.uuid4().hex  # random 32-char hex string
    tran_id = f"{user.id}_{unique_id}" if user.is_authenticated else unique_id # alternative

    sslcommerz_settings = { 'store_id': 'anupc68bfa8f415e23', 'store_pass': 'anupc68bfa8f415e23@ssl', 'issandbox': True } # info from my sandbox account email, use .env file if production.
    sslcz = SSLCOMMERZ(sslcommerz_settings)
    post_body = {}
    post_body['total_amount'] = amount
    post_body['currency'] = "BDT"
    #post_body['tran_id'] = f"txn_{order_id}" # in phimart project
    post_body['tran_id'] = f"{tran_id}"
    post_body['success_url'] = f"{settings.BACKEND_URL}/api/v1/payment/success/"
    post_body['fail_url'] = f"{settings.BACKEND_URL}/api/v1/payment/fail/"
    post_body['cancel_url'] = f"{settings.BACKEND_URL}/api/v1/payment/cancel/"
    post_body['ipn_url']     = f"{settings.BACKEND_URL}/api/v1/payment/ipn/"   # <--- server-to-server POST
    post_body['emi_option'] = 0
    post_body['cus_name'] = user.full_name
    post_body['cus_email'] = user.email
    post_body['cus_phone'] = user.phone_number
    post_body['cus_add1'] = user.address
    post_body['cus_city'] = "Dhaka"
    post_body['cus_country'] = "Bangladesh"
    post_body['shipping_method'] = "NO"
    post_body['multi_card_name'] = ""
    post_body['num_of_item'] = num_items
    post_body['product_name'] = "e-commerce product"
    post_body['product_category'] = "Various"
    post_body['product_profile'] = "general"

    response = sslcz.createSession(post_body) # API response
    # print('from initiate_payment function :', response)
    # return Response(response)  # post request at: http://127.0.0.1:8000/api/payment/initiate/  # "GatewayPageURL"
    if response.get('status') == 'SUCCESS':
        return Response({'payment_url': response["GatewayPageURL"]})
    return Response({'error':response["failedreason"]}, status=status.HTTP_400_BAD_REQUEST)
                     





@api_view(['POST'])
def payment_success(request):
    # get data
    tran_id = request.data.get("tran_id")
    total_amount = request.data.get("amount")
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("request.data =",request.data)  # example print below (in phimart)
    # Use an absolute path so you know where the file will be created
    log_filename = "payment_success_log.txt"
    log_path = os.path.join(settings.BASE_DIR, log_filename)  # BASE_DIR is project root
    # Ensure directory exists (usually BASE_DIR exists, but safe)
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    # Write to file with error handling
    if settings.DEBUG:
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write("############ inside payment_success ############\n")
                f.write(f"tran_id : {tran_id}\n")
                f.write(f"total_amount : {total_amount}\n")
                f.write(f"current time : {current_time}\n\n")
        except Exception as e:
            # log the exception to console and logger so you can see it in runserver output
            logger.exception("Failed to write payment_success log")
            print("Failed to write payment_success log")
            # optionally return 500 so frontend knows it failed
            return JsonResponse({"error": "Failed to write log"}, status=500)
    # Continue with existing logic, guarded by try/except
    try:
        # get user and set is_subscribed = True, save payment history
        user_id = tran_id.split('_')[0]
        user = User.objects.get(id=user_id)
        user.is_subscribed = True
        user.save()
        
        # Save payment details to the Payment model
        payment = Payment.objects.create(
            user=user,
            transaction_id=tran_id,
            amount=total_amount,
            status='success',
            payment_date=timezone.now()
        )
        
    except Exception as e:
        logger.exception("Failed to update order for tran_id=%s", tran_id)
        # return error response or handle as you need
        return JsonResponse({"error": f"payment history update failed for transaction id : {tran_id}"}, status=500)
    # If frontend expects redirect, keep it. If it's an API call, consider returning JSON.
    #return HttpResponseRedirect(f"{settings.FRONTEND_URL}/dashboard/orders/") # remove orders endpoint
    return HttpResponseRedirect(f"{settings.FRONTEND_URL}/payment/success")
    # or: return JsonResponse({"ok": True})




@api_view(['POST'])
def payment_cancel(request):
    return HttpResponseRedirect(f"{settings.FRONTEND_URL}/payment/cancel")


@api_view(['POST'])
def payment_fail(request):    
    return HttpResponseRedirect(f"{settings.FRONTEND_URL}/payment/fail")
