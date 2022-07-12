import requests
import gspread
import json
from rest_framework.response import Response
from rest_framework import status
import pandas as pd
from rest_framework.generics import GenericAPIView
from oauth2client.service_account import ServiceAccountCredentials

from .serializers import ConnectorSerializer
from common.serializers import serialize_worksheet, serialize_spreadsheet

scope = ['https://www.googleapis.com/auth/spreadsheets']
url = "https://sheets.googleapis.com/v4/spreadsheets/{}/values/{}!A1:Z1000?majorDimension=ROWS"
credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
gc = gspread.authorize(credentials)


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
        access_token = params['credentials']['access_token']
        refresh_token = params['credentials']['refresh_token']
        scope = params['credentials']['scope']
        token_type = params['credentials']['token_type']
        if token_type is None:
            token_type = 'Bearer'
        if scope is None:
            scope = 'https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/drive.file openid https://www.googleapis.com/auth/spreadsheets https://www.googleapis.com/auth/drive'

        get_spreadsheets_url = 'https://www.googleapis.com/drive/v3/files/'
        get_spreadsheets_header = {
            'Authorization': 'Bearer ' + access_token,
            'Content-Type': 'application/json'
        }
        get_spreadsheets_params = {
            'token_type': token_type,
            'scope': scope,
            'refresh_token': refresh_token,
            'pageSize': 1000
        }

        get_spreadsheets_res = requests.get(get_spreadsheets_url, headers=get_spreadsheets_header, params=get_spreadsheets_params)
        try:
            spreadsheets_list = json.loads(get_spreadsheets_res.content)['files']
        except:
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
            get_sheets_url = 'https://sheets.googleapis.com/v4/spreadsheets/{}/'.format(spreadsheet)
            get_sheets_header = {
                'Authorization': 'Bearer ' + access_token,
                'Content-Type': 'application/json'
            }
            get_sheets_res = requests.get(get_sheets_url, headers=get_sheets_header)
            try:
                sheets_list = json.loads(get_sheets_res.content)['sheets']
            except:
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
            get_sheets_url = 'https://sheets.googleapis.com/v4/spreadsheets/{}/'.format(spreadsheet)
            get_sheets_header = {
                'Authorization': 'Bearer ' + access_token,
                'Content-Type': 'application/json'
            }
            get_sheets_res = requests.get(get_sheets_url, headers=get_sheets_header)
            try:
                sheets_list = json.loads(get_sheets_res.content)['sheets']
            except:
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
                for data, last_data in zip(worksheet_data[0], worksheet_data[len(worksheet_data) - 1]):
                    out_put_fields.append({
                        "key": data.replace(" ", "_"),
                        "label": data,
                        "type": "string"
                    })
                    sample_array[data.replace(" ", "_")] = last_data

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


class SheetListView(GenericAPIView):

    def get(self, request):
        access_token = request.GET.get("access_token")
        spread_sheet_id = request.GET.get("spread_sheet_id")
        get_sheets_url = 'https://sheets.googleapis.com/v4/spreadsheets/{}/'.format(spread_sheet_id)
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


def get_sheet_data(spread_sheet_id, sheet_id):
    sheet = gc.open_by_key(spread_sheet_id)
    sheet_instance = sheet.get_worksheet(sheet_id)
    all_rows = sheet_instance.get_all_records()
    records_df = pd.DataFrame.from_dict(all_rows)
    return records_df.to_json(orient="split")


def get_new_rows(spread_sheet_id, sheet_id, number_of_added_rows):
    sheet = gc.open_by_key(spread_sheet_id)
    sheet_instance = sheet.get_worksheet(sheet_id)
    all_rows = sheet_instance.get_all_records()
    return all_rows[len(all_rows) - number_of_added_rows:len(all_rows)]


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
            row_object[first_row] = any_row
        rows_objects.append(row_object)
    return rows_objects


def get_number_of_rows(spread_sheet_id, sheet_id):
    sheet = gc.open_by_key(spread_sheet_id)
    sheet_instance = sheet.get_worksheet(sheet_id)
    return len(sheet_instance.get_all_records())
