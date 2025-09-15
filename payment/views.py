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

from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes

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
    """
    Initiate SSLCommerz session and return payment_url or JSON error.
    """
    user = request.user
    # Require authentication - if you want to allow guest payments,
    # change this logic accordingly.
    if not user or not user.is_authenticated:
        return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

    # Validate amount
    try:
        amount = float(request.data.get("amount", 0))
    except (TypeError, ValueError):
        return Response({"error": "Invalid amount"}, status=status.HTTP_400_BAD_REQUEST)

    if amount <= 0:
        return Response({"error": "Amount must be greater than 0"}, status=status.HTTP_400_BAD_REQUEST)

    num_items = request.data.get("numItems", 1)

    # make a safe tran_id: user.id + random hex
    unique_id = uuid.uuid4().hex
    tran_id = f"{user.id}_{unique_id}"

    # prepare SSLCommerz config from environment or settings
    sslcommerz_settings = {
        'store_id': getattr(settings, 'SSLCOMMERZ_STORE_ID', 'anupc68bfa8f415e23'),
        'store_pass': getattr(settings, 'SSLCOMMERZ_STORE_PASS', 'anupc68bfa8f415e23@ssl'),
        'issandbox': getattr(settings, 'SSLCOMMERZ_SANDBOX', True)
    }

    # create instance
    try:
        sslcz = SSLCOMMERZ(sslcommerz_settings)
    except Exception as e:
        logger.exception("Failed to initialize SSLCOMMERZ")
        return Response({"error": "Payment gateway initialization failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # safe getter for user attributes (avoid AttributeError)
    def _safe(u, attr, default=""):
        return getattr(u, attr, default) or default

    post_body = {
        'total_amount': amount,
        'currency': "BDT",
        'tran_id': tran_id,
        'success_url': f"{settings.BACKEND_URL.rstrip('/')}/payment/success/",
        'fail_url': f"{settings.BACKEND_URL.rstrip('/')}/payment/fail/",
        'cancel_url': f"{settings.BACKEND_URL.rstrip('/')}/payment/cancel/",
        'ipn_url': f"{settings.BACKEND_URL.rstrip('/')}/payment/ipn/",
        'emi_option': 0,
        'cus_name': _safe(user, 'full_name', _safe(user, 'get_full_name', '')),
        'cus_email': _safe(user, 'email', ''),
        'cus_phone': _safe(user, 'phone_number', ''),
        'cus_add1': _safe(user, 'address', ''),
        'cus_city': "Dhaka",
        'cus_country': "Bangladesh",
        'shipping_method': "NO",
        'multi_card_name': "",
        'num_of_item': num_items,
        'product_name': "subscription",
        'product_category': "Subscription",
        'product_profile': "general",
    }

    # Call createSession inside try/except and log full response
    try:
        response = sslcz.createSession(post_body)
    except Exception:
        logger.exception("sslcommerz.createSession failed for tran_id=%s post_body=%s", tran_id, post_body)
        return Response({"error": "Payment gateway session creation failed"}, status=status.HTTP_502_BAD_GATEWAY)

    # Defensive checks on response dict
    status_val = response.get('status')
    gateway_url = response.get('GatewayPageURL') or response.get('gateway_url') or response.get('redirect_url')

    # Log the raw response for debugging (use caution in prod)
    logger.debug("sslcommerz response for tran_id=%s: %s", tran_id, response)

    if status_val == 'SUCCESS' and gateway_url:
        return Response({'payment_url': gateway_url})
    else:
        # Prefer any supplied reason, otherwise dump the response to help debugging
        failed_reason = response.get('failedreason') or response.get('failed_reason') or response.get('error') or str(response)
        # return 400 so frontend knows it was a client/gateway issue
        return Response({'error': failed_reason}, status=status.HTTP_400_BAD_REQUEST)
                     





@csrf_exempt
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def payment_success(request):
    """
    Called by SSLCommerz (gateway). Accepts POST without auth.
    The function should validate payload and update records.
    """
    # --- optional: log raw payload for debugging ---
    logger.info("payment_success called (AllowAny). payload=%s headers=%s", request.data, dict(request.headers))

    tran_id = request.data.get("tran_id") or request.POST.get("tran_id")
    total_amount = request.data.get("amount") or request.POST.get("amount")

    if not tran_id:
        return JsonResponse({"error": "missing tran_id"}, status=400)

    # Try to find user based on tran_id if your tran_id encodes user id
    try:
        user_id = tran_id.split('_')[0]
        user = User.objects.get(id=user_id)
    except Exception:
        logger.exception("Failed to find user for tran_id=%s", tran_id)
        return JsonResponse({"error": "failed to find user for transaction id"}, status=400)

    try:
        user.is_subscribed = True
        user.save()
        payment = Payment.objects.create(
            user=user,
            transaction_id=tran_id,
            amount=total_amount or 0,
            status='success',
            payment_date=timezone.now()
        )
    except Exception:
        logger.exception("Failed to create payment record for tran_id=%s", tran_id)
        return JsonResponse({"error":"payment processing failed"}, status=500)

    # return either redirect (if gateway follows) or JSON
    return HttpResponseRedirect(f"{settings.FRONTEND_URL.rstrip('/')}/payment/success")

@csrf_exempt
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def payment_fail(request):
    logger.info("payment_fail called payload=%s", request.data)
    # handle failure: log, create Payment with status 'failed' etc.
    return HttpResponseRedirect(f"{settings.FRONTEND_URL.rstrip('/')}/payment/fail")


@csrf_exempt
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def payment_cancel(request):
    logger.info("payment_cancel called payload=%s", request.data)
    # handle cancel
    return HttpResponseRedirect(f"{settings.FRONTEND_URL.rstrip('/')}/payment/cancel")