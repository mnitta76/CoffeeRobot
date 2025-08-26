import os
import shutil
from django.conf import settings

from django.conf import settings

def upload_file_to_local(file_obj, user, save_file_path, filename_prefix="common"):
    """
    ファイルをローカルフォルダに保存する処理
    """
    if not file_obj:
        print(f"[ERROR]ローカルへのアップロード失敗")
        return {
            "status_code": 500,
            "status": "error",
            "message": "Download Error"
        }

    # ローカルの保存先パスを定義
    local_folder = os.path.join(settings.MEDIA_ROOT, f"{filename_prefix}/{user.username}/{save_file_path}")
    os.makedirs(local_folder, exist_ok=True)  # フォルダが存在しない場合は作成

    # 保存先のファイルパスを決定
    local_file_path = os.path.join(local_folder, file_obj.name)

    # ファイルの保存処理
    try:
        with open(local_file_path, 'wb') as destination:
            for chunk in file_obj.chunks():
                destination.write(chunk)
        print(f"ローカルに保存完了: {local_file_path}")
    except Exception as e:
        print(f"[ERROR]ローカルへの保存に失敗しました: {str(e)}")
        return {
            "status_code": 500,
            "status": "error",
            "message": "Download Error"
        }

    return {
        "status_code": 200,
        "status": "success",
        "message": "Uploaded Local",
        "filename": file_obj.name,
        "local_file_path": local_file_path,
    }

def delete_file_from_local(file_name, user, save_file_path, filename_prefix="common"):
    """
    指定されたファイルをローカルフォルダから削除する処理
    """
    # ローカルの保存先パスを定義
    local_folder = os.path.join(settings.MEDIA_ROOT, f"{filename_prefix}/{user.username}/{save_file_path}")
    local_file_path = os.path.join(local_folder, file_name)

    # ファイルの存在確認
    if os.path.exists(local_file_path):
        try:
            os.remove(local_file_path)
            return {
                "status_code": 200,
                "status": "success",
                "message": "Deleted from Local",
                "file_name": file_name,
                "local_file_path": local_file_path,
            }
        except Exception as e:
            return {
                "status_code": 500,
                "status": "error",
                "message": f"Failed to delete: {str(e)}"
            }
    else:
        return {
            "status_code": 404,
            "status": "error",
            "message": "File not found"
        }



def delete_folder_from_local(user, save_file_path, filename_prefix="common"):
    """
    指定されたフォルダをローカルから削除する処理
    """
    # ローカルの保存先パスを定義
    local_folder = os.path.join(settings.MEDIA_ROOT, f"{filename_prefix}/{user.username}/{save_file_path}")

    # フォルダが存在するか確認
    if not os.path.exists(local_folder):
        return {
            "status_code": 404,
            "status": "not_found",
            "message": "Folder not found"
        }

    # フォルダの削除処理
    try:
        shutil.rmtree(local_folder)
        print(f"[INFO] ローカルフォルダを削除しました: {local_folder}")
    except Exception as e:
        print(f"[ERROR] ローカルフォルダの削除に失敗しました: {str(e)}")
        return {
            "status_code": 500,
            "status": "error",
            "message": "Folder Delete Error"
        }

    return {
        "status_code": 200,
        "status": "success",
        "message": "Folder Deleted",
        "local_folder_path": local_folder,
    }
