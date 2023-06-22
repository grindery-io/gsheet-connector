import json
import os
import asyncio
import requests
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from .views import get_sheet_data_by_token, get_new_rows_by_token, get_number_of_rows_by_token, get_number_of_sheets,\
    get_new_sheets, get_rows_by_token

from .request_prefix import REQUEST_PREFIX

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
        access_token = params['authentication']

        number_of_rows = await asyncio.get_event_loop().run_in_executor(None, lambda: get_number_of_rows_by_token(spreadsheet_id, sheet_id, access_token))

        while self.socket.connected:
            print('--------Triggering--GSheet-------spreadsheet_id---', spreadsheet_id, '--------sheet_id-------', sheet_id)
            check_number_of_row = await asyncio.get_event_loop().run_in_executor(None, lambda: get_number_of_rows_by_token(spreadsheet_id, sheet_id, access_token))
            if check_number_of_row < number_of_rows:
                number_of_rows = check_number_of_row
            if check_number_of_row > number_of_rows:
                print('--------New-row-added----------spreadsheet_id', spreadsheet_id, '-----sheet_id----', sheet_id,
                      '-------added-------', check_number_of_row - number_of_rows)
                response = await asyncio.get_event_loop().run_in_executor(None, lambda: get_new_rows_by_token(spreadsheet_id, sheet_id, access_token, check_number_of_row - number_of_rows))
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
        access_token = params['authentication']

        number_of_sheets = await asyncio.get_event_loop().run_in_executor(None, lambda: get_number_of_sheets(spreadsheet_id, access_token))

        while self.socket.connected:
            check_number_of_sheets = await asyncio.get_event_loop().run_in_executor(None, lambda: get_number_of_sheets(spreadsheet_id, access_token))
            if check_number_of_sheets > number_of_sheets:
                response = await asyncio.get_event_loop().run_in_executor(None, lambda: get_new_sheets(spreadsheet_id, access_token, check_number_of_sheets - number_of_sheets))
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
        params = request.get("params", None)
        id = request.get("id", None)
        method = request.get("method", None)
        if method == 'ping':
            response = {
                'jsonrpc': '2.0',
                'result': {},
                'id': id
            }
            await self.send_json(response)
            return
        access_token = ''
        spreadsheet_id = ''
        sheet_id = ''
        session_id = ''
        fields = ''
        request_key = ''

        if params is not None and params != {}:
            request_key = params['key']
            session_id = params['sessionId']
            fields = params['fields']
            spreadsheet_id = fields['spreadsheet']
            sheet_id = fields['worksheet']

            access_token = params.get('authentication', '')

        if method == 'setupSignal':
            if request_key and request_key != '':
                if request_key == 'newSpreadsheetRow':
                    task = newSpreadsheetRowTrigger(self, text_data).start()
                if request_key == 'newWorksheet':
                    task = newWorksheetTrigger(self, text_data).start()
                self.background_tasks.add(task)
                def on_complete(t):
                    try:
                        t.result()
                    except BaseException as e:
                        print(request_key, ": Task raised error: ", e)
                    if self.connected:
                        self.close()
                task.add_done_callback(on_complete)
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
        elif method == 'runAction':
            if request_key  == 'getAllRows':
                try:
                    payload = await asyncio.get_event_loop().run_in_executor(None, lambda: get_rows_by_token(spreadsheet_id, sheet_id, access_token))
                    if payload.status_code == 200:
                        res = json.loads(payload.content)['values']
                    else:
                        res = {}
                except Exception:
                    res = 'Error'
                run_action_response = {
                    'jsonrpc': '2.0',
                    'result': {
                        'key': 'getAllRows',
                        'sessionId': session_id,
                        'payload': res
                    },
                    'id': id
                }
                await self.send_json(run_action_response)
            else:
                header = {
                    'Authorization': 'Bearer ' + access_token,
                    'Content-Type': 'application/json'
                }
                url = "{}sheets.googleapis.com/v4/spreadsheets/{}/values/{}!A1:ZZZ9999:append?valueInputOption=USER_ENTERED".format(
                    REQUEST_PREFIX, spreadsheet_id, sheet_id)

                values = []
                for key in fields:
                    if key.startswith('_'):
                        # print(key.replace("_", " ").strip())
                        values.append(fields[key])
                payload = {"range": "{}!A1:ZZZ9999".format(sheet_id), "majorDimension": "ROWS", "values": [values]}
                try:
                    res = await asyncio.get_event_loop().run_in_executor(None, lambda: requests.post(headers=header, url=url, json=payload, timeout=15))
                    if res.status_code != 200:
                        fields = {}
                except Exception as e:
                    print("Error when adding row:", repr(e))
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
        else:
            response = {
                'jsonrpc': '2.0',
                'error': {
                    'code': 1,
                    'message': 'unknown method'
                },
                'id': id
            }
            await self.send_json(response)
