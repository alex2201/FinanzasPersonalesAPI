import graphene

from database import sql_server_execute_query, sql_server_call_proc


# Types
class UserType(graphene.ObjectType):
    userId = graphene.ID()


# Query
class UserQuery(graphene.ObjectType):
    validate_user = graphene.Field(
        UserType,
        username=graphene.ID(required=True),
        password=graphene.String(required=True)
    )

    @staticmethod
    def resolve_validate_user(root, info, username, password):
        query = f'EXEC sp_validate_user \'{username}\', ' \
                f'\'{password}\''
        result = sql_server_execute_query(query)
        print('here')
        return result[0]


# Mutation
class CreateUser(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        email = graphene.String(required=True)

    status = graphene.Boolean()
    errorMsg = graphene.String()

    @classmethod
    def mutate(root, info, x, username: str, password: str, email: str):
        spcall = f'EXEC sp_create_user \'{username}\', \'{password}\', \'{email}\''
        result = sql_server_call_proc(spcall)
        return CreateUser(**result)


class UserMutation(graphene.ObjectType):
    create_account = CreateUser.Field()


user_schema = graphene.Schema(query=UserQuery, mutation=UserMutation)
