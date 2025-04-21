from unittest import TestCase, main, mock

import requests_mock
from projectv2.field import Field
from projectv2.project import Project


def test_project_load():
    data = {
        "title": "Test Project",
        "description": "This is a test project",
        "id": "MDExOlByb2plY3RWMi0xMjM0NTY3ODk=",
        "number": 1,
        "createdAt": "2019-01-01T00:00:00Z",
        "closedAt": None,
        "closed": False,
    }
    project = Project(data)

    assert project.title == "Test Project"
    assert project.description == "This is a test project"
    assert project.id == "MDExOlByb2plY3RWMi0xMjM0NTY3ODk="
    assert project.number == 1
    assert project.createdAt == "2019-01-01T00:00:00Z"
    assert project.closedAt is None
    assert project.closed is False


def test_project_load_fields():
    field_data1 = {
        "id": "12345",
        "name": "Test Field 1",
        "dataType": "STRING",
        "options": [],
    }
    field_data2 = {
        "id": "67890",
        "name": "Test Field 2",
        "dataType": "STRING",
        "options": [],
    }
    data = {
        "fields": [field_data1, field_data2],
    }
    project = Project(data)

    # Check the number of fields
    assert len(project.fields) == 2

    # Check that the fields are of the correct type
    assert isinstance(project.fields[0], Field)

    # Check the data of the second field
    assert project.fields[1].id == "67890"


def test_get_project(requests_mock):
    project_json = """{"data":{
        "organization":{
            "id":"MDEyOk9yZ2FuaXphdGlvbjk5MTk=",
            "projectV2":{
                "id":"PVT_kwDNJr_OABt_gg",
                "title":"my test project",
                "number":1234,
                "createdAt":"2022-10-06T16:04:16Z",
                "closedAt":null,
                "closed":false,
                "shortDescription":null,
                "public":false,
                "readme":"This is a test project"
            }
        }
    }}"""
    fields_json = """{
        "data": {
            "organization": {
            "id": "MDEyOk9yZ2FuaXphdGlvbjk5MTk=",
            "projectV2": {
                "id": "PVT_kwDNJr_OABt_gg",
                "fields": {
                "edges": [
                    {
                    "node": {
                        "id": "PVTF_lADNJr_OABt_gs4A_ZIp",
                        "name": "Title",
                        "dataType": "TITLE"
                    }
                    }
                ]
                }
            }
            }
        }
        }"""
    requests_mock.post(
        "https://api.github.com/graphql",
        [{"text": project_json}, {"text": fields_json}],
    )

    project = Project()
    project.get("myorg", 1234)

    # Check the title of the project
    assert project.title == "my test project"

    # Check the number of fields
    assert len(project.fields) == 1
