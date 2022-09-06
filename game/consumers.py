import json
import os
import asyncio
import requests
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from .views import get_sheet_data_by_token, get_new_rows_by_token, get_number_of_rows_by_token, get_number_of_sheets,\
    get_new_sheets


class newSpreadsheetRowTrigger:
    def __init__(self, socket, request):
        self.socket = socket
        self.request = request

    def start(self):
        return asyncio.create_task(newSpreadsheetRowTrigger.main(self))

    async def main(self):
        request = json.loads(self.request)
        params = request.get("params", None)
        session_id = params['sessionId']
        spreadsheet_id = params['fields']['spreadsheet']
        sheet_id = params['fields']['worksheet']
        access_token = ''

        try:
            refresh_token = params['credentials']['refresh_token']
            credentials_params = {
                'client_id': os.environ['client_id'],
                'client_secret': os.environ['client_secret'],
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token,
            }
            res = requests.post(url=os.environ['token_uri'], params=credentials_params)
            access_token = json.loads(res.content)['access_token']
        except Exception:
            access_token = params['credentials']['access_token']

        number_of_rows = get_number_of_rows_by_token(spreadsheet_id, sheet_id, access_token)

        while self.socket.connected:
            try:
                refresh_token = params['credentials']['refresh_token']
                credentials_params = {
                    'client_id': os.environ['client_id'],
                    'client_secret': os.environ['client_secret'],
                    'grant_type': 'refresh_token',
                    'refresh_token': refresh_token,
                }
                res = requests.post(url=os.environ['token_uri'], params=credentials_params)
                access_token = json.loads(res.content)['access_token']
            except Exception:
                access_token = params['credentials']['access_token']
            check_number_of_row = get_number_of_rows_by_token(spreadsheet_id, sheet_id, access_token)
            if check_number_of_row > number_of_rows:
                response = get_new_rows_by_token(spreadsheet_id, sheet_id, access_token, check_number_of_row - number_of_rows)
                number_of_rows = check_number_of_row
                for row in response:
                    await self.socket.send_json({
                        'jsonrpc': '2.0',
                        'method': 'notifySignal',
                        'params': {
                            'key': 'googleSheetNewRowTrigger',
                            'sessionId': session_id,
                            'payload': row
                        }
                    })
            await asyncio.sleep(60)


class newWorksheetTrigger:
    def __init__(self, socket, request):
        self.socket = socket
        self.request = request

    def start(self):
        return asyncio.create_task(newWorksheetTrigger.main(self))

    async def main(self):
        request = json.loads(self.request)
        params = request.get("params", None)
        session_id = params['sessionId']
        spreadsheet_id = params['fields']['spreadsheet']
        sheet_id = params['fields']['worksheet']
        access_token = ''

        try:
            refresh_token = params['credentials']['refresh_token']
            credentials_params = {
                'client_id': os.environ['client_id'],
                'client_secret': os.environ['client_secret'],
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token,
            }
            res = requests.post(url=os.environ['token_uri'], params=credentials_params)
            access_token = json.loads(res.content)['access_token']
        except Exception:
            access_token = params['credentials']['access_token']

        number_of_sheets = get_number_of_sheets(spreadsheet_id, access_token)

        while self.socket.connected:
            try:
                refresh_token = params['credentials']['refresh_token']
                credentials_params = {
                    'client_id': os.environ['client_id'],
                    'client_secret': os.environ['client_secret'],
                    'grant_type': 'refresh_token',
                    'refresh_token': refresh_token,
                }
                res = requests.post(url=os.environ['token_uri'], params=credentials_params)
                access_token = json.loads(res.content)['access_token']
            except Exception:
                access_token = params['credentials']['access_token']
            check_number_of_sheets = get_number_of_sheets(spreadsheet_id, access_token)
            if check_number_of_sheets > number_of_sheets:
                response = get_new_sheets(spreadsheet_id, access_token, check_number_of_sheets - number_of_sheets)
                number_of_sheets = check_number_of_sheets
                for sheet in response:
                    await self.socket.send_json({
                        'jsonrpc': '2.0',
                        'method': 'notifySignal',
                        'params': {
                            'key': 'googleSheetNewWorksheetTrigger',
                            'sessionId': session_id,
                            'payload': sheet
                        }
                    })
            await asyncio.sleep(60)


class SocketAdapter(AsyncJsonWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.background_tasks = set()
        self.connected = False

    async def connect(self):
        self.connected = True
        await self.accept()

    async def disconnect(self, close_code):
        self.connected = False
        print('-----socket disconnected-----')

    async def receive(self, text_data=None, bytes_data=None, **kwargs):
        request = json.loads(text_data)
        method = request.get("method", None)
        params = request.get("params", None)
        id = request.get("id", None)
        access_token = ''
        spreadsheet_id = ''
        sheet_id = ''
        session_id = ''
        fields = ''
        request_key = ''
        print('-----------------', request)

        if params is not None and params != {}:
            request_key = params['key']
            session_id = params['sessionId']
            credentials = params['credentials']
            fields = params['fields']
            spreadsheet_id = fields['spreadsheet']
            sheet_id = fields['worksheet']

            access_token = credentials['access_token']

        if method == 'setupSignal':
            if request_key and request_key != '':
                if request_key == 'newSpreadsheetRow':
                    self.background_tasks.add(newSpreadsheetRowTrigger(self, text_data).start())
                if request_key == 'newWorksheet':
                    self.background_tasks.add(newWorksheetTrigger(self, text_data).start())
                response = {
                    'jsonrpc': '2.0',
                    'result': {},
                    'id': id
                }
            else:
                response = {
                    'jsonrpc': '2.0',
                    'error': {
                        'code': 1,
                        'message': 'operation key is required'
                    },
                    'id': id
                }
            await self.send_json(response)

        if method == 'runAction':
            header = {
                'Authorization': 'Bearer ' + access_token,
                'Content-Type': 'application/json'
            }
            url = "https://sheets.googleapis.com/v4/spreadsheets/{}/values/{}!A1:ZZZZ99999:append?valueInputOption=USER_ENTERED".format(
                spreadsheet_id, sheet_id)

            values = []
            for key in fields:
                if key.startswith('_'):
                    # print(key.replace("_", " ").strip())
                    values.append(fields[key])
            payload = {"range": "{}!A1:Z1".format(sheet_id), "majorDimension": "ROWS", "values": [values]}
            try:
                res = requests.post(headers=header, url=url, json=payload)
                if res.status_code != 200:
                    fields = {}
            except Exception:
                fields = 'Error'
            run_action_response = {
                'jsonrpc': '2.0',
                'result': {
                    'key': 'googleSheetNewRowAction',
                    'sessionId': session_id,
                    'payload': fields
                },
                'id': id
            }
            await self.send_json(run_action_response)

        if method == 'ping':
            response = {
                'jsonrpc': '2.0',
                'result': {},
                'id': id
            }
            await self.send_json(response)
