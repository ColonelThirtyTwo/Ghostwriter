
from collections import OrderedDict
from typing import Any
from django.db.models import Q, F, Lookup, Field
import graphene
from graphene_django import DjangoObjectType


# Equals and Not Equals that match SQL behavior
@Field.register_lookup
class SqlEq(Lookup):
    lookup_name = "sqleq"
    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return "%s == %s" % (lhs, rhs), params

@Field.register_lookup
class SqlNe(Lookup):
    lookup_name = "sqlne"
    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return "%s != %s" % (lhs, rhs), params

class OrderBy(graphene.Enum):
    ASC = "asc"
    ASC_NULLS_LAST = "asc_nulls_last"
    ASC_NULLS_FIRST = "asc_nulls_first"
    DESC = "desc"
    DESC_NULLS_LAST = "desc_nulls_last"
    DESC_NULLS_FIRST = "desc_nulls_first"

def _mk_scalar_comparison_exp(name, scalar) -> type[graphene.InputObjectType]:
    fields = OrderedDict()
    for f in ["_eq", "_neq", "_gt", "_gte", "_lt", "_lte"]:
        fields[f] = graphene.Field(scalar)
    fields["_is_null"] = graphene.Field(graphene.Boolean)
    fields["_in"] = graphene.Field(graphene.List(graphene.NonNull(scalar)))

    def set_filters(self, field_name: str, filter: dict[str, Any]):
        if self._eq is not None:
            filter[field_name+"__sqleq"] = self._eq
        if self._neq is not None:
            filter[field_name+"__sqlne"] = self._neq
        for f in ("_gt", "_gte", "_lt", "_lte", "_in"):
            if getattr(self, f) is not None:
                filter[field_name + "_" + f] = getattr(self, f)
    fields["set_filters"] = set_filters
    return type(name, (graphene.InputObjectType,), fields)

COMPARISONS_FOR_SCALARS = [
    (graphene.BigInt, _mk_scalar_comparison_exp("BigIntComparisonExp", graphene.BigInt)),
    (graphene.Int, _mk_scalar_comparison_exp("IntComparisonExp", graphene.Int)),
    (graphene.String, _mk_scalar_comparison_exp("StringComparisonExp", graphene.String)),
    (graphene.DateTime, _mk_scalar_comparison_exp("DateTimeComparisonExp", graphene.DateTime)),
    # TODO: string like, regex
    # TODO others
]

_mk_bool_exp_cache = {}
def mk_bool_exp(cls: type[DjangoObjectType]) -> type[graphene.InputObjectType]:
    """
    Makes and caches a `*_bool_exp` `InputObjectType` for a GraphQL structure, matching what
    Hasura generates.
    """
    if cls in _mk_bool_exp_cache:
        return _mk_bool_exp_cache[cls]

    # Pre-assigning to generate a var for use in lambdas, for forward referencing
    gql_cls = None
    # Store lazy loader in cache, to be returned for for recursive operations
    _mk_bool_exp_cache[cls] = lambda: gql_cls()

    cls_dict = OrderedDict()
    cmp_fields = []
    cls_dict["_and"] = graphene.Field(graphene.List(graphene.NonNull(lambda: gql_cls())))
    cls_dict["_or"] = graphene.Field(graphene.List(graphene.NonNull(lambda: gql_cls())))
    cls_dict["_not"] = graphene.Field(lambda: gql_cls())

    for (name, field) in cls._meta.fields.items():
        field_ty = field.type
        if isinstance(field_ty, graphene.NonNull):
            field_ty = field_ty.of_type

        scalar_ty = next((
            cmp for ty, cmp in COMPARISONS_FOR_SCALARS if ty == field_ty or isinstance(field_ty, ty)
        ), None)
        if scalar_ty is not None:
            cmp_fields.append(name)
            cls_dict[name] = graphene.Field(scalar_ty)
            continue
        # TODO: other types

    def filter_expr(this, prefix: str = ""):
        q_args = {}
        for name in cmp_fields:
            field = getattr(this, name)
            if field is not None:
                field.set_filters(name, q_args)
        q = Q(**q_args)

        if this._not is not None:
            q = q & ~this._not.filter_expr(prefix)
        if this._and is not None:
            for item in this._and:
                q = q & item.filter_expr(prefix)
        if this._or is not None:
            qor = Q(False)
            for item in this._or:
                qor = qor | item.filter_expr(prefix)
            q = q & qor
        return q

    cls_dict["filter_expr"] = filter_expr

    gql_cls = type(
        cls.__name__ + "_bool_exp",
        (graphene.InputObjectType,),
        cls_dict,
    )
    _mk_bool_exp_cache[cls] = gql_cls
    return gql_cls

_mk_order_by_cache = {}
_ORDERABLE_SCALARS = [
    graphene.ID,
    graphene.Int,
    graphene.BigInt,
    graphene.String,
    # TODO others
]
def mk_order_by(cls: type[DjangoObjectType]) -> type[graphene.InputObjectType]:
    """
    Makes and caches a `*_order_by` `InputObjectType` for a GraphQL structure, matching what
    Hasura generates.
    """
    if cls in _mk_order_by_cache:
        return _mk_order_by_cache[cls]

    cls_dict = OrderedDict()
    fields = []

    for (name, field) in cls._meta.fields.items():
        field_ty = field.type
        if isinstance(field_ty, graphene.NonNull):
            field_ty = field_ty.of_type

        is_scalar = any(field_ty == scalar or isinstance(field_ty, scalar) for scalar in _ORDERABLE_SCALARS)
        if is_scalar:
            fields.append(name)
            cls_dict[name] = graphene.Field(OrderBy)
        # TODO: Other types of fields

    def order_fields(self):
        orders = []
        for field in fields:
            value = getattr(self, field)
            if value is None:
                continue
            f = F(field)
            nulls_first = value.value.endswith("nulls_first") or None
            nulls_last = value.value.endswith("nulls_last") or None
            if value.value.startswith("asc"):
                f = f.asc(nulls_first=nulls_first, nulls_last=nulls_last)
            else:
                f = f.desc(nulls_first=nulls_first, nulls_last=nulls_last)
            orders.append(f)
        return orders

    cls_dict["order_fields"] = order_fields

    gql_cls = type(
        cls.__name__ + "_order_by",
        (graphene.InputObjectType,),
        cls_dict,
    )
    _mk_bool_exp_cache[cls] = gql_cls
    return gql_cls

