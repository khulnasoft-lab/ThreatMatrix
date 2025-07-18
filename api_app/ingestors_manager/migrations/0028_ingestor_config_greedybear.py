from django.db import migrations
from django.db.models.fields.related_descriptors import (
    ForwardManyToOneDescriptor,
    ForwardOneToOneDescriptor,
    ManyToManyDescriptor,
    ReverseManyToOneDescriptor,
    ReverseOneToOneDescriptor,
)

plugin = {
    "python_module": {
        "health_check_schedule": None,
        "update_schedule": {
            "minute": "0",
            "hour": "0",
            "day_of_week": "*",
            "day_of_month": "*",
            "month_of_year": "*",
        },
        "module": "greedybear.GreedyBear",
        "base_path": "api_app.ingestors_manager.ingestors",
    },
    "schedule": {
        "minute": "0",
        "hour": "0",
        "day_of_week": "*",
        "day_of_month": "*",
        "month_of_year": "*",
    },
    "periodic_task": {
        "crontab": {
            "minute": "0",
            "hour": "0",
            "day_of_week": "*",
            "day_of_month": "*",
            "month_of_year": "*",
        },
        "name": "GreedyBearIngestor",
        "task": "threat_matrix.tasks.execute_ingestor",
        "kwargs": '{"config_name": "GreedyBear"}',
        "queue": "default",
        "enabled": False,
    },
    "user": {
        "username": "GreedyBearIngestor",
        "profile": {
            "user": {
                "username": "GreedyBearIngestor",
                "email": "",
                "first_name": "",
                "last_name": "",
                "password": "",
                "is_active": True,
            },
            "company_name": "",
            "company_role": "",
            "twitter_handle": "",
            "discover_from": "other",
            "task_priority": 7,
            "is_robot": True,
        },
    },
    "playbooks_choice": ["Popular_IP_Reputation_Services"],
    "name": "GreedyBear",
    "description": "Queries feeds which are generated by the [GreedyBear Project](https://khulnasoft.github.io/docs/GreedyBear/Introduction/).",
    "disabled": True,
    "soft_time_limit": 60,
    "routing_key": "ingestor",
    "health_check_status": True,
    "maximum_jobs": 50,
    "delay": "00:00:00",
    "model": "ingestors_manager.IngestorConfig",
}

params = [
    {
        "python_module": {
            "module": "greedybear.GreedyBear",
            "base_path": "api_app.ingestors_manager.ingestors",
        },
        "name": "url",
        "type": "str",
        "description": "API endpoint",
        "is_secret": False,
        "required": False,
    },
    {
        "python_module": {
            "module": "greedybear.GreedyBear",
            "base_path": "api_app.ingestors_manager.ingestors",
        },
        "name": "limit",
        "type": "int",
        "description": "Max number of results.",
        "is_secret": False,
        "required": False,
    },
    {
        "python_module": {
            "module": "greedybear.GreedyBear",
            "base_path": "api_app.ingestors_manager.ingestors",
        },
        "name": "feed_type",
        "type": "str",
        "description": "The available feed types are log4j, cowrie, and all.",
        "is_secret": False,
        "required": False,
    },
    {
        "python_module": {
            "module": "greedybear.GreedyBear",
            "base_path": "api_app.ingestors_manager.ingestors",
        },
        "name": "attack_type",
        "type": "str",
        "description": "The available attack_type are scanner, payload_request, and all.",
        "is_secret": False,
        "required": False,
    },
    {
        "python_module": {
            "module": "greedybear.GreedyBear",
            "base_path": "api_app.ingestors_manager.ingestors",
        },
        "name": "age",
        "type": "str",
        "description": "The available age are recent and persistent.",
        "is_secret": False,
        "required": False,
    },
]

values = [
    {
        "parameter": {
            "python_module": {
                "module": "greedybear.GreedyBear",
                "base_path": "api_app.ingestors_manager.ingestors",
            },
            "name": "url",
            "type": "str",
            "description": "API endpoint",
            "is_secret": False,
            "required": False,
        },
        "analyzer_config": None,
        "connector_config": None,
        "visualizer_config": None,
        "ingestor_config": "GreedyBear",
        "pivot_config": None,
        "for_organization": False,
        "value": "https://greedybear.honeynet.org",
        "updated_at": "2025-02-10T12:56:17.294680Z",
        "owner": None,
    },
    {
        "parameter": {
            "python_module": {
                "module": "greedybear.GreedyBear",
                "base_path": "api_app.ingestors_manager.ingestors",
            },
            "name": "limit",
            "type": "int",
            "description": "Max number of results.",
            "is_secret": False,
            "required": False,
        },
        "analyzer_config": None,
        "connector_config": None,
        "visualizer_config": None,
        "ingestor_config": "GreedyBear",
        "pivot_config": None,
        "for_organization": False,
        "value": 50,
        "updated_at": "2025-02-10T12:56:17.302177Z",
        "owner": None,
    },
    {
        "parameter": {
            "python_module": {
                "module": "greedybear.GreedyBear",
                "base_path": "api_app.ingestors_manager.ingestors",
            },
            "name": "feed_type",
            "type": "str",
            "description": "The available feed types are log4j, cowrie, and all.",
            "is_secret": False,
            "required": False,
        },
        "analyzer_config": None,
        "connector_config": None,
        "visualizer_config": None,
        "ingestor_config": "GreedyBear",
        "pivot_config": None,
        "for_organization": False,
        "value": "all",
        "updated_at": "2025-02-10T12:56:17.309549Z",
        "owner": None,
    },
    {
        "parameter": {
            "python_module": {
                "module": "greedybear.GreedyBear",
                "base_path": "api_app.ingestors_manager.ingestors",
            },
            "name": "attack_type",
            "type": "str",
            "description": "The available attack_type are scanner, payload_request, and all.",
            "is_secret": False,
            "required": False,
        },
        "analyzer_config": None,
        "connector_config": None,
        "visualizer_config": None,
        "ingestor_config": "GreedyBear",
        "pivot_config": None,
        "for_organization": False,
        "value": "all",
        "updated_at": "2025-02-10T12:56:17.316766Z",
        "owner": None,
    },
    {
        "parameter": {
            "python_module": {
                "module": "greedybear.GreedyBear",
                "base_path": "api_app.ingestors_manager.ingestors",
            },
            "name": "age",
            "type": "str",
            "description": "The available age are recent and persistent.",
            "is_secret": False,
            "required": False,
        },
        "analyzer_config": None,
        "connector_config": None,
        "visualizer_config": None,
        "ingestor_config": "GreedyBear",
        "pivot_config": None,
        "for_organization": False,
        "value": "recent",
        "updated_at": "2025-02-10T12:56:17.324439Z",
        "owner": None,
    },
]


def _get_real_obj(Model, field, value):
    def _get_obj(Model, other_model, value):
        if isinstance(value, dict):
            real_vals = {}
            for key, real_val in value.items():
                real_vals[key] = _get_real_obj(other_model, key, real_val)
            value = other_model.objects.get_or_create(**real_vals)[0]
        # it is just the primary key serialized
        else:
            if isinstance(value, int):
                if Model.__name__ == "PluginConfig":
                    value = other_model.objects.get(name=plugin["name"])
                else:
                    value = other_model.objects.get(pk=value)
            else:
                value = other_model.objects.get(name=value)
        return value

    if (
        type(getattr(Model, field))
        in [
            ForwardManyToOneDescriptor,
            ReverseManyToOneDescriptor,
            ReverseOneToOneDescriptor,
            ForwardOneToOneDescriptor,
        ]
        and value
    ):
        other_model = getattr(Model, field).get_queryset().model
        value = _get_obj(Model, other_model, value)
    elif type(getattr(Model, field)) in [ManyToManyDescriptor] and value:
        other_model = getattr(Model, field).rel.model
        value = [_get_obj(Model, other_model, val) for val in value]
    return value


def _create_object(Model, data):
    mtm, no_mtm = {}, {}
    for field, value in data.items():
        value = _get_real_obj(Model, field, value)
        if type(getattr(Model, field)) is ManyToManyDescriptor:
            mtm[field] = value
        else:
            no_mtm[field] = value
    try:
        o = Model.objects.get(**no_mtm)
    except Model.DoesNotExist:
        o = Model(**no_mtm)
        o.full_clean()
        o.save()
        for field, value in mtm.items():
            attribute = getattr(o, field)
            if value is not None:
                attribute.set(value)
        return False
    return True


def migrate(apps, schema_editor):
    Parameter = apps.get_model("api_app", "Parameter")
    PluginConfig = apps.get_model("api_app", "PluginConfig")
    python_path = plugin.pop("model")
    Model = apps.get_model(*python_path.split("."))
    if not Model.objects.filter(name=plugin["name"]).exists():
        exists = _create_object(Model, plugin)
        if not exists:
            for param in params:
                _create_object(Parameter, param)
            for value in values:
                _create_object(PluginConfig, value)


def reverse_migrate(apps, schema_editor):
    python_path = plugin.pop("model")
    Model = apps.get_model(*python_path.split("."))
    Model.objects.get(name=plugin["name"]).delete()


class Migration(migrations.Migration):
    atomic = False
    dependencies = [
        ("api_app", "0065_job_mpnodesearch"),
        ("ingestors_manager", "0027_added_limit_parameter_malware_bazaar_threatfox"),
    ]

    operations = [migrations.RunPython(migrate, reverse_migrate)]
