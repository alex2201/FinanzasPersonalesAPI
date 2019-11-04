from flask import Flask
from flask_graphql import GraphQLView

from schemas.account.schema import account_schema
from schemas.movement.schema import movement_schema
from schemas.user.schema import user_schema

# from flask_cors import CORS, cross_origin

app = Flask(__name__)

# Route
app.add_url_rule(
    '/api/user',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=user_schema,
        graphiql=True  # for having the GraphiQL interface
    )
)

app.add_url_rule(
    '/api/account',
    view_func=GraphQLView.as_view(
        'account',
        schema=account_schema,
        graphiql=True  # for having the GraphiQL interface
    )
)

app.add_url_rule(
    '/api/movement',
    view_func=GraphQLView.as_view(
        'movement',
        schema=movement_schema,
        graphiql=True  # for having the GraphiQL interface
    )
)


@app.route('/')
def index():
    return 'Server Running! :)'


if __name__ == '__main__':
    # CORS(app)
    # app.run(host='0.0.0.0', port=5000, debug=False)
    app.run(host='0.0.0.0', debug=False)
