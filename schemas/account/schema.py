import graphene
from flask_graphql_auth import (
    AuthInfoField,
    get_jwt_identity,
    mutation_jwt_required)

from database import sql_server_call_proc, sql_server_execute_query
# Types
from schemas.generic import SPCallResultType, query_jwt_required_list


class Account(graphene.ObjectType):
    accountId = graphene.ID(required=True)
    accountName = graphene.String(required=True)
    balance = graphene.Float(required=True)
    createDate = graphene.DateTime(required=True)


class ProtectedUnion(graphene.Union):
    class Meta:
        types = (Account, AuthInfoField, SPCallResultType)

    @classmethod
    def resolve_type(cls, instance, info):
        return type(instance)


# Query
class Query(graphene.ObjectType):
    user_accounts = graphene.List(ProtectedUnion, token=graphene.String(required=True))

    @staticmethod
    @query_jwt_required_list
    def resolve_user_accounts(root, info):
        identity = get_jwt_identity()
        userId = identity['userId']
        query = f"""select accountId, accountName, createDate, balance
                from vw_account_detail accdet
                where accdet.userId = \'{userId}\'
                order by accountName"""
        result = sql_server_execute_query(query)
        return [Account(**r) for r in result]


# Mutations
class CreateAccount(graphene.Mutation):
    class Arguments:
        token = graphene.String(required=True)
        accountName = graphene.String(required=True)
        initAmount = graphene.Float(required=True)

    result = graphene.Field(ProtectedUnion)

    @classmethod
    @mutation_jwt_required
    def mutate(root, info, _, **kwargs):
        identity = get_jwt_identity()
        user_id = identity['userId']
        account_name = kwargs['accountName']
        init_amount = kwargs['initAmount']
        spcall = f'EXEC sp_create_account \'{user_id}\', \'{account_name}\', {init_amount}'
        result = sql_server_call_proc(spcall)
        return CreateAccount(result=SPCallResultType(**result))


class DeleteAccount(graphene.Mutation):
    class Arguments:
        token = graphene.String(required=True)
        accountId = graphene.ID(required=True)

    result = graphene.Field(ProtectedUnion)

    @classmethod
    @mutation_jwt_required
    def mutate(root, info, _, **kwargs):
        accountId = kwargs['accountId']
        spcall = f'EXEC sp_delete_account \'{accountId}\''
        result = sql_server_call_proc(spcall)
        return DeleteAccount(result=SPCallResultType(**result))


class AccountMutation(graphene.ObjectType):
    create_account = CreateAccount.Field()
    delete_account = DeleteAccount.Field()


account_schema = graphene.Schema(query=Query, mutation=AccountMutation)
