from .serializers import (
    ModelInfo, ModelInfoSerializer, ModelField, ModelFieldSerializer,
    SerializerInfo, SerializerInfoSerializer, SerializerField, SerializerFieldSerializer
)
from rest_framework.viewsets import ModelViewSet
from djuix.helper import Helper
from rest_framework.response import Response
from djuix.functions import WriteToModel, WriteToSerializer
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
        serializer.save()
        
        model_id = serializer.data["id"]
        active_model = self.queryset.get(id=model_id)

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
            active_model.app, model_data).write_model()
        if not status_content:
            active_model.delete()
            raise Exception("There was an issue creating")

        # run migration
        try:
            TerminalController(active_model.app.project.project_path,
                           active_model.app.project.name).run_migration()
        except Exception as e:
            active_model.delete()
            Helper.handleException(e)

        return Response(self.serializer_class(active_model).data, status=201)


class SerializerFieldView(ModelViewSet):
    queryset = SerializerField.objects.select_related("serializer_main")
    serializer_class = SerializerFieldSerializer

    def create(self, request, *args, **kwargs):
        data = Helper.normalizer_request(request.data)
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)

        # ensure that field name is unique to serializer
        if self.queryset.filter(serializer_main_id=data["serializer_main_id"], name__iexact=data["name"]):
            raise Exception(
                "A field with this name already exist for this serializer")

        serializer.save()

        return Response(serializer.data, status=201)


class SerializerInfoView(ModelViewSet):
    queryset = SerializerInfo.objects.select_related("app", "model_relation")
    serializer_class = SerializerInfoSerializer

    def create(self, request, *args, **kwargs):
        data = Helper.normalizer_request(request.data)

        fields = data.pop("fields", None)
        if not data.get("model_relation_id", None) and not fields:
            raise Exception(
                "You need to specify serializer fields since there is no model attached")

        if fields and not isinstance(fields, list):
            fields = [fields]

        # create serializer
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)

        # ensure that serializer name is unique to app
        if self.queryset.filter(app_id=data["app_id"], name__iexact=data["name"]):
            raise Exception(
                "A serializer with this name already exist for this App")

        serializer.save()
        serializer_id = serializer.data["id"]
        active_serializer = self.queryset.get(id=serializer_id)

        if fields:
            # create fields
            for field_data in fields:
                field_data.update({
                    "serializer_main_id": serializer_id
                })

                class req:
                    pass
                req.data = field_data

                SerializerFieldView().create(req, *args, **kwargs)

        serializer_data = self.queryset.filter(app_id=data["app_id"])
        status_content = WriteToSerializer(
            active_serializer.app, serializer_data).write_to_serializer()

        if not status_content:
            active_serializer.delete()
            raise Exception("There was an issue creating")

        return Response(self.serializer_class(active_serializer).data, status=201)
