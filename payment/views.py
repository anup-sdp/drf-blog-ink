from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status


class PaymentPlaceholderViewSet(viewsets.ViewSet):
    """
    To be implemented later
    """

    def list(self, request):
        return Response(
            {"detail": "Payment endpoints are planned for future updates."},
            status=status.HTTP_501_NOT_IMPLEMENTED,
        )

    def create(self, request):
        return self.list(request)

    def retrieve(self, request, pk=None):
        return self.list(request)

    def update(self, request, pk=None):
        return self.list(request)

    def partial_update(self, request, pk=None):
        return self.list(request)

    def destroy(self, request, pk=None):
        return self.list(request)