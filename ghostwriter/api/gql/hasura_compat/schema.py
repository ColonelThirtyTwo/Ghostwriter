
import logging

import graphene
from query_optimizer import DjangoObjectType, DjangoListField, optimize

from ghostwriter.api.gql.hasura_compat.types import mk_bool_exp, mk_order_by
from ghostwriter.oplog.models import Oplog, OplogEntry

logger = logging.getLogger(__name__)

class OplogEntryType(DjangoObjectType):
    class Meta:
        model = OplogEntry
        fields = [
            "entry_identifier",
            "start_date",
            "end_date",
            "source_ip",
            "dest_ip",
            "tool",
            "user_context",
            "command",
            "description",
            "output",
            "comments",
            "operator_name",
            "extra_fields",
            "oplog_id",
        ]

    tags = graphene.NonNull(graphene.List(graphene.NonNull(graphene.String)))
    def resolve_tags(root: OplogEntry, info):
        return root.tags.names()

    @classmethod
    def get_queryset(cls, queryset, info):
        OplogEntry.user_viewable(info.context.user, queryset)

class OplogType(DjangoObjectType):
    class Meta:
        model = Oplog
        fields = [
            "name",
            "project",
            "mute_notifications",
        ]

    entries = DjangoListField(OplogEntryType, required=True)

    @classmethod
    def get_queryset(cls, queryset, info):
        return Oplog.user_viewable(info.context.user, queryset)


def mk_hasura_query(typ: type[DjangoObjectType]):
    field = DjangoListField(
        typ,
        args={
            "where": graphene.Argument(mk_bool_exp(typ)),
            "limit": graphene.Argument(graphene.Int),
            "offset": graphene.Argument(graphene.Int),
            "order_by": graphene.Argument(graphene.List(graphene.NonNull(mk_order_by(typ)))),
        },
    )

    def resolve(self, info, where=None, limit=None, offset=None, order_by=None):
        qs = typ.get_queryset(typ._meta.model.objects.all(), info)
        if where is not None:
            qs = qs.filter(where.filter_expr(""))
        if order_by is not None:
            order = []
            for item in order_by:
                order.extend(item.order_fields())
            if order:
                qs = qs.order_by(*order)
        if offset is not None:
            qs = qs[offset:]
        if limit is not None:
            qs = qs[:limit]
        return optimize(qs, info)
    return (field, resolve)

class Query(graphene.ObjectType):
    (compat_oplogs, resolve_compat_oplogs) = mk_hasura_query(OplogType)
    (compat_oplog_entries, resolve_compat_oplog_entries) = mk_hasura_query(OplogEntryType)

schema = graphene.Schema(query=Query, auto_camelcase=False)
