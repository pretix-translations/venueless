from asgiref.sync import async_to_sync
from django.db import transaction
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView

from venueless.api.auth import (
    ApiAccessRequiredPermission,
    RoomPermissions,
    WorldPermissions,
)
from venueless.api.serializers import RoomSerializer, WorldSerializer
from venueless.core.models import Channel
from venueless.core.services.world import notify_schedule_change, notify_world_change

from ..core.models import Room


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.none()
    serializer_class = RoomSerializer
    permission_classes = [ApiAccessRequiredPermission & RoomPermissions]

    def get_queryset(self):
        return self.request.world.rooms.with_permission(
            traits=self.request.auth.get("traits"), world=self.request.world
        )

    def perform_create(self, serializer):
        serializer.save(world=self.request.world)
        for m in serializer.instance.module_config:
            if m["type"] == "chat.native":
                Channel.objects.get_or_create(
                    room=serializer.instance, world=self.request.world
                )
        transaction.on_commit(  # pragma: no cover
            lambda: async_to_sync(notify_world_change)(self.request.world.id)
        )

    def perform_update(self, serializer):
        super().perform_update(serializer)
        for m in serializer.instance.module_config:
            if m["type"] == "chat.native":
                Channel.objects.get_or_create(
                    room=serializer.instance, world=self.request.world
                )
        transaction.on_commit(  # pragma: no cover
            lambda: async_to_sync(notify_world_change)(self.request.world.id)
        )

    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        for m in instance.module_config:
            if m["type"] == "chat.native":
                Channel.objects.filter(room=instance, world=self.request.world).delete()
        transaction.on_commit(  # pragma: no cover
            lambda: async_to_sync(notify_world_change)(self.request.world.id)
        )


class WorldView(APIView):
    permission_classes = [ApiAccessRequiredPermission & WorldPermissions]

    def get(self, request, **kwargs):
        return Response(WorldSerializer(request.world).data)

    @transaction.atomic
    def patch(self, request, **kwargs):
        serializer = WorldSerializer(request.world, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        transaction.on_commit(  # pragma: no cover
            lambda: async_to_sync(notify_world_change)(request.world.id)
        )
        return Response(serializer.data)


@api_view(http_method_names=["POST"])
@permission_classes([ApiAccessRequiredPermission & WorldPermissions])
def schedule_update(request, **kwargs):
    """POST endpoint to notify venueless that schedule data has changed.

    Optionally, the request may contain data for the ``pretalx`` field in the
    world config.
    """
    domain = request.data.get("domain")
    event = request.data.get("event")

    if domain and event:
        pretalx_config = request.world.config.get("pretalx", {})
        if domain != pretalx_config.get("domain") or event != pretalx_config.get(
            "event"
        ):
            request.world.config["pretalx"] = {"domain": domain, "event": event}
            request.world.save()
            async_to_sync(notify_world_change)(request.world.id)

    async_to_sync(notify_schedule_change)(request.world.id)
    return Response()
