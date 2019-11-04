import graphene

from database import sql_server_call_proc, sql_server_execute_query


class Account(graphene.ObjectType):
    accountId = graphene.ID(required=True)
    accountName = graphene.String(required=True)
    balance = graphene.Float(required=True)
    createDate = graphene.DateTime(required=True)


class Query(graphene.ObjectType):
    user_accounts = graphene.List(Account, userId=graphene.ID(required=True), required=True)

    @staticmethod
    def resolve_user_accounts(root, info, userId):
        query = f"""select accountId, accountName, createDate, balance
                from vw_account_detail accdet
                where accdet.userId = \'{userId}\'
                order by accountName"""
        result = sql_server_execute_query(query)
        return result


# Mutations
class CreateAccount(graphene.Mutation):
    class Arguments:
        userId = graphene.ID(required=True)
        accountName = graphene.String(required=True)
        initAmount = graphene.Float(required=True)

    status = graphene.Boolean()
    errorMsg = graphene.String()

    @classmethod
    def mutate(root, info, _, **kwargs):
        user_id = kwargs['userId']
        account_name = kwargs['accountName']
        init_amount = kwargs['initAmount']
        spcall = f'EXEC sp_create_account \'{user_id}\', \'{account_name}\', {init_amount}'
        result = sql_server_call_proc(spcall)
        return CreateAccount(**result)


class DeleteAccount(graphene.Mutation):
    class Arguments:
        accountId = graphene.ID(required=True)

    status = graphene.Boolean()
    errorMsg = graphene.String()

    @classmethod
    def mutate(root, info, _, **kwargs):
        accountId = kwargs['accountId']
        spcall = f'EXEC sp_delete_account \'{accountId}\''
        result = sql_server_call_proc(spcall)
        return DeleteAccount(**result)


class AccountMutation(graphene.ObjectType):
    create_account = CreateAccount.Field()
    delete_account = DeleteAccount.Field()


account_schema = graphene.Schema(query=Query, mutation=AccountMutation)
