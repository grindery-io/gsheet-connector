
def serialize_spreadsheet(spreadsheet):
    return {
        "value": spreadsheet['id'],
        "label":  spreadsheet['name'],
        "sample":  spreadsheet['id']
    }


def serialize_worksheet(worksheet):
    return {
        "value": worksheet['properties']['title'],
        "label":  worksheet['properties']['title'],
        "sample":  worksheet['properties']['sheetId'],
    }
