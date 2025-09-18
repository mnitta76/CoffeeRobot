import environ
import os
from pathlib import Path

from django.http import JsonResponse
from .x.x_gui import XGui

from common.authentication_utils import authenticate_google_sheets, authenticate_x

BASE_DIR = Path(__file__).resolve().parent.parent   
env = environ.Env()
env.read_env(str(BASE_DIR / '.env'))

"""
Xへのログイン情報を取得する関数
"""
def get_accountlist_from_spreadsheet():
    # スプレッドシートのJSONキーファイル、名前を設定
    json_keyfile_name = env.str('GCP_KEYFILE')
    spreadsheet_name = env.str('MANAGEMENT_SPREADSHEET')

    gc = authenticate_google_sheets(os.path.join(BASE_DIR, json_keyfile_name))
    worksheet = gc.open(spreadsheet_name).sheet1

    # 辞書型のアカウントリストを返却
    return worksheet.get_all_records()

def likeFollws_to_x(request):
    try:
        gc = get_accountlist_from_spreadsheet()
        for index, record in enumerate(gc):
            x_obj = XGui(3, record.get('x_username'), record.get('x_password'))
            result = x_obj.likeFollows()
            return JsonResponse({'status': 'success', 'code': result})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})