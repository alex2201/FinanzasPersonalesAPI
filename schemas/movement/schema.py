import graphene
from database.mysqlconn import DBConn

# Types
from database.sqlserverconn import SQLServerDBConn


class MovementType(graphene.ObjectType):
    mov_type_id = graphene.ID(required=True)
    mov_type_desc = graphene.String(required=True)


class Movement(graphene.ObjectType):
    mov_id = graphene.ID(required=True)
    desc = graphene.String(required=True)
    amount = graphene.Float(required=True)
    account_id = graphene.ID(required=True)
    account_name = graphene.String(required=True)
    mov_type = graphene.Field(MovementType)
    mov_date_id = graphene.DateTime(required=True)


# Query
class MovementQuery(graphene.ObjectType):
    account_movements = graphene.List(Movement, account_id=graphene.ID(required=True), required=True)
    movement_types = graphene.List(MovementType)

    @staticmethod
    def resolve_account_movements(root, info, account_id):
        query = f"""select *
                from vw_movement_detail movdet
                where movdet.accountId = {int(account_id)}
                order by dateTimeId desc"""

        with SQLServerDBConn() as cnxn:
            cursor = cnxn.cursor()
            cursor.execute(query)
            row = cursor.fetchone()
            result = []
            while row:
                r = {
                    "mov_id": row[0],
                    "desc": row[1],
                    "amount": row[2],
                    "account_id": row[3],
                    "account_name": row[4],
                    "mov_type": {
                        "mov_type_id": row[5],
                        "mov_type_desc": row[6],
                    },
                    "mov_date_id": row[7],
                }
                result.append(r)
                row = cursor.fetchone()
            cursor.close()
        return result

    @staticmethod
    def resolve_movement_types(root, info):
        query = f"""select movementTypeId, movementTypeDesc
                    from cat_movement_type;"""

        with SQLServerDBConn() as cnxn:
            cursor = cnxn.cursor()
            cursor.execute(query)
            row = cursor.fetchone()
            result = []
            while row:
                r = {
                    "mov_type_id": row[0],
                    "mov_type_desc": row[1],
                }
                result.append(r)
                row = cursor.fetchone()
            cursor.close()
        return result


# Mutations
class AddMovement(graphene.Mutation):
    class Arguments:
        desc = graphene.String(required=True)
        amount = graphene.Float(required=True)
        account_id = graphene.ID(required=True)
        mov_type_id = graphene.ID(required=True)
        date_id = graphene.String(required=True)

    status = graphene.Boolean()
    error_msg = graphene.String()

    @classmethod
    def mutate(root, info, _, **kwargs):
        desc = kwargs['desc']
        amount = kwargs['amount']
        account_id = int(kwargs['account_id'])
        mov_type = kwargs['mov_type_id']
        date_id = kwargs['date_id']

        spcall = f'EXEC sp_add_movement \'{desc}\', ' \
                 f'{amount}, ' \
                 f'{account_id}, ' \
                 f'\'{mov_type}\', ' \
                 f'\'{date_id}\''

        with SQLServerDBConn() as cnxn:
            cursor = cnxn.cursor()
            cursor.execute(spcall)
            status, error_msg = cursor.fetchone()
            result = {"status": status, "error_msg": error_msg}
            cursor.close()
        return AddMovement(**result)


class DeleteMovement(graphene.Mutation):
    class Arguments:
        mov_id = graphene.Int(required=True)

    status = graphene.Boolean()
    error_msg = graphene.String()

    @classmethod
    def mutate(root, info, _, **kwargs):
        mov_id = kwargs['mov_id']
        spcall = f'EXEC sp_delete_movement {mov_id}'
        with SQLServerDBConn() as cnxn:
            cursor = cnxn.cursor()
            cursor.execute(spcall)
            status, error_msg = cursor.fetchone()
            result = {"status": status, "error_msg": error_msg}
            cursor.close()
        return DeleteMovement(**result)


class MovementMutation(graphene.ObjectType):
    add_movement = AddMovement.Field()
    deleteMovement = DeleteMovement.Field()


movement_schema = graphene.Schema(query=MovementQuery, mutation=MovementMutation)
