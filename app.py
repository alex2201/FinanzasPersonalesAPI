from flask import Flask
from flask_graphql import GraphQLView

from schemas.helloworld.schema import schema as hw_schema
from schemas.account.schema import account_schema
from schemas.movement.schema import movement_schema

app = Flask(__name__)

# Routes
app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=hw_schema,
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
    app.run(host='0.0.0.0', port=5000, debug=True)
