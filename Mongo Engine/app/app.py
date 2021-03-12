from flask import Flask, Blueprint
import os
from dotenv import load_dotenv
from config import app_config
from app.routes import v1
from app.errors import init_error_handeler
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from flask_apispec.extension import FlaskApiSpec





app = Flask(__name__, template_folder='../template', static_folder='../static/')
UPLOAD_FOLDER = os.path.join('../app/', '../static/')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
load_dotenv("../.env", verbose=True)
app.config.from_object(app_config[os.environ.get("APP_CONFIG", "development")])


'''
@app.before_first_request
def before_first_request():
    log.info("before_first_request")
    log.info("indexes created")
    NewsModel.create_index()
'''

init_error_handeler(app)


SWAGGER_URL = '/swagger'
API_URL = 'swagger.json'

app.config.update({
    'APISPEC_SPEC': APISpec(
        title='Robofa_RoboNews Project',
        version='v1',
        plugins=[MarshmallowPlugin()],
        openapi_version='2.0.0'
    ),
    'APISPEC_SWAGGER_URL': '/swagger/',  # URI to access API Doc JSON
    'APISPEC_SWAGGER_UI_URL': '/swagger-ui/'  # URI to access UI of API Doc
})
'''
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'Robofa_RoboNews'
    }
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
'''
for blueprint in vars(v1).values():
    if isinstance(blueprint, Blueprint):
        app.register_blueprint(blueprint, url_prefix="/Robonews/v1")
