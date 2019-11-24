# Types
import graphene
from flask_graphql_auth import (
    AuthInfoField,
    wraps, current_app, verify_jwt_in_argument)


class SPCallResultType(graphene.ObjectType):
    status = graphene.Boolean()
    errorMsg = graphene.String()


# Wrapper
def query_jwt_required_list(fn):
    """
    A decorator to protect a query resolver.

    If you decorate an resolver with this, it will ensure that the requester
    has a valid access token before allowing the resolver to be called. This
    does not check the freshness of the access token.
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        token = kwargs.pop(current_app.config["JWT_TOKEN_ARGUMENT_NAME"])
        try:
            verify_jwt_in_argument(token)
        except Exception as e:
            return [AuthInfoField(message=str(e))]

        return fn(*args, **kwargs)

    return wrapper
