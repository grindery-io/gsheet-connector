import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer


class SocketAdapter(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        print('-----socket disconnected-----')

    async def receive(self, json_rpc):
        """
        Receive message from WebSocket.
        Get the event and send the appropriate event
        """
        request = json.loads(json_rpc)
        method = request.get("method", None)
        params = request.get("params", None)
        id = request.get("id", None)
        key = params['key']
        sessionId = params['sessionId']
        credentials = params['credentials']
        spreadsheetId = params['fields']['spreadsheetId']
        sheetId = params['fields']['sheetId']

        setUpSignalRes = {
            'jsonrpc': '2.0',
            'method': 'notifySignal',
            'params': {
                'key': 'googleSheetNewRowTrigger',
                'sessionId': sessionId,
                'payload': {
                    'spreadsheetId': spreadsheetId,
                    'sheetId': sheetId
                }
            }
        }

        runActionRes = {
            'jsonrpc': '2.0',
            'result': {
                'key': 'googleSheetNewRowAction',
                'sessionId': sessionId,
                'payload': {}
            },
            'id': id
        }

        if method == 'setupSignal':
            await self.send_json(setUpSignalRes)

        if method == 'runAction':
            await self.send_json(runActionRes)

        if method == 'ping':
            await self.accept()

    async def send_message(self, res):
        """ Receive message from room group """
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            "payload": res,
        }))
