import json
import schedule
from crontab import CronTab
from channels.generic.websocket import AsyncWebsocketConsumer
from .views import get_sheet_data


class SocketAdapter(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        print('-----socket disconnected-----')

    async def receive(self, text_data=None, bytes_data=None):
        request = json.loads(text_data)
        method = request.get("method", None)
        params = request.get("params", None)
        id = request.get("id", None)
        key = params['key']
        session_id = params['sessionId']
        credentials = params['credentials']
        spreadsheet_id = params['fields']['spreadsheetId']
        sheet_id = params['fields']['sheetId']

        access_token = params['credentials']['access_token']

        if method == 'setupSignal':
            setup_signal_response = {
                'jsonrpc': '2.0',
                'method': 'notifySignal',
                'params': {
                    'key': 'googleSheetNewRowTrigger',
                    'sessionId': session_id,
                    'payload': {
                        'spreadsheetId': spreadsheet_id,
                        'sheetId': sheet_id,
                        'response': json.loads(get_sheet_data(spreadsheet_id, sheet_id))
                    }
                }
            }
            # create_cron_job(spreadsheet_id)
            create_schedule_job()
            await self.send(text_data=json.dumps(setup_signal_response))

        if method == 'runAction':
            run_action_response = {
                'jsonrpc': '2.0',
                'result': {
                    'key': 'googleSheetNewRowAction',
                    'sessionId': session_id,
                    'payload': {}
                },
                'id': id
            }
            await self.send(text_data=json.dumps(run_action_response))

        if method == 'ping':
            await self.accept()

    async def send_message(self, res):
        """ Receive message from room group """
        # Send message to WebSocket
        await self.send(text_data=json.dumps(res))


def create_cron_job(spread_sheet_id):
    # cron = CronTab(tab="""* * * * * command""")
    cron = CronTab(user="root")
    job = cron.new(command='python scheduleCron.py')
    job.minute.every(1)

    cron.write()
