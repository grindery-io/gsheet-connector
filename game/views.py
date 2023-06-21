import os
import requests
import json
from itertools import zip_longest
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import GenericAPIView

from .serializers import ConnectorSerializer
from common.serializers import serialize_worksheet, serialize_spreadsheet

from .request_prefix import REQUEST_PREFIX

scope = ['https://www.googleapis.com/auth/spreadsheets']
url = REQUEST_PREFIX + "sheets.googleapis.com/v4/spreadsheets/{}/values/{}!A1:ZZZ9999?majorDimension=ROWS&valueRenderOption=UNFORMATTED_VALUE"
url_spread_sheet = REQUEST_PREFIX + "sheets.googleapis.com/v4/spreadsheets/{}/"


class FileListView(GenericAPIView):
    serializer_class = ConnectorSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        params = serializer.data.get('params')
        method = serializer.data.get('method')
        request_id = serializer.data.get('id')

        key = params['key']
        spreadsheet = params['fieldData']['spreadsheet']
        worksheet = params['fieldData']['worksheet']
        access_token = params['authentication']
        token_type = 'Bearer'

        get_spreadsheets_url = REQUEST_PREFIX + 'www.googleapis.com/drive/v3/files/'
        get_spreadsheets_header = {
            'Authorization': 'Bearer ' + access_token,
            'Content-Type': 'application/json'
        }
        get_spreadsheets_params = {
            'token_type': token_type,
            'pageSize': 1000,
            'q': "mimeType = 'application/vnd.google-apps.spreadsheet'"
        }

        get_spreadsheets_res = requests.get(get_spreadsheets_url, headers=get_spreadsheets_header, params=get_spreadsheets_params)
        try:
            body = json.loads(get_spreadsheets_res.content)
            if "files" not in body:
                print(repr(body))
            spreadsheets_list = json.loads(get_spreadsheets_res.content)['files']
        except Exception as e:
            print("Error while getting spreadsheet list")
            print(repr(e))
            spreadsheets_list = []
        spreadsheets_list_array = []
        if spreadsheets_list:
            for item in spreadsheets_list:
                if item['mimeType'] == 'application/vnd.google-apps.spreadsheet':
                    spreadsheets_list_array.append({
                        **serialize_spreadsheet(item)
                    })

        if spreadsheet is None and worksheet is None:
            return Response(
                {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "inputFields": [
                            {
                                "key": "spreadsheet",
                                "label": "Spreadsheet",
                                "helpText": "",
                                "type": "string",
                                "required": True,
                                "placeholder": "Choose sheet...",
                                "choices": spreadsheets_list_array
                            }
                        ]
                    }
                },
                status=status.HTTP_201_CREATED
            )

        elif spreadsheet is not None and worksheet is None:
            get_sheets_url = REQUEST_PREFIX + 'sheets.googleapis.com/v4/spreadsheets/{}/'.format(spreadsheet)
            get_sheets_header = {
                'Authorization': 'Bearer ' + access_token
            }
            get_sheets_res = requests.get(get_sheets_url, headers=get_sheets_header)
            try:
                sheets_list = json.loads(get_sheets_res.content)['sheets']
            except BaseException as e:
                print("Error when getting sheet:", e)
                sheets_list = []
            sheets_list_array = []
            if sheets_list:
                for sheet in sheets_list:
                    sheets_list_array.append({
                        **serialize_worksheet(sheet)
                    })

            return Response(
                {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "inputFields": [
                            {
                                "key": "spreadsheet",
                                "label": "Spreadsheet",
                                "helpText": "",
                                "type": "string",
                                "required": True,
                                "placeholder": "Choose sheet...",
                                "choices": spreadsheets_list_array
                            },
                            {
                                "key": "worksheet",
                                "label": "Worksheet",
                                "helpText": "",
                                "type": "string",
                                "required": True,
                                "placeholder": "Choose sheet...",
                                "choices": sheets_list_array
                            }
                        ]
                    }
                },
                status=status.HTTP_201_CREATED
            )
        elif spreadsheet is not None and worksheet is not None:
            get_sheets_url = REQUEST_PREFIX + 'sheets.googleapis.com/v4/spreadsheets/{}/'.format(spreadsheet)
            get_sheets_header = {
                'Authorization': 'Bearer ' + access_token
            }
            get_sheets_res = requests.get(get_sheets_url, headers=get_sheets_header)
            try:
                sheets_list = json.loads(get_sheets_res.content)['sheets']
            except BaseException as e:
                print("Error when getting sheet:", e)
                sheets_list = []
            sheets_list_array = []
            if sheets_list:
                for sheet in sheets_list:
                    sheets_list_array.append({
                        **serialize_worksheet(sheet)
                    })

            worksheet_response = requests.get(url.format(spreadsheet, worksheet), headers=get_spreadsheets_header)
            try:
                worksheet_data = json.loads(worksheet_response.content)['values']
            except:
                worksheet_data = []
            out_put_fields = []
            sample_array = {}
            if worksheet_data:
                for data, last_data in zip_longest(worksheet_data[0], worksheet_data[len(worksheet_data) - 1]):
                    out_put_fields.append({
                        "key": data.replace(" ", "_"),
                        "label": data,
                        "type": "string"
                    })
                    sample_array[data.replace(" ", "_")] = last_data if last_data is not None else ""

            return Response(
                {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "inputFields": [
                            {
                                "key": "spreadsheet",
                                "label": "Spreadsheet",
                                "helpText": "",
                                "type": "string",
                                "required": True,
                                "placeholder": "Choose sheet...",
                                "choices": spreadsheets_list_array
                            },
                            {
                                "key": "worksheet",
                                "label": "Worksheet",
                                "helpText": "",
                                "type": "string",
                                "required": True,
                                "placeholder": "Choose sheet...",
                                "choices": sheets_list_array
                            }
                        ],
                        "outputFields": out_put_fields,
                        "sample": sample_array
                    }
                },
                status=status.HTTP_201_CREATED
            )


class FirstRowView(GenericAPIView):
    serializer_class = ConnectorSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        params = serializer.data.get('params')
        method = serializer.data.get('method')
        request_id = serializer.data.get('id')

        key = params['key']
        spreadsheet = params['fieldData']['spreadsheet']
        worksheet = params['fieldData']['worksheet']
        access_token = params['authentication']
        token_type = "Bearer"

        get_spreadsheets_url = REQUEST_PREFIX + 'www.googleapis.com/drive/v3/files/'
        get_spreadsheets_header = {
            'Authorization': 'Bearer ' + access_token,
            'Content-Type': 'application/json'
        }
        get_spreadsheets_params = {
            'token_type': token_type,
            'pageSize': 1000,
            'q': "mimeType = 'application/vnd.google-apps.spreadsheet'"
        }

        get_spreadsheets_res = requests.get(get_spreadsheets_url, headers=get_spreadsheets_header, params=get_spreadsheets_params)
        try:
            spreadsheets_list = json.loads(get_spreadsheets_res.content)['files']
        except Exception as e:
            print("Error while getting spreadsheet list")
            print(e)
            spreadsheets_list = []
        spreadsheets_list_array = []
        if spreadsheets_list:
            for item in spreadsheets_list:
                if item['mimeType'] == 'application/vnd.google-apps.spreadsheet':
                    spreadsheets_list_array.append({
                        **serialize_spreadsheet(item)
                    })

        if spreadsheet is None and worksheet is None:
            return Response(
                {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "inputFields": [
                            {
                                "key": "spreadsheet",
                                "label": "Spreadsheet",
                                "helpText": "",
                                "type": "string",
                                "required": True,
                                "placeholder": "Choose sheet...",
                                "choices": spreadsheets_list_array
                            }
                        ]
                    }
                },
                status=status.HTTP_201_CREATED
            )

        elif spreadsheet is not None and worksheet is None:
            get_sheets_url = REQUEST_PREFIX + 'sheets.googleapis.com/v4/spreadsheets/{}/'.format(spreadsheet)
            get_sheets_header = {
                'Authorization': 'Bearer ' + access_token,
                'Content-Type': 'application/json'
            }
            get_sheets_res = requests.get(get_sheets_url, headers=get_sheets_header)
            try:
                sheets_list = json.loads(get_sheets_res.content)['sheets']
            except BaseException as e:
                print("Error when getting sheet:", e)
                sheets_list = []
            sheets_list_array = []
            if sheets_list:
                for sheet in sheets_list:
                    sheets_list_array.append({
                        **serialize_worksheet(sheet)
                    })

            return Response(
                {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "inputFields": [
                            {
                                "key": "spreadsheet",
                                "label": "Spreadsheet",
                                "helpText": "",
                                "type": "string",
                                "required": True,
                                "placeholder": "Choose sheet...",
                                "choices": spreadsheets_list_array
                            },
                            {
                                "key": "worksheet",
                                "label": "Worksheet",
                                "helpText": "",
                                "type": "string",
                                "required": True,
                                "placeholder": "Choose sheet...",
                                "choices": sheets_list_array
                            }
                        ]
                    }
                },
                status=status.HTTP_201_CREATED
            )
        elif spreadsheet is not None and worksheet is not None:
            get_sheets_url = REQUEST_PREFIX + 'sheets.googleapis.com/v4/spreadsheets/{}/'.format(spreadsheet)
            get_sheets_header = {
                'Authorization': 'Bearer ' + access_token,
                'Content-Type': 'application/json'
            }
            get_sheets_res = requests.get(get_sheets_url, headers=get_sheets_header)
            try:
                sheets_list = json.loads(get_sheets_res.content)['sheets']
            except BaseException as e:
                print("Error when getting sheet:", e)
                sheets_list = []
            sheets_list_array = []
            if sheets_list:
                for sheet in sheets_list:
                    sheets_list_array.append({
                        **serialize_worksheet(sheet)
                    })

            worksheet_response = requests.get(url.format(spreadsheet, worksheet), headers=get_spreadsheets_header)
            try:
                worksheet_data = json.loads(worksheet_response.content)['values']
            except:
                worksheet_data = []
            out_put_fields = []
            sample_array = {}
            if worksheet_data:
                for data, last_data in zip_longest(worksheet_data[0], worksheet_data[len(worksheet_data) - 1]):
                    out_put_fields.append({
                        "key": "_" + data.replace(" ", "_"),
                        "label": data,
                        "type": "string"
                    })
                    sample_array[data.replace(" ", "_")] = last_data if last_data is not None else ""

            return Response(
                {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "inputFields": [
                            {
                                "key": "spreadsheet",
                                "label": "Spreadsheet",
                                "helpText": "",
                                "type": "string",
                                "required": True,
                                "placeholder": "Choose sheet...",
                                "choices": spreadsheets_list_array
                            },
                            {
                                "key": "worksheet",
                                "label": "Worksheet",
                                "helpText": "",
                                "type": "string",
                                "required": True,
                                "placeholder": "Choose sheet...",
                                "choices": sheets_list_array
                            },
                            *out_put_fields
                        ],
                        "sample": sample_array
                    }
                },
                status=status.HTTP_201_CREATED
            )


class SheetListView(GenericAPIView):

    def get(self, request):
        access_token = request.GET.get("access_token")
        spread_sheet_id = request.GET.get("spread_sheet_id")
        get_sheets_url = REQUEST_PREFIX + 'sheets.googleapis.com/v4/spreadsheets/{}/'.format(spread_sheet_id)
        header = {
            'Authorization': 'Bearer ' + access_token,
            'Content-Type': 'application/json'
        }
        res = requests.get(get_sheets_url, headers=header)
        sheets_list = json.loads(res.content)['sheets']

        return Response(
            {
                "result": True,
                "data": sheets_list
            },
            status=status.HTTP_201_CREATED
        )


class RowListView(GenericAPIView):
    serializer_class = ConnectorSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        params = serializer.data.get('params')
        method = serializer.data.get('method')
        request_id = serializer.data.get('id')

        key = params['key']
        spreadsheet = params['fieldData']['spreadsheet']
        worksheet = params['fieldData']['worksheet']
        access_token = params['authentication']
        token_type = 'Bearer'

        get_spreadsheets_url = REQUEST_PREFIX + 'www.googleapis.com/drive/v3/files/'
        get_spreadsheets_header = {
            'Authorization': 'Bearer ' + access_token,
            'Content-Type': 'application/json'
        }
        get_spreadsheets_params = {
            'token_type': token_type,
            'pageSize': 1000,
            'q': "mimeType = 'application/vnd.google-apps.spreadsheet'"
        }

        get_spreadsheets_res = requests.get(
            get_spreadsheets_url, headers=get_spreadsheets_header, params=get_spreadsheets_params)
        try:
            body = json.loads(get_spreadsheets_res.content)
            if "files" not in body:
                print(repr(body))
            spreadsheets_list = json.loads(
                get_spreadsheets_res.content)['files']
        except Exception as e:
            print("Error while getting spreadsheet list")
            print(repr(e))
            spreadsheets_list = []
        spreadsheets_list_array = []
        if spreadsheets_list:
            for item in spreadsheets_list:
                if item['mimeType'] == 'application/vnd.google-apps.spreadsheet':
                    spreadsheets_list_array.append({
                        **serialize_spreadsheet(item)
                    })

        if spreadsheet is None and worksheet is None:
            return Response(
                {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "inputFields": [
                            {
                                "key": "spreadsheet",
                                "label": "Spreadsheet",
                                "helpText": "",
                                "type": "string",
                                "required": True,
                                "placeholder": "Choose sheet...",
                                "choices": spreadsheets_list_array
                            }
                        ]
                    }
                },
                status=status.HTTP_201_CREATED
            )

        elif spreadsheet is not None and worksheet is None:
            get_sheets_url = REQUEST_PREFIX + \
                'sheets.googleapis.com/v4/spreadsheets/{}/'.format(spreadsheet)
            get_sheets_header = {
                'Authorization': 'Bearer ' + access_token
            }
            get_sheets_res = requests.get(
                get_sheets_url, headers=get_sheets_header)
            try:
                sheets_list = json.loads(get_sheets_res.content)['sheets']
            except BaseException as e:
                print("Error when getting sheet:", e)
                sheets_list = []
            sheets_list_array = []
            if sheets_list:
                for sheet in sheets_list:
                    sheets_list_array.append({
                        **serialize_worksheet(sheet)
                    })

            return Response(
                {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "inputFields": [
                            {
                                "key": "spreadsheet",
                                "label": "Spreadsheet",
                                "helpText": "",
                                "type": "string",
                                "required": True,
                                "placeholder": "Choose sheet...",
                                "choices": spreadsheets_list_array
                            },
                            {
                                "key": "worksheet",
                                "label": "Worksheet",
                                "helpText": "",
                                "type": "string",
                                "required": True,
                                "placeholder": "Choose sheet...",
                                "choices": sheets_list_array
                            }
                        ]
                    }
                },
                status=status.HTTP_201_CREATED
            )
        elif spreadsheet is not None and worksheet is not None:
            get_sheets_url = REQUEST_PREFIX + \
                'sheets.googleapis.com/v4/spreadsheets/{}/'.format(spreadsheet)
            get_sheets_header = {
                'Authorization': 'Bearer ' + access_token
            }
            get_sheets_res = requests.get(
                get_sheets_url, headers=get_sheets_header)
            try:
                sheets_list = json.loads(get_sheets_res.content)['sheets']
            except BaseException as e:
                print("Error when getting sheet:", e)
                sheets_list = []
            sheets_list_array = []

            if sheets_list:
                for sheet in sheets_list:
                    sheets_list_array.append({
                        **serialize_worksheet(sheet)
                    })
            worksheet_response = requests.get(url.format(
                spreadsheet, worksheet), headers=get_spreadsheets_header)
            try:
                worksheet_data = json.loads(
                    worksheet_response.content)['values']
            except:
                worksheet_data = []

            out_put_fields = []
            sample_array = {}

            if worksheet_data:
                headers = worksheet_data[0]
                for row in worksheet_data:
                    for i in range(len(headers)):
                        row_data = {}
                        row_data["key"] = "row" + \
                            str(worksheet_data.index(row) + 1)
                        row_data["label"] = row[i]
                        row_data["type"] = "string"
                        row_data["list"] = True
                        out_put_fields.append(row_data)
                    for i, row in enumerate(worksheet_data):
                        row_data = [cell for cell in row]
                        sample_array["row" + str(i + 1)] = row_data

            return Response(
                {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "inputFields": [
                            {
                                "key": "spreadsheet",
                                "label": "Spreadsheet",
                                "helpText": "",
                                "type": "string",
                                "required": True,
                                "placeholder": "Choose sheet...",
                                "choices": spreadsheets_list_array
                            },
                            {
                                "key": "worksheet",
                                "label": "Worksheet",
                                "helpText": "",
                                "type": "string",
                                "required": True,
                                "placeholder": "Choose sheet...",
                                "choices": sheets_list_array
                            }
                        ],
                        "outputFields": out_put_fields,
                        "sample": sample_array
                    }
                },
                status=status.HTTP_201_CREATED
            )


def get_sheet_data_by_token(spread_sheet_id, sheet_id, access_token):
    header = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json'
    }
    res = requests.get(url.format(spread_sheet_id, sheet_id), headers=header)
    return json.loads(res.content)['values']


def get_number_of_rows_by_token(spread_sheet_id, sheet_id, access_token):
    header = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json'
    }
    res = requests.get(url.format(spread_sheet_id, sheet_id), headers=header)
    return len(json.loads(res.content)['values'])


def get_new_rows_by_token(spread_sheet_id, sheet_id, access_token, number_of_added_rows):
    header = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json'
    }
    res = requests.get(url.format(spread_sheet_id, sheet_id), headers=header)
    rows = json.loads(res.content)['values']
    rows_objects = []
    for row in rows[len(rows) - number_of_added_rows: len(rows)]:
        row_object = {}
        for first_row, any_row in zip(rows[0], row):
            row_object[first_row.replace(" ", "_")] = any_row
        rows_objects.append(row_object)
    return rows_objects


def get_number_of_sheets(spread_sheet_id, access_token):
    header = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json'
    }
    res = requests.get(url_spread_sheet.format(spread_sheet_id), headers=header)
    return len(json.loads(res.content)['sheets'])


def get_new_sheets(spread_sheet_id, access_token, number_of_added_sheets):
    header = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json'
    }
    res = requests.get(url_spread_sheet.format(spread_sheet_id), headers=header)
    sheets = json.loads(res.content)['sheets']
    sheets_object = []
    for sheet in sheets[len(sheets) - number_of_added_sheets: len(sheets)]:
        sheets_object.append(sheet["properties"]["title"])
    return sheets_object


def get_rows_by_token(spread_sheet_id, sheet_id, access_token):
    header = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json'
    }
    return requests.get(url.format(spread_sheet_id, sheet_id), headers=header)

