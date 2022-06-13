import requests
import gspread
import json
import pandas as pd
from django.shortcuts import render, redirect
from django.http import Http404
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://www.googleapis.com/auth/spreadsheets']
url = "https://sheets.googleapis.com/v4/spreadsheets/{}/values/{}!A1:Z1000?majorDimension=ROWS"
workbook_key = '1GAWEb_N85lECy6mZG7GclYLSuqFvRvbsmrpzBqVP8qc'
credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
gc = gspread.authorize(credentials)


def index(request):
    if request.method == "POST":
        room_code = request.POST.get("room_code")
        char_choice = request.POST.get("character_choice")
        return redirect(
            '/play/%s?&choice=%s'
            % (room_code, char_choice)
        )
    return render(request, "index.html", {})


def game(request, room_code):
    choice = request.GET.get("choice")
    if choice not in ['X', 'O']:
        raise Http404("Choice does not exists")
    context = {
        "char_choice": choice,
        "room_code": room_code
    }
    return render(request, "game.html", context)


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
    return rows[len(rows) - number_of_added_rows: len(rows)]


def get_number_of_rows(spread_sheet_id, sheet_id):
    sheet = gc.open_by_key(spread_sheet_id)
    sheet_instance = sheet.get_worksheet(sheet_id)
    return len(sheet_instance.get_all_records())
