import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import sys

# 导入 PaddleOCR 库
try:
    # 尝试导入并初始化 PaddleOCR
    from paddleocr import PaddleOCR
    # 简化初始化，确保快速启动
    ocr = PaddleOCR(
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False)
    OCR_ENGINE_READY = True
except ImportError:
    messagebox.showerror("错误", "未找到 PaddleOCR 库。请运行 'pip install paddleocr' 安装。")
    OCR_ENGINE_READY = False
except Exception as e:
    messagebox.showerror("错误", f"PaddleOCR 初始化失败，请检查安装和依赖。\n错误信息: {e}")
    OCR_ENGINE_READY = False

# --- GUI 应用程序类 ---
class ModernOCRApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- 配置窗口 ---
        self.title("✨ 离线图像识别工具 (雨季 PaddleOCR)")
        self.min_width = 1000
        self.min_height = 700
        self._center_window(self.min_width, self.min_height)
        
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.current_image_path = None
        self.current_result_text = ""

        # 配置主网格布局（2行，2列）
        self.grid_rowconfigure(0, weight=0)   # 标题行不随窗口缩放
        self.grid_rowconfigure(1, weight=1)   # 内容行随窗口缩放
        self.grid_columnconfigure(0, weight=1) 
        self.grid_columnconfigure(1, weight=1) 

        # --- 0. 顶部标题栏 ---
        self.title_frame = ctk.CTkFrame(self, height=60, fg_color=("gray90", "gray15"))
        self.title_frame.grid(row=0, column=0, columnspan=2, padx=0, pady=0, sticky="ew")
        self.title_frame.grid_columnconfigure(0, weight=1)
        
        self.main_title_label = ctk.CTkLabel(
            self.title_frame,
            text="🌟 离线OCR图像识别工具 🌟",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=("gray10", "gray90")
        )
        self.main_title_label.grid(row=0, column=0, padx=20, pady=10)

        # --- 1. 左侧：图片预览 ---
        self.left_frame = ctk.CTkFrame(self)
        self.left_frame.grid(row=1, column=0, padx=15, pady=15, sticky="nsew")
        self.left_frame.grid_rowconfigure(0, weight=1)
        self.left_frame.grid_columnconfigure(0, weight=1)
        
        # 1.1 图片显示区域
        self.image_label = ctk.CTkLabel(
            self.left_frame, 
            text="[请点击按钮选择图片]", 
            fg_color=("gray80", "gray25"), 
            text_color=("gray20", "gray80")
        )
        self.image_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="nsew")
        self.displayed_image = None
        
        # 1.2 操作按钮
        self.action_button_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        self.action_button_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
        self.action_button_frame.grid_columnconfigure((0, 1), weight=1)

        self.select_button = ctk.CTkButton(
            self.action_button_frame, 
            text="📁 选择图片", 
            command=self.select_image,
            height=40
        )
        self.select_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        self.ocr_button = ctk.CTkButton(
            self.action_button_frame, 
            text="🚀 开始识别 (OCR)", 
            command=self.run_ocr, 
            state="disabled" if not OCR_ENGINE_READY else "normal",
            fg_color="#00A86B", # 稍微亮一点的绿色
            hover_color="#008053", 
            height=40
        )
        self.ocr_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # --- 2. 右侧：识别结果 ---
        self.right_frame = ctk.CTkFrame(self)
        self.right_frame.grid(row=1, column=1, padx=15, pady=15, sticky="nsew")
        self.right_frame.grid_rowconfigure(1, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)

        # 2.1 结果区域标题
        self.result_title = ctk.CTkLabel(
            self.right_frame, 
            text="📄 纯文本识别结果", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.result_title.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")

        # 2.2 结果显示文本框
        self.result_textbox = ctk.CTkTextbox(self.right_frame, wrap="word", width=400)
        self.result_textbox.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self.result_textbox.insert("0.0", "欢迎使用！请先选择图片并点击“开始识别”按钮。")
        self.result_textbox.configure(state="disabled")

        # 2.3 复制按钮
        self.copy_button = ctk.CTkButton(
            self.right_frame, 
            text="📋 复制结果", 
            command=self.copy_result, 
            state="disabled",
            height=40
        )
        self.copy_button.grid(row=2, column=0, padx=10, pady=(5, 10), sticky="ew")

    # --- 核心方法 ---
    
    def _center_window(self, width, height):
        """将窗口居中显示"""
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width / 2) - (width / 2)
        y = (screen_height / 2) - (height / 2)
        self.geometry(f"{width}x{height}+{int(x)}+{int(y)}")

    def select_image(self):
        """选择图片文件，并进行预览设置。"""
        fpath = filedialog.askopenfilename(
            title="选择要识别的图片文件",
            filetypes=[("图片文件", "*.png *.jpg *.jpeg *.bmp"), ("所有文件", "*.*")]
        )
        if fpath:
            self.current_image_path = fpath
            self.display_image(fpath)
            self.ocr_button.configure(state="normal")
            
            # 清空旧结果
            self.result_textbox.configure(state="normal")
            self.result_textbox.delete("0.0", "end")
            self.result_textbox.insert("0.0", f"已选择文件：{os.path.basename(fpath)}\n\n请点击“开始识别”按钮。")
            self.result_textbox.configure(state="disabled")
            self.copy_button.configure(state="disabled")
            self.current_result_text = ""
            self.result_title.configure(text="📄 纯文本识别结果")


    def display_image(self, path):
        """加载图片，缩放适应并显示在左侧 Label 中。"""
        try:
            pil_image = Image.open(path)
            
            # 获取 Label 尺寸以进行缩放
            self.update_idletasks() 
            label_width = self.image_label.winfo_width()
            label_height = self.image_label.winfo_height()

            max_width = max(label_width - 20, 400)
            max_height = max(label_height - 20, 500)
            
            # 保持比例缩放
            original_width, original_height = pil_image.size
            ratio = min(max_width / original_width, max_height / original_height)
            
            new_width = int(original_width * ratio)
            new_height = int(original_height * ratio)

            resized_image = pil_image.resize((new_width, new_height))
            
            self.displayed_image = ImageTk.PhotoImage(resized_image)
            self.image_label.configure(image=self.displayed_image, text="")
            self.image_label.image = self.displayed_image # 保持引用

        except Exception as e:
            messagebox.showerror("图片错误", f"无法加载图片: {e}")
            self.image_label.configure(text="[图片加载失败]", image=None)
            self.displayed_image = None
            self.ocr_button.configure(state="disabled")
            self.current_image_path = None
            
    def run_ocr(self):
        """运行 PaddleOCR 识别并显示纯文本结果。"""
        if not self.current_image_path or not OCR_ENGINE_READY:
            messagebox.showwarning("提示", "请先选择图片或检查 OCR 引擎是否准备就绪。")
            return
        
        self.ocr_button.configure(state="disabled", text="识别中...")
        self.copy_button.configure(state="disabled")
        self.result_textbox.configure(state="normal")
        self.result_textbox.delete("0.0", "end")
        self.result_textbox.insert("0.0", "正在进行 OCR 识别，请稍候...")
        self.update_idletasks() 

        try:
            # 调用您的 OCR 代码
            ocr_results = ocr.predict(input=self.current_image_path)
            
            output_text = []
            
            for res in ocr_results:
                if hasattr(res, 'json') and 'res' in res.json:
                    data = res.json['res']
                    rec_texts = data.get('rec_texts', [])
                    
                    # 只提取文本，忽略置信度
                    for text in rec_texts:
                        output_text.append(text)

            self.current_result_text = "\n".join(output_text)
            
            if not self.current_result_text:
                 self.current_result_text = "未识别到任何文本。"
                 self.result_title.configure(text="❌ 未识别到文本")
            else:
                 self.result_title.configure(text="✅ 识别完成 (纯文本)")

            # 显示结果
            self.result_textbox.delete("0.0", "end")
            self.result_textbox.insert("0.0", self.current_result_text)
            self.copy_button.configure(state="normal")
            
        except Exception as e:
            error_message = f"OCR 识别失败！错误信息：\n{e}"
            self.result_textbox.delete("0.0", "end")
            self.result_textbox.insert("0.0", error_message)
            self.result_title.configure(text="🚨 识别错误")
            messagebox.showerror("识别错误", error_message)
        finally:
            self.ocr_button.configure(state="normal", text="🚀 开始识别 (OCR)")
            self.result_textbox.configure(state="disabled")

    def copy_result(self):
        """将识别结果复制到剪贴板。"""
        if self.current_result_text:
            self.clipboard_clear()
            self.clipboard_append(self.current_result_text)
            messagebox.showinfo("复制成功", "识别结果已复制到剪贴板。")
        else:
            messagebox.showwarning("提示", "当前没有可复制的识别结果。")

# --- 运行程序 ---
if __name__ == "__main__":
    app = ModernOCRApp()
    app.mainloop()