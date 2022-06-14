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


class CredentialsSerializer(serializers.Serializer):
    access_token = serializers.CharField(required=False)
    refresh_token = serializers.CharField(required=False)

    class Meta:
        fields = ("access_token", "refresh_token")

    def validate(self, attrs):
        access_token = attrs.get("access_token")
        refresh_token = attrs.get("refresh_token")
        res = {
            'access_token': access_token,
            'refresh_token': refresh_token
        }
        return res


class ParamSerializer(serializers.Serializer):
    key = serializers.CharField(required=False)
    fieldData = FieldDataSerializer()
    credentials = CredentialsSerializer()

    class Meta:
        fields = ("key", "fieldData", "credentials")

    def validate(self, attrs):
        key = attrs.get("key")
        fieldData = attrs.get("fieldData")
        credentials = attrs.get("credentials")
        # attrs['key'] = key
        # attrs['fieldData'] = fieldData
        # attrs['credentials'] = credentials
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
