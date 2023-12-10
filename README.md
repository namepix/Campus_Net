# Flight_Ticket_Alarm
## 프로그램 설명


## 항공권 예약 시스템을 위한 전제 조건
이 애플리케이션을 실행하기 위해서는 설치해야될 패키지: selenium

파이썬이 설치되어 있을경우

    pip install selenium 

으로 설치 가능


## 실행 환경
이 애플리케이션은 다음 환경에서 개발되고 테스트되었습니다:

- Python 버전: Python 3.12.0
- 운영 체제: 윈도우10


## 크롬 드라이버
이 애플리케이션은 크롬 드라이버를 필요로 합니다. 

1.크롬 버전 확인

    chrome://version
    
위 링크에 접속하면 맨 윗줄에 버전 표시됨

2. 크롬 드라이버 다운로드
    2-1. 버전 114 이하

        https://chromedriver.chromium.org/downloads
   
    2-2. 버전 115 이상

        https://googlechromelabs.github.io/chrome-for-testing/

3. chromedriver.exe 파일을 filght_ticket_alarm.py 파일이 들어있는 디렉토리에 놓으십시오


## 설정 파일: setting.txt
1. 이메일 보낼 구글계정 입력

account_id = ""
account_pasword = ""

2. 항공권 가격 체크 주기 입력

alarm_period = 1800

(초 단위임. 30으로 설정하면 30초마다 가격 체크, 1800으로 설정하면 30분마다 가격 체크)


## 주의사항!
1.크롬 창이 켜지고 항공권 검색중일때 조작시 오류 발생 가능성 있음





