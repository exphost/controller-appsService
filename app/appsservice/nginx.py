from flask import Blueprint, request, current_app
from flask_restx import Api, Resource, fields
import os
import jinja2
import glob
import yaml
from .helpers import auth_required, git_pull, has_access_to_org
from .common import create_project_if_needed

bp = Blueprint('nginx', __name__, url_prefix='/nginx')
api = Api(bp, doc='/')

nginx_model = api.model(
    'Nginx',
    {
        'name': fields.String(
            description="App name",
            required=True,
            example="test-nginx"
        ),
        'org': fields.String(
            description="Organization that owns this app",
            required=True,
            example="test-org"
        ),
    }
)
nginx_query_model = api.model(
    'Nginx',
    {
        'org': fields.String(
            description="Organization that owns this app",
            required=True,
            example="test-org"
        ),
    }
)


@api.route("/", endpoint="nginx")
class Nginx(Resource):
    @api.expect(nginx_model, validate=True)
    @auth_required
    @has_access_to_org
    def post(self):
        git_pull(current_app)
        gitdir = current_app.config['gitdir']
        ingitpath = os.path.join(
            request.json['org'],
            "apps",
            request.json['name']+".yml"
        )
        apppath = os.path.join(
            gitdir,
            ingitpath
        )
        if os.path.exists(apppath):
            return "App already exists", 409
        with open("appsservice/templates/application_helm.j2", "r") as file:
            template = jinja2.Template(file.read())
        app = template.render(
            name=request.json['name'],
            org=request.json['org'],
            namespace="tenant-" + request.json['org'],
            project="tenant-" + request.json['org'],
            chart="nginx",
            version="10.0.1",
            repo="https://charts.bitnami.com/bitnami",
        )
        os.makedirs(os.path.dirname(apppath), exist_ok=True)
        current_app.config['gitsem'].acquire()
        create_project_if_needed(request.json['org'],
                                 current_app.config['repo'],
                                 gitdir)
        with open(apppath, 'w') as file:
            file.write(app)
        repo = current_app.config['repo']
        repo.index.add(ingitpath)
        repo.index.commit("add nginx")
        ssh_cmd = current_app.config['ssh_cmd']
        with repo.git.custom_environment(GIT_SSH_COMMAND=ssh_cmd):
            repo.remotes.origin.push().raise_if_error()
        current_app.config['gitsem'].release()
        return "Created", 201

    @auth_required
    @has_access_to_org
    def get(self):
        git_pull(current_app)
        org = request.args.get('org', None)
        if not org:
            return {'error': 'no org provided'}, 400
        orgdir = os.path.join(current_app.config['gitdir'], org)
        if not os.path.exists(orgdir):
            return {'nginx': [], 'status': 'org does not exists'}
        nginx = []
        for file in glob.glob(orgdir+"/apps/*.yml"):
            with open(file, "r") as f:
                app = yaml.safe_load(f)
            nginx.append({'name': app['metadata']['name']})
        return {'nginx': nginx}
