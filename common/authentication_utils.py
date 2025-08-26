import tweepy
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def authenticate_google_sheets(json_keyfile_name):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile_name, scope) # type: ignore
    gc = gspread.authorize(credentials) # type: ignore
    return gc

def authenticate_x(consumer_key, consumer_secret, access_token, access_token_secret):
    client = tweepy.Client(consumer_key=consumer_key, consumer_secret=consumer_secret, access_token=access_token, access_token_secret=access_token_secret)
    return client