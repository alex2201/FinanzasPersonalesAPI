import graphene
from flask_graphql_auth import create_access_token, create_refresh_token, mutation_jwt_refresh_token_required, \
    get_jwt_identity, AuthInfoField, query_jwt_required

from database import sql_server_execute_query, sql_server_call_proc
# Types
from schemas.generic import SPCallResultType


class User(graphene.ObjectType):
    username = graphene.String()


class ProtectedUnion(graphene.Union):
    class Meta:
        types = (User, AuthInfoField, SPCallResultType)

    @classmethod
    def resolve_type(cls, instance, info):
        return type(instance)


# Query
class UserQuery(graphene.ObjectType):
    user_data = graphene.Field(
        User,
        token=graphene.String(required=True)
    )

    @staticmethod
    @query_jwt_required
    def resolve_user_data(root, info):
        identity = get_jwt_identity()
        userId = identity['userId']
        query = f'select username ' \
                'from cat_user ' \
                f'where userId=\'{userId}\''
        result = sql_server_execute_query(query)
        return User(**result[0])


# Mutation
class AuthMutation(graphene.Mutation):
    class Arguments(object):
        username = graphene.String()
        password = graphene.String()

    access_token = graphene.String()
    refresh_token = graphene.String()

    @classmethod
    def mutate(cls, _, info, username, password):
        query = f'EXEC sp_validate_user \'{username}\', ' \
                f'\'{password}\''
        query_result = sql_server_execute_query(query)
        userId = query_result[0]
        result = AuthMutation(
            access_token=create_access_token(userId),
            refresh_token=create_refresh_token(userId),
        ) if userId['userId'] else AuthMutation(access_token=None, refresh_token=None)
        return result


class RefreshMutation(graphene.Mutation):
    class Arguments(object):
        refresh_token = graphene.String()

    new_token = graphene.String()

    @classmethod
    @mutation_jwt_refresh_token_required
    def mutate(cls, _):
        current_user = get_jwt_identity()
        return RefreshMutation(new_token=create_access_token(identity=current_user))


class CreateUser(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        email = graphene.String(required=True)

    result = graphene.Field(SPCallResultType)

    @classmethod
    def mutate(root, info, x, username: str, password: str, email: str):
        spcall = f'EXEC sp_create_user \'{username}\', \'{password}\', \'{email}\''
        result = sql_server_call_proc(spcall)
        return CreateUser(result=result)


class UserMutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    auth_user = AuthMutation.Field()
    refresh_token = RefreshMutation.Field()


user_schema = graphene.Schema(query=UserQuery, mutation=UserMutation)
