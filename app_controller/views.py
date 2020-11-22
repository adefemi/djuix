from .serializers import (
    ModelInfo, ModelInfoSerializer, ModelField, ModelFieldSerializer,
)
from rest_framework.viewsets import ModelViewSet
from djuix.helper import Helper
from rest_framework.response import Response
from djuix.functions import WriteToModel
from controllers.terminal_controller import TerminalController


class ModelFieldView(ModelViewSet):
    queryset = ModelField.objects.select_related("model_main")
    serializer_class = ModelFieldSerializer

    def create(self, request, *args, **kwargs):
        data = Helper.normalizer_request(request.data)
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)

        # ensure that field name is unique to model
        if self.queryset.filter(model_main_id=data["model_main_id"], name__iexact=data["name"]):
            raise Exception(
                "A field with this name already exist for this model")

        serializer.save()

        return Response(serializer.data, status=201)


class ModelInfoView(ModelViewSet):
    queryset = ModelInfo.objects.select_related("app")
    serializer_class = ModelInfoSerializer

    def create(self, request, *args, **kwargs):
        data = Helper.normalizer_request(request.data)

        fields = data.pop("fields", None)
        if not fields:
            raise Exception("A model requires at least one field")

        if not isinstance(fields, list):
            fields = [fields]

        # create model
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)

        # ensure that model name is unique to app
        if self.queryset.filter(app_id=data["app_id"], name__iexact=data["name"]):
            raise Exception(
                "A model with this name already exist for this App")

        serializer.save()
        model_id = serializer.data["id"]

        # create fields
        for field_data in fields:
            field_data.update({
                "model_main_id": model_id
            })

            class req:
                pass
            req.data = field_data

            ModelFieldView().create(req, *args, **kwargs)

        model_data = self.queryset.filter(app_id=data["app_id"])
        status_content = WriteToModel(
            model_data[0].app, model_data).write_model()
        if not status_content:
            model_data.delete()
            raise Exception("There was an issue creating")

        # run migration
        TerminalController(model_data[0].app.project.project_path,
                           model_data[0].app.project.name).run_migration()

        return Response(self.serializer_class(self.queryset.get(id=model_id)).data, status=201)
