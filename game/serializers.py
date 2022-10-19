from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from common.exception import CustomException


class FieldDataSerializer(serializers.Serializer):
    spreadsheet = serializers.CharField(required=False)
    worksheet = serializers.CharField(required=False)

    class Meta:
        fields = ("spreadsheet", "worksheet")

    def validate(self, attrs):
        spreadsheet = attrs.get("spreadsheet")
        worksheet = attrs.get("worksheet")
        attrs = {
            'spreadsheet': spreadsheet,
            'worksheet': worksheet
        }
        return attrs


class ParamSerializer(serializers.Serializer):
    key = serializers.CharField(required=False)
    fieldData = FieldDataSerializer()
    authentication = serializers.CharField(required=False)

    class Meta:
        fields = ("key", "fieldData", "authentication")

    def validate(self, attrs):
        key = attrs.get("key")
        fieldData = attrs.get("fieldData")
        authentication = attrs.get("authentication")
        # attrs['key'] = key
        # attrs['fieldData'] = fieldData
        # attrs['authentication'] = authentication
        return attrs


class ConnectorSerializer(serializers.Serializer):
    method = serializers.CharField()
    id = serializers.CharField()
    params = ParamSerializer()

    default_error_messages = {
        'invalid_type': _('type is invalid.'),
    }

    class Meta:
        fields = ("params", "method", "id")

    def validate(self, attrs):
        return attrs
