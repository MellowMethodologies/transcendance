from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied
from django.shortcuts import get_object_or_404
from django.db.models import Q
from drf_spectacular.utils import extend_schema
from ...utils import send_real_time_notif

from apps.users import serializers
from apps.users.models import Connection, User, Notification
from apps.users.docs import (
    CONNECTIONS_LIST_SCHEMA,
    CONNECTIONS_ACCEPT_SCHEMA,
    CONNECTIONS_BLOCK_SCHEMA,
    CONNECTIONS_CREATE_SCHEMA,
    CONNECTIONS_DESTROY_SCHEMA,
)


class ConnectionViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
):

    serializer_class = serializers.ConnectionSerializer
    queryset = Connection.objects.all()

    STATUS_QUERIESETS = {
        "all": lambda user: Connection.get_user_connections(user=user),
        "friends": lambda user: Connection.get_friends(user=user),
        "pending": lambda user: Connection.get_pending_requests(user=user),
        "sent_requests": lambda user: Connection.get_sent_requests(user=user),
        "blocked": lambda user: Connection.get_blocked_users(user=user),
    }

    def get_queryset(self):
        """
        Override get_queryset to filter connections based on status parameter
        """
        user = self.request.user
        if self.action == "list":
            status_param = self.request.GET.get("status", "all")
            if status_param not in self.STATUS_QUERIESETS:
                valid_status = ", ".join(self.STATUS_QUERIESETS.keys())
                raise ValidationError(
                    {
                        "detail": f"Invalid status {status_param}. valid options are: {valid_status}"
                    }
                )
            return self.STATUS_QUERIESETS[status_param](user=user)
        return self.queryset

    def get_connection(self):
        """Get connection object and verify user's permission to modify it"""
        # print('eroor', flush=True)
        connection = get_object_or_404(Connection, pk=self.kwargs["pk"])
        user = self.request.user

        if user not in [connection.initiator, connection.recipient]:
            raise PermissionDenied(
                "You don't have permission to modify this connection"
            )
        return connection, user

    def perform_create(self, serializer):
        """Set the initiator to the current user when creating a connection"""
        serializer.save(initiator=self.request.user, status=Connection.PENDING)

    @extend_schema(**CONNECTIONS_LIST_SCHEMA)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(**CONNECTIONS_CREATE_SCHEMA)
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(**CONNECTIONS_ACCEPT_SCHEMA)
    @action(detail=True, methods=["get"])
    def accept(self, request, pk=None):
        """Accept a pending connection request"""
        connection, user = self.get_connection()

        if connection.status != Connection.PENDING:
            raise ValidationError("Can only accept pending connections")
        if user != connection.recipient:
            raise PermissionDenied("Only the recipient can accept connection requests")

        connection.status = Connection.FRIENDS
        connection.save()
        sent = Notification.objects.filter(Q(connection_id=connection.id, user=connection.recipient)).first()
        if sent:
            sent.connection_id = None
            sent.sender = None
            sent.message = f"You accepted {connection.initiator.username}'s friend request"
            sent.save()
            data = serializers.NotificationSerializer(sent)
            send_real_time_notif(sent.user.id, data.data)
        notif = Notification.objects.create(
            user=connection.initiator,
            notification_type=Notification.NOTIFICATION_TYPES["connections"],
            message=f"{connection.recipient.username} accepted your friend request",
        )
        data = serializers.NotificationSerializer(notif)
        send_real_time_notif(notif.user.id, data.data)
        return Response(
            {
                "message": "Connection request accepted",
                "connection": self.get_serializer(connection).data,
            }
        )

    @extend_schema(**CONNECTIONS_BLOCK_SCHEMA)
    @action(detail=False, methods=["post"])
    def block(self, request):
        """
        Block a user by user_id
        Expects: {"user_id": <id>}
        """
        user_id = request.data.get("recipient_id")
        if not user_id:
            raise ValidationError("user_id is required")

        user_to_block = get_object_or_404(User, id=user_id)
        current_user = request.user

        if user_to_block == current_user:
            raise ValidationError("You cannot block yourself")

        # find any existing connection between the users
        connection = Connection.objects.filter(
            (Q(initiator=current_user) & Q(recipient=user_to_block))
            | (Q(initiator=user_to_block) & Q(recipient=current_user))
        ).first()

        if connection and connection.status == Connection.BLOCKED:
            if connection.recipient == current_user:
                raise PermissionDenied("Failed to perform this action")
            return Response(
                {
                    "message": "Connection already blocked",
                    "connection": self.get_serializer(connection).data,
                }
            )

        if connection:
            connection.delete()

        new_conn = Connection.objects.create(
            initiator=current_user, recipient=user_to_block, status=Connection.BLOCKED
        )

        return Response(
            {
                "message": "User blocked",
                "connection": self.get_serializer(new_conn).data,
            }
        )

    @extend_schema(**CONNECTIONS_DESTROY_SCHEMA)
    def destroy(self, request, *args, **kwargs):
        """Handle reject/cancel/remove/unblock actions by deleting the connection"""
        connection, user = self.get_connection()

        if connection.status == Connection.BLOCKED and connection.recipient == user:
            raise PermissionDenied("Cannot remove a connection where you are blocked")

        
        notif = Notification.objects.filter(Q(connection_id=connection.id, user=connection.recipient)).first()
        if notif:
            notif.delete()

        connection.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
