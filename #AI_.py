#AI绘画工具_
import os, sys, time
import threading
import webbrowser
import configparser as configparser

from PIL import Image, ImageQt

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget,QMessageBox, QFileDialog,QApplication
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QImage, QPixmap, QIcon
from PyQt5.QtCore import QByteArray
# import hashlib
from AI_Drawing_UI_Local import Ui_Ai_Drawing
import torch
from diffusers import StableDiffusionPipeline

my_title = "AI绘画工具"

out_dir = os.path.join(os.path.expanduser("~"), 'Pictures')
out_dir_pic = out_dir
run_flag = 0; Box1_flag = True; Box2_flag = True; Box3_flag = False
filesnums = 1
t0 = time.time()
t1 = time.time()
t2 = time.time()
iii = 0
stop_flag = False
break_flag = False

icanx_path = os.path.join(os.path.expanduser("~"), '.icanx')
if not os.path.exists(icanx_path): os.mkdir(icanx_path)
ini_file = os.path.join(icanx_path,'icanx.ini')
cfg = configparser.ConfigParser()
if not os.path.exists(ini_file):
    file = open(ini_file, 'w')
    file.write("[APPID]\napiKey=\nsecretKey=\nout_path=\n")
    file.close()

    cfg.read(ini_file)
    out_dir = os.path.join(os.path.expanduser("~"), 'Pictures')
    cfg.set('APPID', 'out_path', out_dir)    # 注意键值是用set()方法
    cfg.write(open(ini_file, 'w'))    # 一定要写入才生效

sample = [
    '日照香炉生紫烟,遥看瀑布挂前川,水墨画',
    '亭台楼榭 中国画',
    '杨柳依依 莫奈',
    '牧童遥指杏花村 水墨画',
    '姹紫嫣红 中国画',
    '青山绿水 梵高',
    '雄鹰展翅 中国画',
    '倒影 写意 油画 莫奈',
    '孤舟蓑笠翁 水墨画',
    '万山红遍 中国画',
    '山花烂漫 水彩画',
    '晚来天欲雪,能饮一杯无',
    "星空,未来,科技",
    '山水,松,石,水墨画',
    '日出,海面,4k壁纸,复杂'
]

# def get_md5(src):	#调用云上模型的API使用
#     m = hashlib.md5()
#     m.update(src.encode('UTF-8'))
#     return m.hexdigest()
# def get_stamp():
#     timestamp = int(round(time.time() * 1000))
#     return str(timestamp)

class MainWin(QWidget, Ui_Ai_Drawing):
    def __init__(self):
        super(MainWin, self).__init__()
        self.setupUi(self)
        global run_flag, out_dir
        self.createLayout()
       
        data = QByteArray().fromBase64(ico_data.encode())
        image = QImage()
		#image.loadFromData(data, "my.ico")
        pix = QPixmap.fromImage(image)

        cfg.read(ini_file)
        out_dir = cfg.get('APPID', 'out_path')
        self.txt2.setText(out_dir)
        self.flash_item_str = ""

        self.setWindowIcon(QIcon(pix))
        self.setWindowFlags(Qt.WindowMinimizeButtonHint)
        self.show(); run_flag = 1
        self.total_nums_over = 5
        # def show_error(self,str):
    #     r_button = QMessageBox.question(self, my_title,'\n\n'+str+'\n\n', QMessageBox.Ok)
    def show_error(self, str):
        infoBox = QMessageBox()
        infoBox.setIcon(QMessageBox.Information)
        infoBox.setText(str)
        infoBox.setStandardButtons(QMessageBox.Ok)
        infoBox.button(QMessageBox.Ok).animateClick(10000)  # 10秒自动关闭
        infoBox.exec_()

    def set_False_Btn(self):
        self.outButton.setEnabled(False)
        self.startButton.setEnabled(False);       self.stopButton.setEnabled(True)
        self.quitButton.setEnabled(False)
    def set_True_Btn(self):
        self.outButton.setEnabled(True)
        self.startButton.setEnabled(True);       self.stopButton.setEnabled(False)
        self.quitButton.setEnabled(True)

    def startrun(self):
        global iii, stop_flag, break_flag, t0, t2
        iii = 0
        stop_flag = False
        break_flag = False

        t0 = time.time()
        if not os.path.exists(out_dir): self.show_error('输出目录不存在，请重新选择！'); return

        self.set_False_Btn()
        out_sums = self.spinBox.value()
        prompt = self.lineEdit.text()
        self.set_text_info('【运行信息】 正在初始化AI模型......')

        def run_thread():
            global iii, stop_flag, break_flag, t0 ,t1, t2
            for i in range(out_sums):
                iii += 1
                t1 = time.time()
                if break_flag:
                    self.txt12.setText('【运行信息】 用户终止了正在运行的绘画...')
                    # self.set_True_Btn()
                    break

                torch.backends.cudnn.benchmark = True
                pipe = StableDiffusionPipeline.from_pretrained("IDEA-CCNL/Taiyi-Stable-Diffusion-1B-Chinese-v0.1",
                                                               torch_dtype=torch.float16,
                                                               cache_dir='./model').to('cuda')
                image = pipe(prompt, guidance_scale=7.5).images[0]
                time_str = str(time.strftime('%Y%m%d@%H-%M-%S', time.localtime(time.time())))
                file_name = out_dir + '/' + time_str + '.jpg'
                image.save(file_name)

                # image = Image.open("11.jpg")
                # time.sleep(2)

                t2 = time.time()
                runinfo = '【运行信息】 当前绘画耗时：%.3f秒 | 总绘画耗时：%.1f秒 | 绘画个数：%d' % ((t2 - t1), (t2 - t0), i+1)
                self.set_text_info(runinfo)

                image = ImageQt.toqimage(image)
                piximg = QPixmap.fromImage(image.scaled(QSize(256, 256), Qt.IgnoreAspectRatio))
                if i % 3 == 0: self.my_label1.setPixmap(piximg)
                if i % 3 == 1: self.my_label2.setPixmap(piximg)
                if i % 3 == 2: self.my_label3.setPixmap(piximg)

            stop_flag = True

        t = threading.Thread(target=run_thread)
        t.start()

        self.my_timer = QTimer(self)
        self.my_timer.start(500)
        self.my_timer.timeout.connect(self.set_run_over)

    def set_text_info(self, str):
        self.txt12.setText(str)
        self.flash_item_str = str

    def set_run_over(self):
        global t0, t1, t2, iii
        if stop_flag:
            t2 = time.time()
            self.txt12.setText('【运行信息】 绘画完毕！总消耗时间：%d秒' % (t2 - t0))
            self.set_True_Btn()
            self.my_timer.stop()
        else:
            if self.txt12.text() == '【运行信息】':
                self.txt12.setText(self.flash_item_str)
            else:
                self.txt12.setText('【运行信息】')
                # self.txt12.repaint()

    def stoprun(self):
        global break_flag
        r_button = QMessageBox.question(self, my_title,
                                        "\n\n    确定要停止绘画过程吗？\n\n", QMessageBox.Yes | QMessageBox.No)
        if r_button == QMessageBox.Yes: break_flag = True

    def getapikeyBT(self):
        webbrowser.open("https://fengshenbang-lm.com/document")

    def helpWin(self):
        str="\n\n\n【软件设置】首次使用需要点击右上角按钮，此步骤只需操作一次即可；\n" \
            "【绘画提示】输入您想得到的绘画内容、风格等信息，可参考体验示例；\n" + \
            "【测试示例】可以直接下拉选择绘画提示语，用于初学者参考；\n"+\
            "【输出目录】选择绘画文件保存的目录，默认是本机图片目录；\n【查看输出】点击打开输出目录，便于查看绘画结果；\n\n\n"
        QMessageBox.question(self, my_title+"  【帮助信息】", str, QMessageBox.Ok)
    def quitWin(self):
        r_button = QMessageBox.question(self, my_title,
                                        "\n\n退出将终止绘画进程...... \n\n确认退出吗？\n\n", QMessageBox.Yes | QMessageBox.No)
        if r_button == QMessageBox.Yes:
            cfg.read(ini_file)
            cfg.set('APPID', 'out_path', out_dir)  # 注意键值是用set()方法
            cfg.write(open(ini_file, 'w'))  # 一定要写入才生效
            sys.exit()
    def checkresult(self):
        try: os.startfile(out_dir)
        except: pass

    def outButton_fuc(self):
        global out_dir
        out_dir = QFileDialog.getExistingDirectory(self,'选择绘画的输出文件夹', out_dir)
        if out_dir == '':
            self.txt2.setText(out_dir_pic)
            out_dir = out_dir_pic
        else: self.txt2.setText(out_dir)
    def click_comboBox(self, text):
        self.lineEdit.setText(text)

    def createLayout(self):
        self.my_label1.setAlignment(Qt.AlignCenter)
        self.my_label2.setAlignment(Qt.AlignCenter)
        self.my_label3.setAlignment(Qt.AlignCenter)
        # self.sample_lbl.setPixmap(QPixmap("sample.jpg"))
        # self.my_label1.setFixedSize(427, 240); self.my_label2.setFixedSize(427, 240)
        self.my_label1.setToolTip("本区域，显示的是绘画图片缩略图...")
        self.my_label2.setToolTip("本区域，显示的是绘画图片缩略图...")
        self.my_label3.setToolTip("本区域，显示的是绘画图片缩略图...")
        self.txt12.setText('【运行信息】 可以点击帮助按钮，查看使用说明..')
        self.lineEdit.setText(sample[0])
        self.comboBox.addItems(sample)
        self.comboBox.activated[str].connect(self.click_comboBox)

        self.outButton.setToolTip("选择输出文件目录，绘画后的文件将存在此目录...")

        self.outButton.clicked.connect(self.outButton_fuc)

        self.stopButton.setEnabled(False)
        self.startButton.clicked.connect(self.startrun)
        self.stopButton.clicked.connect(self.stoprun)
        self.helpButton.clicked.connect(self.helpWin)
        self.quitButton.clicked.connect(self.quitWin)
        self.check_result.clicked.connect(self.checkresult)

if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QtWidgets.QApplication(sys.argv)
    MainWin = MainWin()
    sys.exit(app.exec_())

