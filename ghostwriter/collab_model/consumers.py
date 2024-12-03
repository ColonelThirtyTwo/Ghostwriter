import asyncio
from typing import Any, Callable, Coroutine, Generic, TypeVar
import uuid
import logging
from django.db import transaction
from django.contrib.auth.models import User
from django.apps import apps
import pycrdt
from pycrdt_websocket.django_channels_consumer import YjsConsumer
from channels.consumer import AsyncConsumer
from channels.layers import BaseChannelLayer
from channels.db import database_sync_to_async

from ghostwriter.collab_model.models.ydocmodel import YDocModel

logger = logging.getLogger(__name__)

DEFAULT_WORKER_CHANNEL_NAME: str = "yjs_save"

T = TypeVar("T", bound=YDocModel)

class YjsUpdateConsumer(YjsConsumer, Generic[T]):
    """
    Websocket consumer for handling a connection from y-websockets for a `YDocModel`.

    Forwards updates to other clients, as well as the `YjsSaverWorkerConsumer` worker for saving.
    Saving updates is debounced, to prevent excessive database traffic and history entries.
    History entries will also be created, with the author set to the logged in user (via `self.scope["user"]`).
    """
    worker_channel_name: str
    model_cls: type[T]
    pk: Any | None
    connection_id: str
    updates_to_send: list[dict[str, Any]]
    getter: Callable[[dict], T | None]

    def __init__(
        self,
        model: type[T],
        getter: Callable[[dict], T | None],
        worker_channel_name: str = DEFAULT_WORKER_CHANNEL_NAME,
    ):
        """
        Create a consumer.

        * model: Model class to save
        * getter: Callable that takes the route arguments and returns either an instance to edit or returns None or
          throws a `model.DoesNotExist` exception to close the connection.
        """
        super().__init__()
        self.model_cls = model
        self.pk = None
        self.worker_channel_name = worker_channel_name
        self.connection_id = str(uuid.uuid4())
        self.updates_to_send = []
        self.getter = getter

    async def get_ydoc_model_object(self) -> T | None:
        """
        Retreives the model instance from the database.
        """
        try:
            model = await database_sync_to_async(self.getter)(self.scope["url_route"])
        except self.model_cls.DoesNotExist:
            model = None
        if model is None:
            self.close(code=404)
            return None

        if self.scope.get("user") is None or self.scope["user"].is_anonymous:
            self.close(code=404)
            return None
        if not await database_sync_to_async(model.user_can_edit)(self.scope["user"]):
            self.close(code=404)
            return None
        return model

    async def connect(self):
        instance = await self.get_ydoc_model_object()
        if instance is None:
            return
        assert isinstance(instance, self.model_cls)
        self.pk = instance.pk
        self.ydoc = instance.yjs_doc
        self.ydoc.observe(self._doc_transaction_callback)
        return await super().connect()

    def make_room_name(self) -> str:
        return "yjs-{}-{}".format(
            self.model_cls._meta.label, self.pk
        )

    async def make_ydoc(self) -> pycrdt.Doc:
        # our connect override initializes this
        return self.ydoc

    async def receive(self, text_data=None, bytes_data=None):
        if self.ydoc is None:
            logger.warning("%s: received with no ydoc - did `get_ydoc_model_object` return `None` without calling `close`?")
            return
        await super().receive(text_data=text_data, bytes_data=bytes_data)
        logger.debug("%s: Receive %d bytes", self.connection_id, len(bytes_data))
        # Can't send channel messages inside of the observer callback, since sending is async,
        # the callback is sync, and async_to_sync can't be used since its running in an async
        # thread. So buffer them up and send when we can.
        for ev in self.updates_to_send:
            await self.channel_layer.send(self.worker_channel_name, ev)
        self.updates_to_send.clear()

    def _doc_transaction_callback(self, ev: pycrdt.TransactionEvent):
        logger.debug("%s: Transaction", self.connection_id)
        self.updates_to_send.append(
            {
                "type": "doc_updated",
                "connection_id": self.connection_id,
                "model_app": self.model_cls._meta.app_label,
                "model_name": self.model_cls._meta.model_name,
                "model_pk": self.pk,
                "user_pk": self.scope["user"].pk,
                "update_bytes": ev.update,
            }
        )

    async def disconnect(self, code) -> None:
        self.channel_layer.send(
            self.worker_channel_name,
            {
                "type": "doc_flush",
                "connection_id": self.connection_id,
            },
        )
        await super().disconnect(code)


class _DebouncedCallback:
    """
    Calls a callback while applying debouncing.

    When `trigger` is called, schedules the callback to run after `delay` seconds.
    If `trigger` is called again before then, the delay is reset.
    """
    task_name: str | None
    task: asyncio.Task | None
    cb: Callable[[], Coroutine[Any, Any, None]]

    def __init__(
        self,
        cb: Callable[[], Coroutine[Any, Any, None]],
        *,
        task_name: str | None = None
    ):
        self.cb = cb
        self.task_name = task_name
        self.ended = False
        self.task = None

    async def _task(self, delay: float):
        await asyncio.sleep(delay)
        await self.cb()

    def trigger(self, delay: float):
        if self.task is not None:
            self.task.cancel()
        self.task = asyncio.create_task(self._task(delay), name=self.task_name)

    def stop(self):
        if self.task is not None:
            self.task.cancel()


class _PendingState:
    """
    Unsaved state kept in memory until a debounce timeout has passed.

    Update blobs are accumulated in the `updates` list. When the `save_debounce_cb` fires or the websocket
    disconnects, the document is loaded, updates applied, then saved.
    """

    # Higher values reduce database load and number of history entries, but also cause edits to take longer to save.
    save_debounce_time: float = 1.0  # seconds

    connection_id: str
    model_cls: type[YDocModel]
    user_pk: int
    doc_pk: int
    updates: list[bytes]
    channel_layer: BaseChannelLayer
    channel_name: str
    save_debounce_cb: _DebouncedCallback

    def __init__(
        self,
        connection_id: str,
        model_cls: type[YDocModel],
        user_pk: int,
        doc_pk: int,
        channel_layer: BaseChannelLayer,
        channel_name: str,
    ) -> None:
        self.connection_id = connection_id
        self.model_cls = model_cls
        self.user_pk = user_pk
        self.doc_pk = doc_pk
        self.updates = []
        self.channel_layer = channel_layer
        self.channel_name = channel_name
        self.save_debounce_cb = _DebouncedCallback(self._debounce_cb)

    async def _debounce_cb(self):
        await self.channel_layer.send(
            self.channel_name,
            {
                "type": "doc_flush",
                "connection_id": self.connection_id,
            },
        )

    def update(self, update_bytes: bytes) -> None:
        self.updates.append(update_bytes)
        self.save_debounce_cb.trigger(self.save_debounce_time)

    async def flush(self) -> None:
        self.save_debounce_cb.stop()
        if not self.updates:
            return

        await database_sync_to_async(self.save)()
        self.updates.clear()

    def save(self) -> None:
        with transaction.atomic():
            instance = self.model_cls.objects.select_for_update().get(pk=self.doc_pk)
            with instance.yjs_doc.transaction():
                for update in self.updates:
                    instance.yjs_doc.apply_update(update)
            instance.save(author=self.user_pk)

        if logger.isEnabledFor(logging.DEBUG):
            user = User.objects.get(pk=self.user_pk)
            logger.debug("Update from %s: %r", user, instance)


class YjsSaverWorkerConsumer(AsyncConsumer):
    """
    Channels worker that combines and saves updates.

    Needs to be started for collaborative edits to save. See
    https://channels.readthedocs.io/en/latest/topics/worker.html.
    """
    pending: dict[str, _PendingState]

    def __init__(self) -> None:
        super().__init__()
        self.pending = {}

    async def doc_updated(self, message: dict) -> None:
        connection_id: str = message["connection_id"]
        logger.debug("doc_updated from %s user %s", connection_id, message["user_pk"])
        if connection_id not in self.pending:
            model = apps.get_app_config(message["model_app"]).get_model(
                message["model_name"]
            )
            self.pending[connection_id] = _PendingState(
                connection_id,
                model,
                message["user_pk"],
                message["model_pk"],
                self.channel_layer,
                self.channel_name,
            )
        self.pending[connection_id].update(message["update_bytes"])

    async def doc_flush(self, message: dict) -> None:
        connection_id: str = message["connection_id"]
        logger.debug("doc_flush from %s", connection_id)
        if connection_id not in self.pending:
            return
        await self.pending[connection_id].flush()
        del self.pending[connection_id]

