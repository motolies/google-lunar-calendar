from __future__ import print_function
import datetime
import os.path
import time
from korean_lunar_calendar import KoreanLunarCalendar
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# 구글 캘린더 API 범위 설정
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    creds = None
    # 토큰 파일이 존재하면 로드
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # 유효하지 않거나 없으면 로그인
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # 토큰 저장
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    service = build('calendar', 'v3', credentials=creds)
    return service

def lunar_to_solar(year, month, day, is_leap_month=False):
    try:
        calendar = KoreanLunarCalendar()
        calendar.setLunarDate(year, month, day, is_leap_month)
        solar_iso = calendar.SolarIsoFormat()
        # solar_iso는 'YYYY-MM-DD' 형식의 문자열입니다.
        solar_date = datetime.datetime.strptime(solar_iso, "%Y-%m-%d").date()
        return solar_date
    except ValueError as e:
        print(f"날짜 변환 오류: {e}")
        return None

def create_event(service, calendar_id, summary, description, date, recurrence_id):
    event = {
        'summary': summary,
        'description': description,
        'start': {
            'date': date.strftime('%Y-%m-%d'),
            'timeZone': 'Asia/Seoul',
        },
        'end': {
            'date': date.strftime('%Y-%m-%d'),
            'timeZone': 'Asia/Seoul',
        },
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'popup', 'minutes': 10080},  # 1주일 전
                {'method': 'popup', 'minutes': 1440},  # 1일 전
            ],
        }
    }
    try:
        created_event = service.events().insert(calendarId=calendar_id, body=event).execute()
        print(f"이벤트 생성됨: {created_event.get('htmlLink')}")
        return created_event.get('id')
    except Exception as e:
        print(f"이벤트 생성 오류: {e}")
        return None

def add_lunar_birthdays(service, calendar_id, lunar_month, lunar_day, start_year, count=200):
    current_year = start_year
    for i in range(count):
        if current_year >= datetime.datetime.now().year :
            solar_date = lunar_to_solar(current_year, lunar_month, lunar_day)
            if solar_date:
                summary = "아빠 생신"
                description = f"{i}번 째 생신(음력 {start_year}년 {lunar_month}월 {lunar_day}일)"
                recurrence_id = f"{lunar_month}-{lunar_day}-{current_year}"
                create_event(service, calendar_id, summary, description, solar_date, recurrence_id)
                time.sleep(0.1)
            else:
                print(f"{current_year}년의 음력 날짜 변환에 실패했습니다.")

        current_year += 1  # 다음 해로 이동


def main():
    service = get_calendar_service()
    calendar_id = 'primary'  # 기본 캘린더를 사용, 다른 캘린더 ID를 사용할 수도 있음

    # 음력 생일 정보 입력
    lunar_month = 1
    lunar_day = 1
    start_year = 1960

    add_lunar_birthdays(service, calendar_id, lunar_month, lunar_day, start_year, count=150)

if __name__ == '__main__':
    main()