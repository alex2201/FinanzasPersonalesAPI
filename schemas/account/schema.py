import graphene
from database.mysqlconn import DBConn
from database.sqlserverconn import SQLServerDBConn


class Account(graphene.ObjectType):
    account_id = graphene.ID(required=True)
    name = graphene.String(required=True)
    balance = graphene.Float(required=True)
    date = graphene.DateTime(required=True)


class Query(graphene.ObjectType):
    user_accounts = graphene.List(Account, user_id=graphene.ID(required=True), required=True)

    @staticmethod
    def resolve_user_accounts(root, info, user_id):
        query = f"""select accountId, accountName, createDate, balance
                from vw_account_detail accdet
                where accdet.userId = {int(user_id)}"""

        with SQLServerDBConn() as cnxn:
            cursor = cnxn.cursor()
            cursor.execute(query)
            row = cursor.fetchone()
            result = []
            while row:
                r = {
                    "account_id": row[0],
                    "name": row[1],
                    "date": row[2],
                    "balance": row[3],
                }
                result.append(r)
                row = cursor.fetchone()
        return result


# Mutations
class CreateAccount(graphene.Mutation):
    class Arguments:
        user_id = graphene.ID(required=True)
        account_name = graphene.String(required=True)
        init_amount = graphene.Float(required=True)

    status = graphene.Boolean()
    error_msg = graphene.String()

    @classmethod
    def mutate(root, info, _, **kwargs):
        user_id = kwargs['user_id']
        account_name = kwargs['account_name']
        init_amount = kwargs['init_amount']

        spcall = f'EXEC sp_create_account {user_id}, \'{account_name}\', {init_amount}'

        with SQLServerDBConn() as cnxn:
            cursor = cnxn.cursor()
            cursor.execute(spcall)
            status, error_msg = cursor.fetchone()
            result = {"status": status, "error_msg": error_msg}
            cursor.close()

        return CreateAccount(**result)


class DeleteAccount(graphene.Mutation):
    class Arguments:
        account_id = graphene.ID(required=True)

    status = graphene.Boolean()
    error_msg = graphene.String()

    @classmethod
    def mutate(root, info, _, **kwargs):
        account_id = kwargs['account_id']
        spcall = f'EXEC sp_delete_account {account_id}'
        with SQLServerDBConn() as cnxn:
            cursor = cnxn.cursor()
            cursor.execute(spcall)
            status, error_msg = cursor.fetchone()
            result = {"status": status, "error_msg": error_msg}
            cursor.close()

        return DeleteAccount(**result)


class AccountMutation(graphene.ObjectType):
    create_account = CreateAccount.Field()
    delete_account = DeleteAccount.Field()


account_schema = graphene.Schema(query=Query, mutation=AccountMutation)
