import requests
import gspread
import pandas as pd
from django.shortcuts import render, redirect
from django.http import Http404
from oauth2client.service_account import ServiceAccountCredentials


scope = ['https://www.googleapis.com/auth/spreadsheets']
workbook_key = '1GAWEb_N85lECy6mZG7GclYLSuqFvRvbsmrpzBqVP8qc'
credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
gc = gspread.authorize(credentials)


def index(request):
    if request.method == "POST":
        room_code = request.POST.get("room_code")
        char_choice = request.POST.get("character_choice")
        return redirect(
            '/play/%s?&choice=%s' 
            %(room_code, char_choice)
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

    records_df = pd.DataFrame.from_dict(sheet_instance.get_all_records())
    return records_df.to_json(orient="split")


def get_sheet_data_by_token(spread_sheet_id, sheet_id, access_token):
    url = "https://sheets.googleapis.com/v4/spreadsheets/{}".format(spread_sheet_id)
    header = {
        'Authorization': 'Bearer ' + 'AIzaSyAqEpkH-jhLwyzOZC_8SMdDnNpcEC0cVz0',
        'Content-Type': 'application/json'
    }
    response = requests.get(url, headers=header)
    return response
