import RPi.GPIO as GPIO
import tkinter as tk
import random
import time
from PIL import Image, ImageTk

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

class RockPaperScissorsGame:

    def __init__(self, master):
        # 버튼 및 LED, 부저 핀 설정
        self.led_pins = {'가위': 5, '바위': 6, '보': 13}  # LED 핀
        self.buzzer_pin = 18  # 부저 핀
        self.button_pins = {'가위': 17, '바위': 27, '보': 22} # 버튼 핀

        # LED 핀 출력 설정
        for pin in self.led_pins.values():
            GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW) # LED저항 셋업

        # 버튼 핀 출력 설정
        for pin_2 in self.button_pins.values():
            GPIO.setup(pin_2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # 버튼 풀다운 저항 셋업

        # 버튼 이벤트 설정
        for choice, pin_2 in self.button_pins.items():
            GPIO.add_event_detect(pin_2, GPIO.RISING, callback=lambda channel, ch=choice: self.make_choice(ch), bouncetime=400)

        # 부저 핀 출력 설정 PWM사용
        GPIO.setup(self.buzzer_pin, GPIO.OUT)
        self.buzzer = GPIO.PWM(self.buzzer_pin, 440)

        # 승리/패배/무승부 횟수 초기화 부분
        self.win_count = 0
        self.loss_count = 0
        self.draw_count = 0

        # 제목 설정
        self.master = master
        self.master.title("가위바위보 게임")

        # 게임에 필요한 변수 초기화
        self.choices = ["가위", "바위", "보"]
        self.user_choice = None  # 사용자 선택 초기값
        self.cpu_choice = None  # CPU 선택 초기값

        # 사용자와 CPU 선택 표시 레이블 / GUI
        self.user_label = tk.Label(self.master, text="사용자: 선택 안함", font=("Helvetica", 14), fg="red")
        self.user_label.pack()
        self.cpu_label = tk.Label(self.master, text="CPU: 선택 안함", font=("Helvetica", 14), fg="blue")
        self.cpu_label.pack()

        # Canvas 생성 / GUI
        self.canvas = tk.Canvas(self.master, width=400, height=200)
        self.canvas.pack(pady=20)

        # 이미지 로드 및 Canvas에 추가
        self.scissors_image = self.load_image("scissors.png", (100, 100))
        self.rock_image = self.load_image("rock.png", (100, 100))
        self.paper_image = self.load_image("paper.png", (100, 100))

        self.scissors_item = self.canvas.create_image(100, 100, image=self.scissors_image, tags="가위")
        self.rock_item = self.canvas.create_image(220, 100, image=self.rock_image, tags="바위")
        self.paper_item = self.canvas.create_image(340, 100, image=self.paper_image, tags="보")

        # Canvas 클릭 이벤트 연결 / GUI
        self.canvas.tag_bind("가위", "<Button-1>", lambda event: self.make_choice("가위"))
        self.canvas.tag_bind("바위", "<Button-1>", lambda event: self.make_choice("바위"))
        self.canvas.tag_bind("보", "<Button-1>", lambda event: self.make_choice("보"))

        # 결과 표시 레이블 / GUI
        self.result_label = tk.Label(self.master, text="결과: ", font=("Arial", 14))
        self.result_label.pack(pady=10)

        # 승률 표시 레이블
        self.score_label = tk.Label(self.master, text="승률: 0.0%", font=("Helvetica", 14), fg="green")
        self.score_label.pack()

        # 재시작 및 종료 버튼 프레임 / GUI
        self.control_frame = tk.Frame(self.master)
        self.control_frame.pack(pady=20)

        # 재시작 버튼 / GUI
        self.restart_button = (tk.Button(self.control_frame, text="재시작", font=("Helvetica", 12), command=self.reset_game))
        self.restart_button.grid(row=0, column=0, padx=10)

        # 종료 버튼 / GUI
        self.quit_button = (tk.Button(self.control_frame, text="종료", font=("Helvetica", 12), command=self.quit))
        self.quit_button.grid(row=0, column=1, padx=10)

    def reset_leds(self):  # 모든 LED를 꺼서 초기화
        for pin in self.led_pins.values():
            GPIO.output(pin, GPIO.LOW)

    def play_buzzer(self, sound_sequence):  # 부저 울리기
        for freq in sound_sequence:
            self.buzzer.ChangeFrequency(freq)
            self.buzzer.start(50)  # 듀티 사이클 50%
            time.sleep(0.2)
        self.buzzer.stop()

    def load_image(self, path, size):
        img = Image.open(path)  # 이미지 파일 열기
        img = img.resize(size, Image.ANTIALIAS)  # 크기 조정 (안티앨리어싱 처리)
        return ImageTk.PhotoImage(img)  # PhotoImage 객체 반환
    
    def update_canvas(self, choice):  # Canvas의 원 색상을 업데이트
        # 초기화: 모든 원을 회색으로 설정
        self.canvas.itemconfig(self.scissors_circle, fill="gray")
        self.canvas.itemconfig(self.rock_circle, fill="gray")
        self.canvas.itemconfig(self.paper_circle, fill="gray")

        # 선택한 원의 색상 업데이트
        if choice == "가위":
            self.canvas.itemconfig(self.scissors_circle, fill="red")
        elif choice == "바위":
            self.canvas.itemconfig(self.rock_circle, fill="yellow")
        elif choice == "보":
            self.canvas.itemconfig(self.paper_circle, fill="green")

    def make_choice(self, choice):  # 사용자가 버튼을 클릭하거나 Canvas를 클릭했을 때 동작
        # LED 초기화
        self.reset_leds()

        # 사용자 선택 처리
        self.user_choice = choice
        GPIO.output(self.led_pins[choice], GPIO.HIGH)  # 선택에 맞는 LED 켜기
        self.user_label.config(text=f"사용자: {choice}")
        self.update_canvas(choice)  # Canvas 원 색상 업데이트

        # CPU의 랜덤 선택
        self.cpu_choice = random.choice(['가위', '바위', '보'])
        self.cpu_label.config(text=f"CPU: {self.cpu_choice}")

        # 게임 결과 계산
        result = self.check_result(self.user_choice, self.cpu_choice)
        self.result_label.config(text=f"결과: {result}")

        # 결과에 따라 부저 작동 +  결과에 따라 승/패/무 횟수 업데이트
        if result == "승리하셨습니다.":
            self.play_buzzer([261, 329, 391, 523])  # 이겼을 때 부저 소리
            self.win_count += 1
        elif result == "패배하셨습니다.":
            self.play_buzzer([523, 391, 329, 261])  # 졌을 때 부저 소리
            self.loss_count += 1
        else :
            self.play_buzzer([261, 523]) # 비겼을 때 부저 소리
            self.draw_count += 1

        self.update_score()

    def check_result(self, user, cpu):
        if user == cpu:
            return "비겼습니다."
        elif (user == "가위" and cpu == "보") or \
             (user == "바위" and cpu == "가위") or \
             (user == "보" and cpu == "바위"):
            return "승리하셨습니다."
        else:
            return "패배하셨습니다."

    def update_score(self): # 승률 계산
        total_games = self.win_count + self.loss_count + self.draw_count
        if total_games > 0:
            win_rate = (self.win_count / total_games) * 100
        else:
            win_rate = 0.0
        self.score_label.config(text=f"승률: {win_rate:.1f}%")

    def reset_game(self):  # 게임 초기화
        self.user_choice = None
        self.cpu_choice = None
        self.reset_leds()
        self.user_label.config(text="사용자: 선택 안함")
        self.cpu_label.config(text="CPU: 선택 안함")
        self.result_label.config(text="결과: ")
        self.update_canvas(None)  # Canvas 초기화
        self.win_count = 0
        self.loss_count = 0
        self.draw_count = 0
        self.update_score()

    def quit(self):
        self.reset_leds()
        GPIO.cleanup()
        self.master.quit()


if __name__ == "__main__":
    root = tk.Tk()
    game = RockPaperScissorsGame(root)
    root.mainloop()
