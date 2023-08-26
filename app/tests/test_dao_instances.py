import pytest
import yaml
import os


def test_get_instance(app):
    instance = app.dao.get_instance("test-org", "app1", "master")
    expected = {
            "values": {}
    }
    assert instance == expected


def test_get_instance_with_values(app):
    instance = app.dao.get_instance("test-org", "app1", "some-values")
    expected = {
            "values": {
                "key1": "value1",
            }
    }
    assert instance == expected


def test_get_instances(app):
    instances = app.dao.get_instances("test-org", "app1")
    expected = {
        "master": {
            "values": {}
        },
        "some-values": {
            "values": {
                "key1": "value1",
            }
        }
    }
    assert instances == expected


def test_get_instances_non_existing_org(app):
    with pytest.raises(FileNotFoundError):
        app.dao.get_instances("non-existing-org", "app1")


def test_get_instances_non_existing_app(app):
    with pytest.raises(FileNotFoundError):
        app.dao.get_instances("test-org", "non-existing-app")


def test_create_instance_manifest_content(app):
    instance = {
        "values": {
            "key2": "value2",
        }
    }
    app.dao.create_instance("test-org", "app1", "instance1", instance)
    with open(os.path.join(app.dao.gitdir, "instances", "test-org", "app1", "instance1.yml"), "r") as f:  # noqa E501
        content = yaml.safe_load(f)
    expected = yaml.safe_load("""apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: test-org-app1-instance1
  namespace: argocd
  labels:
    org: test-org
    app: app1
    instance: instance1
spec:
  destination:
    namespace: test-org-app1-instance1
    server: https://kubernetes.default.svc
  project: default
  source:
    path: apps/test-org/app1
    repoURL: git@gitlab.exphost.pl:exphost-controller/test_tenants_repo.git
    targetRevision: HEAD
    helm:
      values: |
        key2: value2
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
""")
    assert content == expected
