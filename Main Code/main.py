import tkinter as tk
from PIL import Image, ImageTk
import random
import sys
import time
import ctypes
import os
import winsound

def resource_path(relative_path):
    """ PyInstaller geçici klasöründeki dosya yolunu bulur """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def gorsele_yesil_ton_ver(image):
    """ Orijinal anahtarı program içinde otomatik olarak yeşile dönüştürür """
    hsv_img = image.convert("HSV")
    h, s, v = hsv_img.split()
    h = h.point(lambda p: 70)
    s = s.point(lambda p: min(255, int(p * 1.5)))
    yesil_hsv = Image.merge("HSV", (h, s, v))
    return yesil_hsv.convert("RGB")

class LimboPrank:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw() 
        
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        
        self.center_x = self.screen_width // 2
        self.center_y = self.screen_height // 2
        
        try:
            self.base_key_img = Image.open(resource_path("key.jpg")).resize((60, 60))
            self.bsod_img = Image.open(resource_path("bsod.jpg")).resize((self.screen_width, self.screen_height))
        except Exception as e:
            sys.exit()

        self.normal_key_img = self.base_key_img
        self.green_key_img = gorsele_yesil_ton_ver(self.base_key_img)

        self.grid_positions = []
        for satir in range(2):
            for sutun in range(4):
                gx = self.center_x - 250 + (sutun * 130)
                gy = self.center_y - 120 + (satir * 130)
                self.grid_positions.append((gx, gy))

        self.pencereler = []
        self.butonlar = [] 
        self.mevcut_x = [0] * 8
        self.mevcut_y = [0] * 8
        
        self.hedef_grid_indexleri = list(range(8))
        self.baslangic_zamani = time.time()
        self.durma_zamani = None
        self.muzik_sustu_mu = False
        self.durum = "BEKLEME" 
        
        self.dogru_anahtar_indexi = random.randint(0, 7)
        
        self.tk_normal_img = ImageTk.PhotoImage(self.normal_key_img)
        self.tk_green_img = ImageTk.PhotoImage(self.green_key_img)
        
        self.pencereleri_olustur()
        self.animasyonu_baslat()
        self.root.mainloop()

    def pencereleri_olustur(self):
        for i in range(8):
            win = tk.Toplevel(self.root)
            win.geometry("100x100")
            win.resizable(False, False)
            win.attributes("-topmost", True)
            win.overrideredirect(True) 
            win.config(bg="white")
            
            gorsel = self.tk_green_img if i == self.dogru_anahtar_indexi else self.tk_normal_img
            
            label = tk.Button(win, image=gorsel, bd=0, cursor="hand2", 
                              bg="white", activebackground="white",
                              command=lambda idx=i: self.anahtar_tiklandi(idx))
            label.pack(expand=True, fill="both")
            
            self.pencereler.append(win)
            self.butonlar.append(label) 
            
            self.mevcut_x[i], self.mevcut_y[i] = self.grid_positions[i]
            win.geometry(f"100x100+{self.mevcut_x[i]}+{self.mevcut_y[i]}")

    def animasyonu_baslat(self):
        gecen_sure = time.time() - self.baslangic_zamani
        

        if gecen_sure < 1.5:
            self.durum = "BEKLEME"
            for i, win in enumerate(self.pencereler):
                hx, hy = self.grid_positions[i]
                win.geometry(f"100x100+{hx}+{hy}")
                

        elif 1.5 <= gecen_sure < 11.1:
            if self.durum == "BEKLEME":
                self.durum = "DONME"
                self.butonlar[self.dogru_anahtar_indexi].config(image=self.tk_normal_img)
                
                try:
                    winsound.PlaySound(resource_path("music.wav"), winsound.SND_FILENAME | winsound.SND_ASYNC)
                except Exception:
                    pass
            
            for i, win in enumerate(self.pencereler):
                hx, hy = self.grid_positions[self.hedef_grid_indexleri[i]]
                dx = hx - self.mevcut_x[i]
                dy = hy - self.mevcut_y[i]
                
                if abs(dx) <= 5 and abs(dy) <= 5:
                    self.hedef_grid_indexleri[i] = random.randint(0, 7)
                else:
                    self.mevcut_x[i] += int(dx * 0.25)
                    self.mevcut_y[i] += int(dy * 0.25)
                
                win.geometry(f"100x100+{self.mevcut_x[i]}+{self.mevcut_y[i]}")
                

        else:
            if self.durum != "DURDU":
                self.durum = "DURDU"
                self.durma_zamani = time.time()
                
                kalan_kutular = list(range(8))
                random.shuffle(kalan_kutular)
                for i in range(8):
                    self.hedef_grid_indexleri[i] = kalan_kutular[i]

            
            if self.durma_zamani and (time.time() - self.durma_zamani >= 7) and not self.muzik_sustu_mu:
                winsound.PlaySound(None, winsound.SND_PURGE)
                self.muzik_sustu_mu = True

            hepsi_yerinde = True
            for i, win in enumerate(self.pencereler):
                hx, hy = self.grid_positions[self.hedef_grid_indexleri[i]]
                dx = hx - self.mevcut_x[i]
                dy = hy - self.mevcut_y[i]
                
                if abs(dx) > 1 or abs(dy) > 1:
                    self.mevcut_x[i] += int(dx * 0.15)
                    self.mevcut_y[i] += int(dy * 0.15)
                    hepsi_yerinde = False
                else:
                    self.mevcut_x[i] = hx
                    self.mevcut_y[i] = hy
                
                win.geometry(f"100x100+{self.mevcut_x[i]}+{self.mevcut_y[i]}")
            
   
            if hepsi_yerinde and self.muzik_sustu_mu:
                return 

        self.root.after(10, self.animasyonu_baslat)

    def anahtar_tiklandi(self, idx):
        if self.durum != "DURDU":
            return
            
        if idx == self.dogru_anahtar_indexi:
            for win in self.pencereler:
                win.destroy()
            winsound.PlaySound(None, winsound.SND_PURGE)
            self.root.quit()
        else:
            self.mavi_ekran_tetikle()

    def mavi_ekran_tetikle(self):
        for win in self.pencereler:
            win.destroy()
            
        ctypes.windll.user32.ShowCursor(0)
            
        bsod_win = tk.Toplevel(self.root)
        bsod_win.geometry(f"{self.screen_width}x{self.screen_height}+0+0")
        bsod_win.attributes("-fullscreen", True)
        bsod_win.attributes("-topmost", True)
        bsod_win.overrideredirect(True)
        
        tk_bsod = ImageTk.PhotoImage(self.bsod_img)
        label = tk.Label(bsod_win, image=tk_bsod)
        label.image = tk_bsod
        label.pack(fill="both", expand=True)
        
        bsod_win.bind("<Escape>", lambda e: self.cikis_yap())

    def cikis_yap(self):
        winsound.PlaySound(None, winsound.SND_PURGE)
        ctypes.windll.user32.ShowCursor(1)
        self.root.quit()

if __name__ == "__main__":
    LimboPrank()
