import math
from tkinter import *
from tkinter.colorchooser import askcolor
from tkinter.simpledialog import askinteger
from tkinter import Tk, Menu, PhotoImage, Canvas, Entry, Button, BOTH
from PIL import Image, ImageTk, ImageDraw
from tkinter import filedialog, Menu
from PIL import ImageGrab
import io

# 전역 변수 초기화
x1, y1, x2, y2 = None, None, None, None
penColor = "black"
fillColor = ""
penWidth = 1
shapeMode = "line"  # 기본 도형 모드
lineStyle = "solid"  # 기본 선 스타일
drawn_items = []
erased_items = []
bg_image = None
canvas_image = None


# 마우스 클릭 이벤트
def mouseClick(event):
    global x1, y1
    x1 = event.x
    y1 = event.y


# 마우스 드래그 이벤트
def mouseDrag(event):
    global x1, y1
    if shapeMode == "free":  # 자유형 드로잉
        line = canvas.create_line(x1, y1, event.x, event.y, width=penWidth, fill=penColor)
        drawn_items.append(line)  # 그린 선을 drawn_items에 추가
        x1, y1 = event.x, event.y


# 마우스 릴리즈 이벤트
def mouseDrop(event):
    global x1, y1, x2, y2
    x2 = event.x
    y2 = event.y
    if shapeMode == "line":
        drawLine(x1, y1, x2, y2)
    elif shapeMode == "rectangle":
        rect = canvas.create_rectangle(x1, y1, x2, y2, width=penWidth, outline=penColor, fill=fillColor)
        drawn_items.append(rect)  # 그린 사각형을 drawn_items에 추가
    elif shapeMode == "oval":
        oval = canvas.create_oval(x1, y1, x2, y2, width=penWidth, outline=penColor, fill=fillColor)
        drawn_items.append(oval)  # 그린 타원을 drawn_items에 추가
    elif shapeMode == "triangle":
        triangle = canvas.create_polygon(x1, y1, x2, y2, (x1 + x2) // 2, y1 - abs(y2 - y1),
                                         width=penWidth, outline=penColor, fill=fillColor)
        drawn_items.append(triangle)  # 그린 삼각형을 drawn_items에 추가
    elif shapeMode == "star":
        drawStar(x1, y1, x2, y2)


# 선 그리기 함수
def drawLine(x1, y1, x2, y2):
    if lineStyle == "solid":
        line = canvas.create_line(x1, y1, x2, y2, width=penWidth, fill=penColor)
        drawn_items.append(line)  # 그린 선을 drawn_items에 추가
    elif lineStyle == "dashed":
        drawDashedLine(x1, y1, x2, y2)


# 대시 선 그리기 함수
def drawDashedLine(x1, y1, x2, y2):
    dash_length = 5
    gap_length = 3
    total_length = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
    num_dashes = int(total_length / (dash_length + gap_length))

    for i in range(num_dashes):
        start_x = x1 + (x2 - x1) * (i * (dash_length + gap_length) / total_length)
        start_y = y1 + (y2 - y1) * (i * (dash_length + gap_length) / total_length)
        end_x = start_x + (x2 - x1) * (dash_length / total_length)
        end_y = start_y + (y2 - y1) * (dash_length / total_length)
        line = canvas.create_line(start_x, start_y, end_x, end_y, width=penWidth, fill=penColor)
        drawn_items.append(line)  # 그린 대시 선을 drawn_items에 추가


def erase(event):
    # 마우스 위치에서 지우개 크기만큼의 사각형을 정의
    x, y = event.x, event.y
    # 지우개 크기 설정
    erase_size = penWidth * 2  # 지우개 크기 조정
    # 지우개로 지울 영역을 정의
    overlapping_items = canvas.find_overlapping(x - erase_size, y - erase_size, x + erase_size, y + erase_size)

    # 겹치는 아이템을 지우기
    for item in overlapping_items:
        canvas.delete(item)
        erased_items.append(item)  # 지운 아이템을 erased_items에 추가


# 별 그리기 함수
def drawStar(x1, y1, x2, y2):
    radius = int(((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5)  # 드래그로 반지름 계산
    coords = []
    for i in range(10):
        angle = i * math.pi / 5
        r = radius if i % 2 == 0 else radius / 2
        coords.append((x1 + r * math.cos(angle), y1 - r * math.sin(angle)))
    star = canvas.create_polygon(coords, width=penWidth, outline=penColor, fill=fillColor)
    drawn_items.append(star)  # 그린 별을 drawn_items에 추가


def drawStarWithSize():
    size = askinteger("별 크기", "별의 크기를 입력하세요:", minvalue=1)
    if size is not None:
        drawStar(x1, y1, x1 + size, y1 + size)


def getColor():
    global penColor
    color = askcolor()
    penColor = color[1] if color[1] else penColor


def getFillColor():
    global fillColor
    color = askcolor()
    fillColor = color[1] if color[1] else ''


def getWidth():
    global penWidth
    penWidth = askinteger("선 두께", "선 두께(1-10)를 입력하세요", minvalue=1, maxvalue=10)


def setShape(new_shape):
    global shapeMode
    shapeMode = new_shape


def setLineStyle(style):
    global lineStyle
    lineStyle = style


def undo():
    if drawn_items:
        last_item = drawn_items.pop()
        canvas.delete(last_item)
    elif erased_items:
        last_erased = erased_items.pop()
        canvas.delete(last_erased)


def clearCanvas():
    canvas.delete("all")


def change_bg_color():
    global bg_image
    color = askcolor()[1]
    if color:
        canvas.config(bg=color)
        bg_image = None  # 배경 이미지를 제거


def change_bg_image():
    global bg_image
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")])
    if file_path:
        image = Image.open(file_path)
        # 캔버스 크기를 가져오기 전에 캔버스가 생성되었는지 확인
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()

        # 캔버스 크기에 맞게 이미지 크기 조정
        image = image.resize((canvas_width, canvas_height), Image.LANCZOS)
        bg_image = ImageTk.PhotoImage(image)

        # 이미지를 캔버스에 추가
        canvas.create_image(0, 0, anchor=NW, image=bg_image)
        canvas.lower(bg_image)  # 배경 이미지가 다른 항목 뒤에 있도록 설정
        canvas.update()  # 캔버스 업데이트





def save_canvas_image():
    # 캔버스 위젯의 절대 위치 가져오기
    x = window.winfo_rootx() + canvas.winfo_x()
    y = window.winfo_rooty() + canvas.winfo_y()
    x1 = x + canvas.winfo_width()
    y1 = y + canvas.winfo_height()

    # 화면을 캡처하여 이미지를 저장
    img = ImageGrab.grab(bbox=(x, y, x1, y1))

    # 파일 저장 대화상자
    save_path = filedialog.asksaveasfilename(defaultextension=".png",
                                             filetypes=[("PNG files", "*.png"),
                                                        ("JPEG files", "*.jpg"),
                                                        ("All files", "*.*")])
    if save_path:
        img.save(save_path)
        print(f"이미지가 {save_path}에 저장되었습니다!")


# 메인 실행
if __name__ == "__main__":
    window = Tk()
    window.title('통합 그림판')
    window.configure(cursor='pencil')

    canvas = Canvas(window, height=600, width=800, bg="white")
    canvas.bind("<Button-1>", mouseClick)
    canvas.bind("<ButtonRelease-1>", mouseDrop)
    canvas.bind("<B1-Motion>", mouseDrag)
    canvas.pack(fill=BOTH, expand=True)

    mainMenu = Menu(window)
    window.config(menu=mainMenu)

    save_button = Button(window, text="이미지 저장", command=save_canvas_image)
    save_button.pack()

    ridMenu = Menu(mainMenu)
    mainMenu.add_cascade(label="지우기", menu=ridMenu)
    ridMenu.add_command(label="모두 지우기", command=clearCanvas)
    ridMenu.add_command(label="되돌리기", command=undo)

    lineMenu = Menu(mainMenu)
    mainMenu.add_cascade(label="선", menu=lineMenu)
    lineMenu.add_command(label="직선", command=lambda: setShape('line'))
    lineMenu.add_command(label="실선(-)", command=lambda: setLineStyle("solid"))
    lineMenu.add_command(label="점선(---)", command=lambda: setLineStyle("dashed"))

    shapeMenu = Menu(mainMenu)
    mainMenu.add_cascade(label="도형", menu=shapeMenu)
    shapeMenu.add_command(label="사각형", command=lambda: setShape('rectangle'))
    shapeMenu.add_command(label="원", command=lambda: setShape('oval'))
    shapeMenu.add_command(label="삼각형", command=lambda: setShape('triangle'))
    shapeMenu.add_command(label="자유형", command=lambda: setShape('free'))
    shapeMenu.add_command(label="별", command=drawStarWithSize)

    designMenu = Menu(mainMenu)
    mainMenu.add_cascade(label="디자인(선, 도형)", menu=designMenu)
    designMenu.add_command(label="선 색상 선택", command=getColor)
    designMenu.add_command(label="채우기 색상 선택", command=getFillColor)
    designMenu.add_command(label="선 두께 설정", command=getWidth)

    bgMenu = Menu(mainMenu)
    mainMenu.add_cascade(label="배경", menu=bgMenu)
    bgMenu.add_command(label="배경 색상 변경", command=change_bg_color)
    bgMenu.add_command(label="배경 이미지 변경", command=change_bg_image)

    # 메뉴 항목의 배경색과 글자색 설정
    for menu in [mainMenu, ridMenu, lineMenu, shapeMenu, designMenu, bgMenu]:
        menu.config(activebackground='skyblue', activeforeground='black')

    window.mainloop()
