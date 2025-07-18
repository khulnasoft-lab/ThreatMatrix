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
        "update_schedule": None,
        "module": "any_compare.AnyCompare",
        "base_path": "api_app.pivots_manager.pivots",
    },
    "related_analyzer_configs": ["ExpandURL"],
    "related_connector_configs": [],
    "playbooks_choice": ["Popular_URL_Reputation_Services"],
    "name": "ExpandedURLReputation",
    "description": "Pivot for plugins ExpandURL that executes playbooks Popular_URL_Reputation_Services",
    "disabled": False,
    "soft_time_limit": 60,
    "routing_key": "default",
    "health_check_status": True,
    "delay": "00:00:00",
    "model": "pivots_manager.PivotConfig",
}

params = [
    {
        "python_module": {
            "module": "any_compare.AnyCompare",
            "base_path": "api_app.pivots_manager.pivots",
        },
        "name": "field_to_compare",
        "type": "str",
        "description": "Dotted path to the field",
        "is_secret": False,
        "required": True,
    }
]

values = [
    {
        "parameter": {
            "python_module": {
                "module": "any_compare.AnyCompare",
                "base_path": "api_app.pivots_manager.pivots",
            },
            "name": "field_to_compare",
            "type": "str",
            "description": "Dotted path to the field",
            "is_secret": False,
            "required": True,
        },
        "analyzer_config": None,
        "connector_config": None,
        "visualizer_config": None,
        "ingestor_config": None,
        "pivot_config": "ExpandedURLReputation",
        "for_organization": False,
        "value": "actual_url",
        "updated_at": "2025-07-04T11:33:50.702088Z",
        "owner": None,
    }
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
        ("api_app", "0071_delete_last_elastic_report"),
        (
            "pivots_manager",
            "0036_alter_extractedonenotefiles_resubmitdownloadedfile_loadfilesameplaybook",
        ),
    ]

    operations = [migrations.RunPython(migrate, reverse_migrate)]
