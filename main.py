import os
import wx
import sys
import time
import pickle
import threading
import inspect

from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class FalconVoucherChecker(wx.App):
    def OnInit(self):
        # create initial frame
        frame = FalconFrame()
        frame.Show()
        return True




class FalconFrame(wx.Frame):
    def __init__(self):
        # init
        style = wx.SYSTEM_MENU | wx.CAPTION | wx.MINIMIZE_BOX | wx.CLOSE_BOX | wx.CLIP_CHILDREN
        super(FalconFrame, self).__init__(parent=None, title="FalconVoucherChecker", style=style, size=(925, 645))

        # set icon
        self.SetIcon(wx.Icon(wx.Bitmap(self.resource_path(r"images\falcon_logo.png"), wx.BITMAP_TYPE_ANY)))

        # create panel
        self.panel = FalconPanel(self)
        self.CenterOnParent()

    @staticmethod
    def resource_path(relative_path):
        """ manage resource path (for .exe and code) """
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)


class FalconPanel(wx.Panel):
    def __init__(self, parent):
        super(FalconPanel, self).__init__(parent=parent)
        self.frame = parent

        # settings
        self.URL = "https://enjinx.io/eth/address/0x8c54085ad729fde488338fc50cfc8dfd5e2b5b89/assets"
        self.checking_interval = 15  # minutes
        self.font = wx.Font(80, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.falcon_color = wx.Colour(18, 246, 213)

        # create sizer
        sizer = wx.GridBagSizer(hgap=0, vgap=0)

        # set up vouchers
        self.vouchers = ["500K", "1M", "2M", "5M", "10M", "50M"]
        self.counts = self.create_empty_dict()
        self.bitmaps = {}
        self.bitmap_controls = {}
        for i, voucher in enumerate(self.vouchers):
            self.bitmaps[voucher] = self.scale_bitmap(wx.Bitmap(self.frame.resource_path(f"images\\{voucher}.png"), wx.BITMAP_TYPE_PNG), 0.7)
            self.bitmap_controls[voucher] = wx.StaticBitmap(parent=self, bitmap=self.bitmaps[voucher])
            sizer.Add(self.bitmap_controls[voucher], pos=(0 if i < 3 else 1, i % 3), flag=wx.ALIGN_CENTER)

        # read old counts and draw them onto bitmaps
        self.read_counts()
        self.draw_counts()

        # continuously get current counts and draw them onto bitmaps
        thread = threading.Thread(target=self.refresh_counts_thread)
        thread.setDaemon(True)
        thread.start()

        # set sizer
        self.SetSizerAndFit(sizer)

    def refresh_counts_thread(self):
        # set up driver
        options = Options()
        options.headless = True
        driver = Firefox(executable_path=self.frame.resource_path("driver\geckodriver.exe"), service_log_path=os.path.devnull, options=options)
        try:
            driver.get(self.URL)
        except Exception as e:
            wx.MessageBox(f"{inspect.stack()[0][3]}():\n{str(e)}", type(e).__name__)
        else:
            WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div/div[3]/div/div/div/div[2]/div/button/span"))).click()
            WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div/div[1]/main/div/div/div/div/div/div/button[3]"))).click()

            while True:
                try:
                    # open URL
                    driver.get(self.URL)
                    assert "EnjinX" in driver.title

                    # get current vouchers
                    new_counts = self.create_empty_dict()
                    erc1155_elements = WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "erc1155-name")))
                    for erc1155 in erc1155_elements:
                        if erc1155.text.startswith("Deposit voucher "):
                            for voucher in self.vouchers:
                                if voucher in erc1155.text:
                                    new_counts[voucher] += 1
                                    break

                    # apply changes
                    for voucher in self.vouchers:
                        if self.counts[voucher] != new_counts[voucher]:
                            print(f"{voucher}: {self.counts[voucher]} -> {new_counts[voucher]}")
                            self.counts[voucher] = new_counts[voucher]
                    wx.CallAfter(self.draw_counts)

                    # write to disk
                    self.write_counts()

                # error handling
                except AssertionError as e:
                    print("Could not reach EnjinX.")
                    wx.MessageBox(f"{inspect.stack()[0][3]}():\n{str(e)}", type(e).__name__)
                except TimeoutException as e:
                    print("Could not find any vouchers.")
                    wx.MessageBox(f"{inspect.stack()[0][3]}():\n{str(e)}", type(e).__name__)

                # sleep for checking_interval minutes
                finally:
                    time.sleep(self.checking_interval * 60)

    def draw_counts(self):
        # for every voucher
        for voucher in self.vouchers:
            # get image and count
            image = self.bitmaps[voucher].GetSubBitmap(wx.Rect(0, 0, *self.bitmaps[voucher].Size))
            count = str(self.counts[voucher])

            # draw text
            dc = wx.MemoryDC(image)
            dc.SetFont(self.font)
            dc.SetTextForeground(self.falcon_color)
            bmp_w, bmp_h = dc.GetSize()
            text_w, text_h = dc.GetTextExtent(count)
            pos_w = (bmp_w - text_w) / 2
            pos_h = (bmp_h - text_h) / 2
            dc.DrawText(count, pos_w, pos_h)
            del dc

            # set new bitmap
            self.bitmap_controls[voucher].SetBitmap(image)

    def read_counts(self):
        filepath = self.frame.resource_path("counts.pkl")
        if os.path.exists(filepath):
            with open(filepath, "rb") as file:
                self.counts = pickle.load(file)

    def write_counts(self):
        filepath = self.frame.resource_path("counts.pkl")
        with open(filepath, "wb") as file:
            pickle.dump(self.counts, file)

    def create_empty_dict(self):
        tmp = {}
        for voucher in self.vouchers:
            tmp[voucher] = 0
        return tmp

    @staticmethod
    def scale_bitmap(bitmap, factor):
        image = bitmap.ConvertToImage()
        image = image.Scale(image.GetWidth()*factor, image.GetHeight()*factor, wx.IMAGE_QUALITY_HIGH)
        return wx.Bitmap(image)


if __name__ == "__main__":
    app = FalconVoucherChecker()
    app.MainLoop()
