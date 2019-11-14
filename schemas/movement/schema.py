import graphene
from flask_graphql_auth import AuthInfoField, mutation_jwt_required

from database import sql_server_call_proc, sql_server_execute_query
# Types
from schemas.generic import SPCallResultType, query_jwt_required_list


class MovementType(graphene.ObjectType):
    movTypeId = graphene.ID(required=True)
    movTypeDesc = graphene.String(required=True)


class Movement(graphene.ObjectType):
    movId = graphene.ID(required=True)
    movDesc = graphene.String(required=True)
    amount = graphene.Float(required=True)
    accountId = graphene.ID(required=True)
    accountName = graphene.String(required=True)
    movType = graphene.Field(MovementType)
    dateTimeId = graphene.DateTime(required=True)


class ProtectedUnion(graphene.Union):
    class Meta:
        types = (Movement, AuthInfoField, SPCallResultType)

    @classmethod
    def resolve_type(cls, instance, info):
        return type(instance)


# Query
class MovementQuery(graphene.ObjectType):
    account_movements = graphene.List(Movement, accountId=graphene.ID(required=True), required=True)
    movement_types = graphene.List(MovementType)

    @staticmethod
    @query_jwt_required_list
    def resolve_account_movements(root, info, accountId):
        query = f"""select *
                from vw_movement_detail movdet
                where movdet.accountId = \'{accountId}\'
                order by dateTimeId desc"""
        result = sql_server_execute_query(query)
        for r in result:
            r['movType'] = {'movTypeId': r['movTypeId'], 'movTypeDesc': r['movTypeDesc']}
            del r['movTypeId']
            del r['movTypeDesc']
        return [Movement(**r) for r in result]

    @staticmethod
    def resolve_movement_types(root, info):
        query = f"""select movTypeId, movTypeDesc
                    from cat_movement_type;"""
        result = sql_server_execute_query(query)
        return result


# Mutations
class AddMovement(graphene.Mutation):
    class Arguments:
        token = graphene.String(required=True)
        movDesc = graphene.String(required=True)
        amount = graphene.Float(required=True)
        accountId = graphene.ID(required=True)
        movTypeId = graphene.ID(required=True)
        dateId = graphene.String(required=True)

    result = graphene.Field(ProtectedUnion)

    @classmethod
    @mutation_jwt_required
    def mutate(cls, info, _, **kwargs):
        movDesc = kwargs['movDesc']
        amount = kwargs['amount']
        accountId = kwargs['accountId']
        movTypeId = kwargs['movTypeId']
        dateId = kwargs['dateId']

        spcall = f'EXEC sp_add_movement \'{movDesc}\', ' \
                 f'{amount}, ' \
                 f'\'{accountId}\', ' \
                 f'\'{movTypeId}\', ' \
                 f'\'{dateId}\''
        result = sql_server_call_proc(spcall)
        return AddMovement(result=SPCallResultType(**result))


class DeleteMovement(graphene.Mutation):
    class Arguments:
        token = graphene.String(required=True)
        movId = graphene.ID(required=True)

    result = graphene.Field(ProtectedUnion)

    @classmethod
    @mutation_jwt_required
    def mutate(cls, info, _, **kwargs):
        movId = kwargs['movId']
        spcall = f'EXEC sp_delete_movement \'{movId}\''
        result = sql_server_call_proc(spcall)
        return DeleteMovement(result=SPCallResultType(**result))


class MovementMutation(graphene.ObjectType):
    add_movement = AddMovement.Field()
    delete_movement = DeleteMovement.Field()


movement_schema = graphene.Schema(query=MovementQuery, mutation=MovementMutation)
