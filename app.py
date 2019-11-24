from flask import Flask
from flask_cors import CORS
from flask_graphql import GraphQLView
from flask_graphql_auth import GraphQLAuth

from schemas.account.schema import account_schema
from schemas.movement.schema import movement_schema
from schemas.user.schema import user_schema

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'

app.config["EMAIL_CONFIRM_SECRET_KEY"] = r"$Godin.Financiero.Email.Confirm"  # change this!
# JWT configuration.
auth = GraphQLAuth(app)
app.config["JWT_SECRET_KEY"] = r"$Godin.Financiero.App"  # change this!
app.config["REFRESH_EXP_LENGTH"] = False
app.config["ACCESS_EXP_LENGTH"] = 10

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
    app.run(host='0.0.0.0', port=5000, debug=True)
    # app.run(host='0.0.0.0', debug=False)
