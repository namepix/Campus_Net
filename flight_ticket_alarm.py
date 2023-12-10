import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import JavascriptException
from threading import Lock
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import TimeoutException, NoSuchWindowException
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from smtplib import SMTPException, SMTPAuthenticationError
import os


price_check_lock = Lock()

class Flight:
    def __init__(self, departure_region, departure_detail, destination_region, destination_detail, going_date, return_date, adult, child, infant, seat_type, min_price=-1):
        self.departure_region = departure_region
        self.departure_detail = departure_detail
        self.destination_region = destination_region
        self.destination_detail = destination_detail
        self.going_date = going_date
        self.return_date = return_date
        self.adult = adult
        self.child = child
        self.infant = infant
        self.seat_type = seat_type
        self.min_price = min_price
        
    def __hash__(self):
        return hash((self.departure_region, self.departure_detail, self.destination_region, self.destination_detail, self.going_date, self.return_date, self.adult, self.child, self.infant, self.seat_type))
        
    def __eq__(self, other):
        if isinstance(other, Flight):
            return (
                self.departure_region == other.departure_region
                and self.departure_detail == other.departure_detail
                and self.destination_region == other.destination_region
                and self.destination_detail == other.destination_detail
                and self.going_date == other.going_date
                and self.return_date == other.return_date
                and self.adult == other.adult
                and self.child == other.child
                and self.infant == other.infant
                and self.seat_type == other.seat_type
            )
        return False   

class FlightReservationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("항공권 예약 시스템")

        # 변수 초기화
        self.departure_region_var = tk.StringVar()
        self.departure_detail_var = tk.StringVar()
        self.destination_region_var = tk.StringVar()
        self.destination_detail_var = tk.StringVar()
        self.going_year_var = tk.StringVar()
        self.going_month_var = tk.StringVar()
        self.going_day_var = tk.StringVar()
        self.return_year_var = tk.StringVar()
        self.return_month_var = tk.StringVar()
        self.return_day_var = tk.StringVar()
        self.adult_var = tk.IntVar()
        self.child_var = tk.IntVar()
        self.infant_var = tk.IntVar()
        self.seat_var = tk.StringVar()

        # 저장된 항공권 정보 리스트
        self.flight_list = []
        self.data_flight_list = []
        
        # 알람 활성화 리스트
        self.alarm_list = []
        self.data_alarm_list = []

        # 각 Flight 객체에 대한 타이머를 저장하는 딕셔너리
        self.timer_dict = {} 
        
        # UI 구성 요소 생성
        self.create_widgets()
        
        # 수신 이메일 초기화
        self.registered_email = 0
        
        # 설정 로드
        settings = FlightReservationApp.load_settings()
        self.account_id = settings.get('account_id', '')
        self.account_password = settings.get('account_password', '')
        self.alarm_period = int(settings.get('alarm_period', 1800))        
        # #테스트 출력
        # print(self.account_id, self.account_password, self.alarm_period)
        
    def start_price_check_timer(self, flight):
        try:
            timer = threading.Timer(self.alarm_period, self.flight_price_check, args=(flight,))
        except NoSuchElementException:
            print("target_calendar 요소를 찾을 수 없습니다.")
            self.error_window("target_calendar 요소를 찾을 수 없습니다.")
        except JavascriptException:
            print("JavaScript 실행 중 오류 발생.")
            self.error_window("JavaScript 실행 중 오류 발생.")
        except StaleElementReferenceException:
            print("웹페이지 오류 발생!")
            self.error_window("웹페이지 오류 발생! \n 알람을 껐다 켜주세요")
        except TimeoutException:
            self.error_window("요소를 찾는 데 시간이 너무 오래 걸립니다.")
        except NoSuchWindowException:
            self.error_window("크롬창이 중간에 종료되었습니다!")
        except Exception as e:
            self.error_window("알수없는 오류가 발생했습니다!\n", e)
        timer.start()
        self.timer_dict[flight] = timer
    
    def error_window(self, text_error):
        error_win = tk.Toplevel(self.root)
        error_win.title("오류")
        # 창 크기 및 위치 설정
        window_width = 400
        window_height = 200
        # 화면 크기와 위치 계산
        screen_width = error_win.winfo_screenwidth()
        screen_height = error_win.winfo_screenheight()
        x = int((screen_width / 2) - (window_width / 2))
        y = int((screen_height / 2) - (window_height / 2))
        # 창 크기 및 위치 설정 적용
        error_win.geometry(f'{window_width}x{window_height}+{x}+{y}')
        # 레이블과 패킹
        renewal_label = ttk.Label(error_win, text=text_error, font=("Helvetica", 16, "bold"))
        renewal_label.pack(pady=10)

    def flight_price_check(self, flight):
        # 네이버 항공권 웹 크롤링 및 최저가 체크 로직을 구현해야 합니다.
        # 이 부분은 나중에 추가하셔야 합니다.
        # 현재는 단순히 "가격 체크 중..." 메시지만 출력합니다.
        print(f"가격 체크 중... ({flight.departure_region} -> {flight.destination_region})")
        try:
            current_price = self.current_ticket_price(flight)
            # #테스트용 코드: 2회차에 갱신을 발생시키는 코드
            # current_price = 0
        except NoSuchElementException:
            print("target_calendar 요소를 찾을 수 없습니다.")
            self.error_window("target_calendar 요소를 찾을 수 없습니다.")
        except JavascriptException:
            print("JavaScript 실행 중 오류 발생.")
            self.error_window("JavaScript 실행 중 오류 발생.")
        except StaleElementReferenceException:
            print("웹페이지 오류 발생!")
            self.error_window("웹페이지 오류 발생!")
        except TimeoutException:
            self.error_window("요소를 찾는 데 시간이 너무 오래 걸립니다.")
        except NoSuchWindowException:
            self.error_window("크롬창이 중간에 종료되었습니다!")
        except Exception as e:
            self.error_window("알수없는 오류가 발생했습니다!\n", e)
            
        
        if flight.min_price == -1:
            pass 
        elif flight.min_price != current_price:
            # #테스트용 출력
            # print("가격이 갱신되었습니다!")
            # print(f"현재가격: {current_price}원")
            # print(f"이전가격 : {flight.min_price}원")
            
            # 이메일 주소가 등록되어 있는 경우
            if self.registered_email:
                self.send_email(current_price, flight.min_price)
            else:
                #"가격이 갱신되었습니다!" 프로그램 창 띄우기
                price_renewal = tk.Toplevel(self.root)
                price_renewal.title("알람 상세 정보")
                # 창 크기 및 위치 설정
                window_width = 400
                window_height = 200
                # 화면 크기와 위치 계산
                screen_width = price_renewal.winfo_screenwidth()
                screen_height = price_renewal.winfo_screenheight()
                x = int((screen_width / 2) - (window_width / 2))
                y = int((screen_height / 2) - (window_height / 2))
                # 창 크기 및 위치 설정 적용
                price_renewal.geometry(f'{window_width}x{window_height}+{x}+{y}')
                # 레이블과 패킹
                renewal_label = ttk.Label(price_renewal, text="가격이 갱신되었습니다!", font=("Helvetica", 16, "bold"))
                renewal_label.pack(pady=10)
                current_price_label = ttk.Label(price_renewal, text=f"현재가격: {current_price}원")
                current_price_label.pack()
                previous_price_label = ttk.Label(price_renewal, text=f"이전가격 : {flight.min_price}원")
                previous_price_label.pack()
                current_price_label = ttk.Label(price_renewal, text=f"(이메일 등록이 안되어있어 알림창을 띄움)")
                current_price_label.pack()
            
            #가격 갱신
            flight.min_price = current_price
            pass
        else:
            pass

        # 임시로 30분 간격으로 다시 호출되도록 설정
        if flight in self.alarm_list:
            self.start_price_check_timer(flight)
    
    def current_ticket_price(self, flight):
        with price_check_lock:
            #flight의 정보로 네이버티켓 사이트에서 검색후 최저가 가져오기(나중에 구현 예정)
            #0.변수 설정
            departure_region = flight.departure_region
            departure_detail = flight.departure_detail
            destination_region = flight.destination_region
            destination_detail = flight.destination_detail
            going_date = flight.going_date
            return_date = flight.return_date
            adult = flight.adult
            child = flight.child
            infant = flight.infant
            seat_type = flight.seat_type
            
            # #테스트용 정보 출력
            # print(
            #     departure_region,
            #     departure_detail,
            #     destination_region,
            #     destination_detail,
            #     going_date,
            #     return_date,
            #     adult,
            #     child,
            #     infant,
            #     seat_type
            # )

                # 각 부분에서 숫자만 추출하여 정수로 변환
            parts = going_date.split()
            going_year = int(parts[0].replace("년", ""))
            going_month = int(parts[1].replace("월", ""))
            going_day = int(parts[2].replace("일", ""))

                # 각 부분에서 숫자만 추출하여 정수로 변환
            parts = return_date.split()
            return_year = int(parts[0].replace("년", ""))
            return_month = int(parts[1].replace("월", ""))
            return_day = int(parts[2].replace("일", ""))

            #0.사이트 접속
            browser = webdriver.Chrome()
            browser.maximize_window()
            url = 'https://flight.naver.com/'
            browser.get(url)

            #1.가는 날 버튼
            begin_date = WebDriverWait(browser, 30).until(
                EC.presence_of_element_located((By.XPATH, '//button[text() = "가는 날"]'))
                )
            browser.execute_script("arguments[0].scrollIntoView();", begin_date)
            begin_date = WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//button[text() = "가는 날"]'))
            )
            begin_date.click()


            #1-1.가는날 선택
            # 달력을 찾는 데 필요한 문자열 형식으로 변환
            try:
                date_string = f"{going_year}.{str(going_month).zfill(2)}."

                # 해당하는 달력 찾기
                calendars = browser.find_elements(By.CLASS_NAME, 'month')
                target_calendar = None

                for calendar in calendars:
                    if date_string in calendar.find_element(By.CLASS_NAME, "sc-iqcoie").text:
                        target_calendar = calendar
                        break

                # 해당하는 날짜 버튼 찾아 클릭하기
                if target_calendar:
                    browser.execute_script("arguments[0].scrollIntoView();", target_calendar)
                    day_button = WebDriverWait(target_calendar, 30).until(
                    EC.presence_of_element_located((By.XPATH, f'.//b[text() = "{going_day}"]'))
                    )
                    WebDriverWait(target_calendar, 30).until(
                        EC.element_to_be_clickable((By.XPATH, f'.//b[text() = "{going_day}"]'))
                    )
                    time.sleep(1.5)
                    day_button = target_calendar.find_element(By.XPATH, f'.//b[text() = "{going_day}"]')
                    day_button.click()
                else:
                    print("해당하는 날짜를 찾을 수 없습니다!")
                    self.error_window("해당하는 날짜를 찾을 수 없습니다!\n[현재 날짜]~[1년후] \n범위 내로 입력해주세요")
                    browser.quit()
                    return
            except StaleElementReferenceException:
                # 요소 재탐색
                day_button = WebDriverWait(target_calendar, 10).until(
                    EC.presence_of_element_located((By.XPATH, f'.//b[text() = "{going_day}"]'))
                )
                day_button.click()

            #1-2.오는날 선택
            try:
                return_date_string = f"{return_year}.{str(return_month).zfill(2)}."

                return_calendars = browser.find_elements(By.CLASS_NAME, 'month')
                return_target_calendar = None

                for return_calendar in return_calendars:
                    if return_date_string in return_calendar.find_element(By.CLASS_NAME, "sc-iqcoie").text:
                        return_target_calendar = return_calendar
                        break

                # 해당하는 날짜 버튼 찾아 클릭하기
                if return_target_calendar:
                    browser.execute_script("arguments[0].scrollIntoView();", return_target_calendar)
                    return_day_button = WebDriverWait(return_target_calendar, 30).until(
                    EC.presence_of_element_located((By.XPATH, f'.//b[text() = "{return_day}"]'))
                    )
                    WebDriverWait(return_target_calendar, 30).until(
                        EC.element_to_be_clickable((By.XPATH, f'.//b[text() = "{return_day}"]'))
                    )
                    time.sleep(1.5)
                    return_day_button = return_target_calendar.find_element(By.XPATH, f'.//b[text() = "{return_day}"]')
                    return_day_button.click()
                else:
                    print("해당하는 날짜를 찾을 수 없습니다!")
                    self.error_window("해당하는 날짜를 찾을 수 없습니다!\n[현재 날짜]~[1년후] \n범위 내로 입력해주세요")
                    browser.quit()
                    return
                      
            except StaleElementReferenceException:
                # 요소 재탐색
                return_day_button = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located((By.XPATH, f'.//b[text() = "{return_day}"]'))
                )
                return_day_button.click()        
            
 
                
            #2.출발지 선택
            WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "select_code__d6PLz")))
            departure_button = browser.find_elements(By.CLASS_NAME, "select_code__d6PLz")
            browser.execute_script("arguments[0].scrollIntoView();",departure_button[0])
            WebDriverWait(browser, 30).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "select_code__d6PLz"))
            )
            departure_button[0].click()

            #2-1.출발지 지역 선택
            departure_reg_button = WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.XPATH, f'//button[text() = "{departure_region}"]')))
            browser.execute_script("arguments[0].scrollIntoView();", departure_reg_button)
            departure_reg_button = WebDriverWait(browser, 30).until(
                EC.element_to_be_clickable((By.XPATH, f'//button[text() = "{departure_region}"]'))
            )
            departure_reg_button.click()

            # #2-2.출발지 상세 지역 선택
            WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "autocomplete_Airport__3_dRP")))
            departure_details = browser.find_elements(By.CLASS_NAME, "autocomplete_Airport__3_dRP")

            found = False
            for detail_button in departure_details:
                WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "autocomplete_location__TDL6g")))
                location_text = detail_button.find_element(By.CLASS_NAME, "autocomplete_location__TDL6g").text
                if departure_detail in location_text:
                    browser.execute_script("arguments[0].scrollIntoView();", detail_button)
                    WebDriverWait(browser, 30).until(
                        EC.element_to_be_clickable((By.CLASS_NAME, "autocomplete_location__TDL6g"))
                    )
                    detail_button.click()
                    found = True
                    break
                
            #원하는 지역을 찾지 못한 경우
            if not found:
                self.error_window("지역을 찾지 못했습니다!")
                browser.quit()
                return
                
            # #3.도착지 선택
            WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "select_code__d6PLz")))
            destination_button = browser.find_elements(By.CLASS_NAME, "select_code__d6PLz")
            browser.execute_script("arguments[0].scrollIntoView();",departure_button[1])
            WebDriverWait(browser, 30).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "select_code__d6PLz"))
            )
            destination_button[1].click()


            # #3-1.도착지 지역 선택
            WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.XPATH, f'//button[text() = "{destination_region}"]')))
            destination_reg_button = browser.find_element(By.XPATH, f'//button[text() = "{destination_region}"]')
            browser.execute_script("arguments[0].scrollIntoView();", destination_reg_button)
            WebDriverWait(browser, 30).until(
                EC.element_to_be_clickable((By.XPATH, f'//button[text() = "{destination_region}"]'))
            )
            destination_reg_button = browser.find_element(By.XPATH, f'//button[text() = "{destination_region}"]')
            destination_reg_button.click()

            # # #3-2.도착지 상세 지역 선택
            WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "autocomplete_Airport__3_dRP")))
            destination_details = browser.find_elements(By.CLASS_NAME, "autocomplete_Airport__3_dRP")
            
            found = False
            for detail_button in destination_details:
                WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "autocomplete_location__TDL6g")))
                location_text = detail_button.find_element(By.CLASS_NAME, "autocomplete_location__TDL6g").text
                if destination_detail in location_text:
                    browser.execute_script("arguments[0].scrollIntoView();", detail_button)
                    WebDriverWait(browser, 30).until(
                        EC.element_to_be_clickable((By.CLASS_NAME, "autocomplete_location__TDL6g"))
                    )
                    detail_button.click()
                    found = True
                    break
                
            #원하는 지역을 찾지 못한 경우
            if not found:
                self.error_window("지역을 찾지 못했습니다!")
                browser.quit()
                return

            # #4.인원 선택
            WebDriverWait(browser, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".tabContent_option__2y4c6.select_Passenger__36sFM"))
            )
            passenger_select_button = WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".tabContent_option__2y4c6.select_Passenger__36sFM"))
            )
            browser.execute_script("arguments[0].scrollIntoView();", passenger_select_button)
            passenger_select_button = WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".tabContent_option__2y4c6.select_Passenger__36sFM"))
            )
            passenger_select_button.click()

            # 성인 승객 수 조정
            for _ in range(adult - 1):  # 이미 1명이 기본값이므로 adult - 1 번만큼 증가
                WebDriverWait(browser, 30).until(
                EC.presence_of_element_located((By.XPATH, "(//button[@aria-label='+'])[1]"))
                )
                adult_increase_button = browser.find_element(By.XPATH, "(//button[@aria-label='+'])[1]")
                browser.execute_script("arguments[0].scrollIntoView();", adult_increase_button)
                adult_increase_button = WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, "(//button[@aria-label='+'])[1]"))
                )
                adult_increase_button.click()

            # 소아 승객 수 조정
            for _ in range(child):
                WebDriverWait(browser, 30).until(
                EC.presence_of_element_located((By.XPATH, "(//button[@aria-label='+'])[2]"))
                )
                child_increase_button = browser.find_element(By.XPATH, "(//button[@aria-label='+'])[2]")
                browser.execute_script("arguments[0].scrollIntoView();", child_increase_button)
                child_increase_button = WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, "(//button[@aria-label='+'])[2]"))
                )
                child_increase_button.click()

            # 유아 승객 수 조정
            for _ in range(infant):
                WebDriverWait(browser, 30).until(
                EC.presence_of_element_located((By.XPATH, "(//button[@aria-label='+'])[3]"))
                )
                infant_increase_button = browser.find_element(By.XPATH, "(//button[@aria-label='+'])[3]")
                browser.execute_script("arguments[0].scrollIntoView();", infant_increase_button)
                infant_increase_button = WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, "(//button[@aria-label='+'])[3]"))
                )
                infant_increase_button.click()
                
            # 좌석 타입 선택
            WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".searchBox_option__2CEVQ.searchBox_as_seat__2dnhf")))
            seat_buttons = browser.find_elements(By.CSS_SELECTOR, ".searchBox_option__2CEVQ.searchBox_as_seat__2dnhf")
            for button in seat_buttons:
                if button.text == seat_type:
                    button.click()
                    break
                

                
            # #5.항공권 검색
            search_button = WebDriverWait(browser, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, "searchBox_search__2KFn3"))
                )
            browser.execute_script("arguments[0].scrollIntoView();", search_button)
            search_button = WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "searchBox_search__2KFn3"))
            )
            search_button.click()
            search_button = WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "searchBox_search__2KFn3"))
            )
            search_button.click()

            # #6.최저가 출력
            try:
                # 'concurrent_ConcurrentList' 클래스를 포함하는 첫 번째 요소 찾기
                WebDriverWait(browser, 100).until(
                EC.presence_of_element_located((By.CLASS_NAME, "inlineFilter_name__23asA"))
                )
                WebDriverWait(browser, 60).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[class*="concurrent_ConcurrentList"]'))
                )
                concurrent_list = browser.find_elements(By.CSS_SELECTOR, '[class*="concurrent_ConcurrentList"]')
                # 'concurrent_ConcurrentItemContainer' 클래스를 포함하는 첫 번째 요소 찾기
                concurrent_item_container = concurrent_list[0].find_elements(By.CSS_SELECTOR, '[class*="concurrent_ConcurrentItemContainer"]')

                # 'item_num'을 포함하는 클래스를 가진 첫 번째 요소의 텍스트 가져오기
                item_num_element = concurrent_item_container[0].find_element(By.CSS_SELECTOR, '[class*="item_num"]')
                item_num_text = item_num_element.text
                
            except NoSuchElementException:
                print("원하는 요소를 찾을 수 없습니다.")

            browser.quit()
            #테스트용 정보 출력
            print(f"현재가격 :{item_num_text}")
            return item_num_text
            pass

    def create_widgets(self):
        # 전체 창의 크기를 반으로 나누어 왼쪽 영역과 오른쪽 영역으로 나눔
        self.root.geometry("1050x450")
        left_frame = ttk.Frame(self.root, padding=10)
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        right_frame = ttk.Frame(self.root, padding=10)
        right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # 출발지 정보 입력
        ttk.Label(left_frame, text="출발지 지역").grid(row=0, column=0, padx=5, pady=5)
        ttk.Combobox(left_frame, textvariable=self.departure_region_var,
                    values=["국내", "일본", "동남아", "중국", "유럽", "미주", "대양주", "남미", "아시아", "중동", "아프리카"], justify="right", width=7, state="readonly").grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(left_frame, text="출발도시 or 공항이름").grid(row=0, column=2, padx=5, pady=5)
        ttk.Entry(left_frame, textvariable=self.departure_detail_var, width=12, justify="right").grid(row=0, column=3, padx=5, pady=5)

        # 도착지 정보 입력
        ttk.Label(left_frame, text="도착지 지역").grid(row=2, column=0, padx=5, pady=5)
        ttk.Combobox(left_frame, textvariable=self.destination_region_var,
                    values=["국내", "일본", "동남아", "중국", "유럽", "미주", "대양주", "남미", "아시아", "중동", "아프리카"], justify="right", width=7, state="readonly").grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(left_frame, text="도착도시 or 공항이름").grid(row=2, column=2, padx=5, pady=5)
        ttk.Entry(left_frame, textvariable=self.destination_detail_var, width=12, justify="right").grid(row=2, column=3, padx=5, pady=5)

        # 가는날, 오는날, 성인, 소아, 유아 입력
        ttk.Label(left_frame, text="가는날").grid(row=4, column=0, padx=5, pady=5)
        self.create_date_widgets(left_frame, "going", 4, 1)

        ttk.Label(left_frame, text="오는날").grid(row=5, column=0, padx=5, pady=5)
        self.create_date_widgets(left_frame, "return", 5, 1)

        ttk.Label(left_frame, text="성인").grid(row=6, column=0, padx=5, pady=5)
        ttk.Entry(left_frame, textvariable=self.adult_var, width=4, justify="right").grid(row=6, column=1, padx=5, pady=5)

        ttk.Label(left_frame, text="소아").grid(row=7, column=0, padx=5, pady=5)
        ttk.Entry(left_frame, textvariable=self.child_var, width=4, justify="right").grid(row=7, column=1, padx=5, pady=5)

        ttk.Label(left_frame, text="유아").grid(row=8, column=0, padx=5, pady=5)
        ttk.Entry(left_frame, textvariable=self.infant_var, width=4, justify="right").grid(row=8, column=1, padx=5, pady=5)

        # 좌석 종류 선택
        ttk.Label(left_frame, text="좌석 종류").grid(row=9, column=0, padx=5, pady=5)
        ttk.Combobox(left_frame, textvariable=self.seat_var, values=["일반석", "프리미엄 일반석", "비즈니스석", "일등석"], width=15, justify="right").grid(row=9, column=1, padx=5, pady=5)

        ttk.Button(left_frame, text="항공권 예약", command=self.reserve_flight).grid(row=10, column=0, columnspan=2, pady=10)

        # 오른쪽 영역 - 항공권 리스트
        frame_flight_list = ttk.Frame(right_frame, padding=10)
        frame_flight_list.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        ttk.Label(frame_flight_list, text="항공권 리스트", font=("Helvetica", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=5)

        self.flight_listbox = tk.Listbox(frame_flight_list, height=5, selectmode=tk.SINGLE, width=40)
        self.flight_listbox.grid(row=1, column=0, padx=5, pady=5, columnspan=2)

        ttk.Button(frame_flight_list, text="항공권 상세 정보 보기", command=self.show_flight_detail).grid(row=2, column=0, pady=5)
        ttk.Button(frame_flight_list, text="항공권 삭제", command=self.delete_flight).grid(row=2, column=1, pady=5)
        ttk.Button(frame_flight_list, text="알람 활성화", command=self.activate_alarm).grid(row=2, column=2, pady=5)

        # 오른쪽 영역 - 알람 리스트
        frame_alarm_list = ttk.Frame(right_frame, padding=10)
        frame_alarm_list.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        ttk.Label(frame_alarm_list, text="알람 활성화 리스트", font=("Helvetica", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=5)

        self.alarm_listbox = tk.Listbox(frame_alarm_list, height=5, selectmode=tk.SINGLE, width=40)
        self.alarm_listbox.grid(row=1, column=0, padx=5, pady=5, columnspan=2)

        ttk.Button(frame_alarm_list, text="알람 상세 정보 보기", command=self.show_alarm_detail).grid(row=2, column=0, pady=5)
        ttk.Button(frame_alarm_list, text="알람 비활성화", command=self.deactivate_alarm).grid(row=2, column=1, pady=5)

        # Column weights를 설정하여 창 크기 조절 시 좌우 비율을 유지
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        #이메일 칸
        self.email_var = tk.StringVar()  # 이메일 주소를 저장할 변수
        ttk.Entry(left_frame, textvariable=self.email_var).grid(row=11, column=0, columnspan=3, padx=5, pady=5)  # 이메일 입력 필드
        ttk.Button(left_frame, text="<= 이메일 등록", command=self.register_email).grid(row=11, column=3, padx=5, pady=5)  # 등록 버튼
        self.registered_email_label = ttk.Label(left_frame, text="")  # 등록된 이메일 주소를 표시할 레이블
        self.registered_email_label.grid(row=12, column=0, columnspan=4, padx=5, pady=5)

    def create_date_widgets(self, parent, prefix, row, column):
        ttk.Combobox(parent, textvariable=getattr(self, f"{prefix}_year_var"),
                    values=[f"{i:02d}" for i in range(23, 26)], width=3, justify="right").grid(row=row, column=column, padx=5, pady=6)
        ttk.Label(parent, text="년도").grid(row=row, column=column + 1, padx=5, pady=5)
        ttk.Combobox(parent, textvariable=getattr(self, f"{prefix}_month_var"),
                    values=[f"{i:02d}" for i in range(1, 13)], width=3, justify="right").grid(row=row, column=column + 2, padx=5, pady=5)
        ttk.Label(parent, text="월").grid(row=row, column=column + 3, padx=5, pady=5)
        ttk.Combobox(parent, textvariable=getattr(self, f"{prefix}_day_var"),
                    values=[f"{i:02d}" for i in range(1, 32)], width=3, justify="right").grid(row=row, column=column + 4, padx=5, pady=5)
        ttk.Label(parent, text="일").grid(row=row, column=column + 5, padx=5, pady=5)

    def reserve_flight(self):
        # 항공권 예약 기능 구현
        going_date_str = f"{self.going_year_var.get()}-{self.going_month_var.get()}-{self.going_day_var.get()}"
        return_date_str = f"{self.return_year_var.get()}-{self.return_month_var.get()}-{self.return_day_var.get()}"
        going_date = datetime.strptime(going_date_str, "%y-%m-%d")
        return_date = datetime.strptime(return_date_str, "%y-%m-%d")
        
        # 출발 날짜가 도착 날짜보다 늦은 경우 오류 메시지 표시
        if going_date > return_date:
            self.error_window("날짜 시간순서를 정확히 입력해주세요!")
            return
        
        if self.check_input_valid():
            flight_info = Flight(
            departure_region=self.departure_region_var.get(),
            departure_detail=self.departure_detail_var.get(),
            destination_region=self.destination_region_var.get(),
            destination_detail=self.destination_detail_var.get(),
            going_date=f"{self.going_year_var.get()}년 {self.going_month_var.get()}월 {self.going_day_var.get()}일",
            return_date=f"{self.return_year_var.get()}년 {self.return_month_var.get()}월 {self.return_day_var.get()}일",
            adult=self.adult_var.get(),
            child=self.child_var.get(),
            infant=self.infant_var.get(),
            seat_type=self.seat_var.get()
            )
            # 중복 확인
            if flight_info not in self.flight_list:
                if len(self.flight_list) < 5:
                    self.flight_list.append(flight_info)
                    self.update_flight_listbox()
                else:
                    self.show_message("리스트가 꽉 찼습니다.")
            else:
                self.show_message("이미 리스트에 있는 항공권입니다.")
        else:
            return       
            
    def check_input_valid(self):
        # 입력이 유효한지 확인
        if (
            not self.departure_region_var.get()
            or not self.destination_region_var.get()
            or not self.going_year_var.get()
            or not self.going_month_var.get()
            or not self.going_day_var.get()
            or not self.return_year_var.get()
            or not self.return_month_var.get()
            or not self.return_day_var.get()
            or not self.adult_var.get()
        ):
            self.show_message("입력이 올바르지 않습니다. 모든 항목을 입력해주세요.")
            return False
        return True

    def show_flight_detail(self):
    # 항공권 상세 정보 보기 기능 구현
        selected_index = self.flight_listbox.curselection()
        if selected_index:
            selected_flight = self.flight_list[selected_index[0]]
            detail_window = tk.Toplevel(self.root)
            detail_window.title("항공권 상세 정보")

            # 상세 정보를 라벨로 표시
            ttk.Label(detail_window, text=f"출발지: {selected_flight.departure_region} {selected_flight.departure_detail}").pack(pady=5)
            ttk.Label(detail_window, text=f"도착지: {selected_flight.destination_region} {selected_flight.destination_detail}").pack(pady=5)
            ttk.Label(detail_window, text=f"가는날: {selected_flight.going_date}").pack(pady=5)
            ttk.Label(detail_window, text=f"오는날: {selected_flight.return_date}").pack(pady=5)
            ttk.Label(detail_window, text=f"성인: {selected_flight.adult}명").pack(pady=5)
            ttk.Label(detail_window, text=f"소아: {selected_flight.child}명").pack(pady=5)
            ttk.Label(detail_window, text=f"유아: {selected_flight.infant}명").pack(pady=5)
            ttk.Label(detail_window, text=f"좌석종류: {selected_flight.seat_type}").pack(pady=5)
        else:
            self.show_message("항공권을 선택해주세요.")

    def delete_flight(self):
        # 항공권 삭제 기능 구현
        selected_index = self.flight_listbox.curselection()
        if selected_index:
            self.flight_list.pop(selected_index[0])
            self.update_flight_listbox()
        else:
            self.show_message("삭제할 항공권을 선택해주세요.")

    def activate_alarm(self):
        selected_index = self.flight_listbox.curselection()
        if selected_index:
            selected_flight = self.flight_list[selected_index[0]]
            # 중복 확인
            if selected_flight not in self.alarm_list:
                if len(self.alarm_list) < 5:
                    self.alarm_list.append(selected_flight)
                    self.update_alarm_listbox()
                    
                     # 알람 활성화되면 30분마다 가격 체크 시작
                    print("타이머 시작!")
                    selected_flight.min_price = self.current_ticket_price(selected_flight)
                    #알람 리스트에있는 선택된 Flight객체 원본의 min_price값을 변경할려고함
                    timer = self.start_price_check_timer(selected_flight)
                    self.data_alarm_list.append(timer)  # 타이머 객체를 저장해 둠
                else:
                    self.show_message("알람 활성화 리스트가 이미 다 찼습니다.")
            else:
                self.show_message("이미 리스트에 있는 항공권입니다.")
        else:
            self.show_message("항공권을 선택해주세요.")
        
    def deactivate_alarm(self):
        selected_index = self.alarm_listbox.curselection()
        if selected_index:
            selected_flight = self.alarm_list[selected_index[0]]
            if selected_flight in self.timer_dict:
                self.timer_dict[selected_flight].cancel()
                del self.timer_dict[selected_flight]
            self.alarm_list.pop(selected_index[0])
            self.update_alarm_listbox()
        else:
            self.show_message("알람을 선택해주세요.")

    def show_alarm_detail(self):
    # 알람 상세 정보 보기 기능 구현
        selected_index = self.alarm_listbox.curselection()
        if selected_index:
            selected_alarm = self.alarm_list[selected_index[0]]
            detail_window = tk.Toplevel(self.root)
            detail_window.title("알람 상세 정보")

            # 상세 정보를 라벨로 표시
            ttk.Label(detail_window, text=f"출발지: {selected_alarm.departure_region} {selected_alarm.departure_detail}").pack(pady=5)
            ttk.Label(detail_window, text=f"도착지: {selected_alarm.destination_region} {selected_alarm.destination_detail}").pack(pady=5)
            ttk.Label(detail_window, text=f"가는날: {selected_alarm.going_date}").pack(pady=5)
            ttk.Label(detail_window, text=f"오는날: {selected_alarm.return_date}").pack(pady=5)
            ttk.Label(detail_window, text=f"성인: {selected_alarm.adult}명").pack(pady=5)
            ttk.Label(detail_window, text=f"소아: {selected_alarm.child}명").pack(pady=5)
            ttk.Label(detail_window, text=f"유아: {selected_alarm.infant}명").pack(pady=5)
            ttk.Label(detail_window, text=f"좌석종류: {selected_alarm.seat_type}").pack(pady=5)
        else:
            self.show_message("알람을 선택해주세요.")

    def update_flight_listbox(self):
        # 리스트박스 갱신
        self.flight_listbox.delete(0, tk.END)
        for flight in self.flight_list:
            departure = f"{flight.departure_region} {flight.departure_detail}"
            destination = f"{flight.destination_region} {flight.destination_detail}"
            self.flight_listbox.insert(tk.END, f"{departure} => {destination}")
            
    def update_alarm_listbox(self):
    # 알람 리스트박스 갱신
        self.alarm_listbox.delete(0, tk.END)
        for alarm in self.alarm_list:
            departure = f"{alarm.departure_region} {alarm.departure_detail}"
            destination = f"{alarm.destination_region} {alarm.destination_detail}"
            departure_text = f"{departure} =>" if departure else ""
            self.alarm_listbox.insert(tk.END, f"{departure_text} {destination}")

    def show_message(self, message):
        # 간단한 메시지 박스 표시
        messagebox.showinfo("알림", message)

    def send_email(self,current_price, before_price):
        try:
            username = self.account_id
            password = self.account_password
            
            # 이메일 메시지 설정
            to_email = self.registered_email  # 수신자 이메일 주소
            subject = '항공권 가격 갱신 알림'              # 이메일 제목
            body = f"현재가격: {current_price}\n이전가격: {before_price}"        # 이메일 본문
            
            # MIME 메시지 생성
            msg = MIMEMultipart()
            msg['From'] = username
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            
            # SMTP 서버 접속 및 이메일 발송
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(username, password)
            text = msg.as_string()
            server.sendmail(username, to_email, text)
            server.quit()
            
            print("이메일이 성공적으로 발송되었습니다.")
            return True
        except SMTPAuthenticationError:
            print("이메일 로그인 실패: 인증 정보를 확인해주세요.")
            self.error_window("이메일 로그인 실패: 인증 정보를 확인해주세요.")
        except SMTPException as e:
            print(f"이메일 발송 실패: {e}")
            self.error_window(f"이메일 발송 실패: {e}")
        except Exception as e:
            print(f"알 수 없는 오류가 발생했습니다: {e}")
            self.error_window(f"알 수 없는 오류가 발생했습니다: {e}")
            
        return False
        
    def register_email(self):
        # 등록된 이메일 주소 업데이트
        self.registered_email = self.email_var.get()
        self.registered_email_label.config(text=f"등록된 이메일: {self.registered_email}")

    @staticmethod
    def load_settings(file_path='setting.txt'):
        settings = {}
        with open(file_path, 'r') as file:
            for line in file:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    value = value.strip().strip('"').strip("'")
                    settings[key.strip()] = value.strip()
        return settings

if __name__ == "__main__":
    root = tk.Tk()
    app = FlightReservationApp(root)
    root.mainloop()

    
