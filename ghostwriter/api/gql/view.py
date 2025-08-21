
import logging

from django.conf import settings
from django.http import HttpRequest
from graphql import ExecutionResult, GraphQLError
from django.contrib.auth.models import AbstractUser
from graphene_django.views import GraphQLView

from ghostwriter.api import utils
from ghostwriter.api.gql.fake_admin import ADMIN_USER, FakeAdminUser

logger = logging.getLogger(__name__)

class GwGqlContext:
    def __init__(self, request: HttpRequest, user: AbstractUser | FakeAdminUser):
        self.request = request
        self.user = user
    request: HttpRequest
    user: AbstractUser | FakeAdminUser


class GwGraphqlView(GraphQLView):
    def get_context(self, request: HttpRequest):
        #if not utils.verify_graphql_request(request.headers):
        #    raise HasuraError(403, "Unauthorized access method", "Unauthorized")
        if "x-hasura-admin-secret" in request.headers and request.headers["x-hasura-admin-secret"] == settings.GRAPHQL_ADMIN_SECRET:
            user = ADMIN_USER
        elif "HTTP_AUTHORIZATION" in request.META:
            jwt = utils.get_jwt_from_request(request)
            if not jwt:
                raise utils.HasuraError(400, "Invalid JWT in authorization header", "JWTMissing")
            user = utils.check_token_get_user(jwt)
        else:
            #if not request.user.is_authenticated:
            #    raise HasuraError(400, "No ``Authorization`` header found", "JWTMissing")
            user = request.user
        if user.is_authenticated and not user.is_active:
            logger.warning("Received JWT for inactive user: %s", self.user_obj.username)
            raise utils.HasuraError(401, "Received invalid API token", "JWTInvalid")
        return GwGqlContext(
            request=request,
            user=user,
        )

    # def parse_body(self, request: HttpRequest):
    #     b = super().parse_body(request)
    #     logger.info("DEBUG headers: %r", request.headers)
    #     logger.info("DEBUG body: %r", b)
    #     return b

    # def get_response(self, request, data, show_graphiql=False):
    #     res = super().get_response(request, data, show_graphiql)
    #     logger.info("DEBUG response: %r", res)
    #     return res

    def execute_graphql_request(self, *args, **kwargs):
        out: ExecutionResult = super().execute_graphql_request(*args, **kwargs)
        # Log errors with tracebacks for debugging
        if out.errors is not None:
            for err in out.errors:
                if isinstance(err, GraphQLError):
                    if err.original_error:
                        logger.error("GraphQL Error", exc_info=err.original_error)
                elif isinstance(err, utils.HasuraError):
                    pass
                else:
                    logger.error("GraphQL Error", exc_info=err)
        return out
