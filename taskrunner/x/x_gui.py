import environ
import sys

from pathlib import Path
import pyautogui as pag
from time import sleep
import subprocess
import pyperclip
import urllib.parse
from datetime import datetime

from django.apps import apps



class XGui:
    ## 共通定数
    wait_time = 5 #キーボード入力やマウス操作後の待機秒数
    chrome_path = r'chrome.exe' #Chromeの起動コマンド

    ## ログインに関する変数
    json_file_path = './tool/config/settings.json' #Xのログイン画面へのURL
    x_login_url = 'https://x.com/i/flow/login' #Xのログイン画面へのURL
    x_url = 'https://x.com/' #XのトップページへのURL
    x_username = '' #Xのアカウント名(コンストラクタで設定可能)
    x_password = '' #Xにログインするためのパスワード(コンストラクタで設定可能)
    is_login_check_text = '"screen_name":"  ' #Xにログイン済みかどうかを確認するための文字列(要チューニング)

    ## リポストに関する変数
    x_search_url = 'https://x.com/search?q=' # ポストの検索URL
    x_post_button = './img/x_gui/post-button.png'  # Xのリポストボタンの画像(要チューニング)
    x_post_simple_button = './img/x_gui/post-simple-button.png'  # Xのリポストボタンの画像(要チューニング)
    x_repost_button = './img/x_gui/repost-button.png'  # Xのリポストボタンの画像(要チューニング)
    x_repost_text = './img/x_gui/repost-text.png'  # リポストのテキストの画像(要チューニング)
    x_quote_post_text = './img/x_gui/quote-repost-text.png' # 引用リポストのテキストの画像(要チューニング)
    x_quote_repost_post_button = './img/x_gui/quote-repost-post-button.png' # 引用リポスト時の投稿ボタンの画像(要チューニング)
    x_like_button_focus = './img/x_gui/like-button-focus.png' # 引用リポスト時の投稿ボタンの画像(要チューニング)
    x_input_username = './img/x_gui/input_username.png' # ユーザー名入力テキストボックスの画像(要チューニング)
    scroll_num = 2 # repost関数実行時に何回リポストをするか(要チューニング)

    ## いいねに関する変数
    x_search_Follows_live_url = 'filter%3Afollows&src=recent_search_click&f=live' # フォロワーの最新ポスト検索ワード
    x_Follows_like_num = 1

    ## 関数群
    """
    コンストラクタ
      wait_time: キーボード入力やマウス操作後の待機秒数
      x_username: Xのアカウント名
      x_password: Xにログインするためのパスワード
    """
    def __init__(self, wait_time, x_username, x_password):
        self.wait_time = wait_time
        self.x_username = x_username
        self.x_password = x_password
        self.x_url += self.x_username

    """
    Xへのログイン情報を取得する関数
    """
    def get_posts_from_spreadsheet(self, worksheet):
        # セルA1から行を読み込み、未ツイートのデータをツイートする
        all_records = worksheet.get_all_records()
        tweet=""
        for index, record in enumerate(all_records):
            if record.get('x_datetime'):
                continue

            tweet_count = 0
            for col in ['x_posts']:
                tweet = record.get(col)
                if tweet:
                    tweet_count += 1
        
            if tweet_count > 0:
                # 少なくとも1件のデータがポスト処理に渡された場合、日時を記録
                worksheet.update_cell(index + 2, 3, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                break  # ツイート処理後にループを終了
        return tweet

    """
    Xへログインする関数
    """
    def login_x(self):
        return_code = 0 # 0の場合は正常終了　1の場合は異常終了

        try:
            ## Chromeを起動する
            chrome_path = self.chrome_path
            process = subprocess.Popen(['start', chrome_path], shell=True) # Windowsの場合
            #process = subprocess.Popen([r"google-chrome --simulate-outdated-no-au='Tue, 31 Dec 2099 23:59:59 GMT'"], shell=True) # linuxの場合
            sleep(self.wait_time)
            is_opend_chrome = True

            ## 全画面表示にする
            pag.hotkey('alt', 'space', 'x')
            pag.press('esc')

            ## Xを開く
            pag.hotkey('ctrl', "l")
            sleep(self.wait_time)

            pag.hotkey('ctrl', "a")
            sleep(self.wait_time)

            pyperclip.copy(self.x_url)
            pag.hotkey("ctrl", "v")
            sleep(self.wait_time)

            pag.press("enter")
            sleep(self.wait_time)
            
            ## ページのソースを表示
            pag.hotkey("ctrl", "u")
            sleep(self.wait_time)
            pag.hotkey("ctrl", "a")
            sleep(self.wait_time)
            pag.hotkey("ctrl", "c")
            sleep(self.wait_time)
            html_src_text = pyperclip.paste()
            sleep(self.wait_time)

            ## Xにログイン済みか確認
            if self.is_login_check_text not in html_src_text:
                ## ログイン画面を表示
                pag.hotkey('ctrl', "l")
                sleep(self.wait_time)

                pyperclip.copy(self.x_login_url)
                pag.hotkey("ctrl", "v")
                sleep(self.wait_time)
                pag.press("enter")
                sleep(self.wait_time)

                p= pag.locateOnScreen(self.x_input_username, confidence=0.8)
                if p is not None:
                    # ユーザー名をクリック
                    x, y = pag.center(p)
                    pag.click(x, y)
                    sleep(self.wait_time)
                    # 念のためもう一回クリック
                    x, y = pag.center(p)
                    pag.click(x, y)
                    sleep(self.wait_time)

                    ## アカウント名を入力
                    pyperclip.copy(self.x_username)
                    pag.hotkey("ctrl", "v")
                    sleep(self.wait_time)
                    pag.press("enter")
                    sleep(self.wait_time)

                    ## パスワードを入力
                    pag.hotkey("ctrl", "a")
                    sleep(self.wait_time)
                    pyperclip.copy(self.x_password)
                    pag.hotkey("ctrl", "v")
                    sleep(self.wait_time)
                    pag.press("enter")
                    sleep(self.wait_time)

                    ## プロフィール画面へ移動
                    pag.hotkey('ctrl', "l")
                    sleep(self.wait_time)

                    pag.hotkey('ctrl', "a")
                    sleep(self.wait_time)

                    pyperclip.copy(self.x_url)
                    pag.hotkey("ctrl", "v")
                    sleep(self.wait_time)

                    pag.press("enter")
                    sleep(self.wait_time)
            else:
                pag.hotkey('ctrl', "w")

        except Exception as e:
            print(e)
            return_code = 1
            # Chromeを起動した場合は閉じる
            if is_opend_chrome == True:
                pag.FAILSAFE = False
                pag.moveTo(0,0)
                pag.hotkey('ctrl', 'shift', "w")
        return return_code        

    """
    Xでポストを行う関数
      quote_post: ポスト内容
    """
    def post(self, quote_post):
        return_code = 0 # 0の場合は正常終了　1の場合は異常終了

        try:

            # Xの画面を開く
            return_code = self.login_x()

            if return_code == 0:

                # ポストショートカットボタンをプレス
                pag.press("n")
                sleep(self.wait_time)
                    
                # 文章を入力
                pyperclip.copy(quote_post)
                pag.hotkey("ctrl", "v")
                sleep(self.wait_time)

                # 投稿ボタンをクリック
                pag.hotkey('ctrl', "enter")
                sleep(self.wait_time)

                ## Chromeを閉じる
                pag.hotkey('ctrl', 'shift', "w")

        except Exception as e:
            print(e)
            return_code = 1

        return return_code

    """
    Xでリポストを行う関数
      search_condition: ポストの検索条件　例）#python  OR #駆け出しエンジニア
      mode: 0なら引用リポスト, 1ならリポスト
      quote_post: 引用リポストする場合のポスト内容
    """
    def repost(self, search_condition, mode, quote_post):
        return_code = 0 # 0の場合は正常終了　1の場合は異常終了

        # Xの画面を開く
        return_code = self.login_x()

        if return_code == 0:
            # アドレスバーにフォーカスしポストを検索
            pag.hotkey('ctrl', "l")
            sleep(self.wait_time)

            pag.hotkey('ctrl', "a")
            sleep(self.wait_time)

            access_url = self.x_search_url + urllib.parse.quote(search_condition) + '&src=typed_query&f=live'
            pyperclip.copy(access_url)
            pag.hotkey("ctrl", "v")
            sleep(self.wait_time)

            pag.press("enter")
            sleep(self.wait_time)

            # 任意回だけ画面をスクロールさせ自動リポストをする
            for num in range(0, self.scroll_num):
                # 画面をスクロール
                # Todo 必要ならコメント外す　pag.press('pagedown')
                # Todo 必要ならコメント外す　sleep(self.wait_time)

                # 画面内にリポストの画像を探す
                p= pag.locateOnScreen(self.x_repost_button, confidence=0.8)
                if p is not None:
                    # リポストボタンをクリック
                    x, y = pag.center(p)
                    pag.click(x, y)
                    sleep(self.wait_time)
                    
                    if mode == 0: # 引用ポストの場合
                      # 引用ポストボタンをクリック
                      p= pag.locateOnScreen(self.x_quote_post_text, confidence=0.8)
                      if p is not None:
                        x, y = pag.center(p)
                        pag.click(x, y)
                        sleep(self.wait_time)
                        
                        # 文章を入力
                        pyperclip.copy(quote_post)
                        pag.hotkey("ctrl", "v")
                        sleep(self.wait_time)

                        # 投稿ボタンをクリック
                        p= pag.locateOnScreen(self.x_quote_repost_post_button, confidence=0.8)
                        if p is not None:
                          x, y = pag.center(p)
                          pag.click(x, y)
                          sleep(self.wait_time)

                    else: # リポストの場合
                      # リポストボタンをクリック
                      p= pag.locateOnScreen(self.x_repost_text, confidence=0.8)
                      if p is not None:
                        x, y = pag.center(p)
                        pag.click(x, y)
                        sleep(self.wait_time)

            ## Chromeを閉じる
            pag.hotkey('ctrl', 'shift', "w")

        return return_code
    
    """
    Xでフォロワーのいいねを行う関数
    """
    def likeFollows(self):
        return_code = 0 # 0の場合は正常終了　1の場合は異常終了

        try:

            # Xの画面を開く
            return_code = self.login_x()

            if return_code == 0:

                # アドレスバーにフォーカスしポストを検索
                pag.hotkey('ctrl', "l")
                sleep(self.wait_time)

                pag.hotkey('ctrl', "a")
                sleep(self.wait_time)

                access_url = self.x_search_url + self.x_search_Follows_live_url
                pyperclip.copy(access_url)
                pag.hotkey("ctrl", "v")
                sleep(self.wait_time)

                pag.press("enter")
                sleep(self.wait_time)

                # 任意回だけ画面をスクロールさせ自動リポストをする
                for num in range(0, self.x_Follows_like_num):
                    # ポストフォーカスショートカットボタンをプレス
                    pag.press("j")
                    sleep(self.wait_time)
                    
                    # いいねを実行
                    # pag.press("l")
                    # sleep(self.wait_time)

                    try:
                        p= pag.locateOnScreen(self.x_like_button_focus, confidence=0.8)
                        if p is not None:
                            # いいねボタンをクリック
                            x, y = pag.center(p)
                            pag.click(x, y)
                            sleep(self.wait_time)
                    except Exception as e:
                        print(e)

                ## Chromeを閉じる
                pag.hotkey('ctrl', 'shift', "w")

        except Exception as e:
            print(e)
            return_code = 1

        return return_code
