import tkinter as tk
from tkinter import ttk, filedialog, colorchooser
from PIL import Image, ImageTk, ImageDraw, ImageFont
from diffusers import StableDiffusionPipeline

# モデル読込
pipeline = StableDiffusionPipeline.from_pretrained("stabilityai/stable-diffusion-2-1")
root = tk.Tk()
root.title("壁紙メーカーAI")

generated_image = None  # 生成された画像
edited_image = None     # 編集用画像

# フォントパスの初期設定
AVAILABLE_FONTS = {
    "Arial": "arial.ttf",
    "HGP創英角ポップ体": "HGRPP1.TTC",
    "Times New Roman": "times.ttf",
    "Bauhaus93": "bahnschrift.ttf",
    "Stencil": "STENCIL.TTF"
}

def generate_image():
    global generated_image
    prompt = prompt_entry.get().strip()

    if not prompt:
        error_label.config(text="詳細が未入力です", foreground="red")
        error_label.grid(row=4, column=0, columnspan=2, pady=5)
        return

    generate_button.config(state="disabled")
    status_label.config(text="生成中・・・（この処理には数分かかります）", foreground="blue")
    status_label.grid(row=5, column=0, columnspan=2, pady=5)

    root.update_idletasks()

    try:
        generated_image = pipeline(prompt).images[0]
        display_image(generated_image)
        save_button.grid(row=3, column=0, padx=5, pady=10, sticky="w")
        edit_button.grid(row=3, column=1, padx=5, pady=10, sticky="e")
    except Exception as e:
        error_label.config(text=f"エラーが発生しました: {e}", foreground="red")
        error_label.grid(row=4, column=0, columnspan=2, pady=5)
    finally:
        generate_button.config(state="normal")
        status_label.grid_remove()

def load_custom_image():
    global generated_image
    file_path = filedialog.askopenfilename(filetypes=[("画像ファイル", "*.png;*.jpg;*.jpeg;*.bmp")])
    if file_path:
        try:
            generated_image = Image.open(file_path)
            display_image(generated_image)
            save_button.grid(row=3, column=0, padx=5, pady=10, sticky="w")
            edit_button.grid(row=3, column=1, padx=5, pady=10, sticky="e")
        except Exception as e:
            error_label.config(text=f"画像を読み込めません: {e}", foreground="red")
            error_label.grid(row=4, column=0, columnspan=2, pady=5)

def display_image(image):
    image = image.resize((400, 400), Image.LANCZOS)  # 表示用にリサイズ
    tk_image = ImageTk.PhotoImage(image)
    image_label.config(image=tk_image)
    image_label.image = tk_image

def save_image():
    global generated_image
    if generated_image:
        filename = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Files", "*.png")])
        if filename:
            generated_image.save(filename)
    else:
        error_label.config(text="画像を生成してください。", foreground="red")
        error_label.grid(row=4, column=0, columnspan=2, pady=5)

def open_edit_window():
    global edited_image
    if generated_image is None:
        error_label.config(text="画像を生成または選択してください。", foreground="red")
        error_label.grid(row=4, column=0, columnspan=2, pady=5)
        return

    edited_image = generated_image.copy()
    edit_window = tk.Toplevel(root)
    edit_window.title("壁紙編集")
    font_color = "white"  # 初期フォントカラー
    selected_font = list(AVAILABLE_FONTS.values())[0]  # 初期フォント

    def pick_color():
        nonlocal font_color
        color_code = colorchooser.askcolor(title="フォントカラー選択")[1]
        if color_code:
            font_color = color_code
            color_button.config(bg=color_code)

    def update_preview():
        nonlocal preview_image
        preview = edited_image.copy()
        draw = ImageDraw.Draw(preview)
        text = text_entry.get("1.0", tk.END).strip()
        x = int(x_slider.get())
        y = int(y_slider.get())
        font_size = int(font_size_combobox.get())

        try:
            custom_font = ImageFont.truetype(selected_font, font_size)
        except IOError:
            custom_font = ImageFont.load_default()

        draw.multiline_text((x, y), text, font=custom_font, fill=font_color)
        preview = preview.resize((400, 400), Image.LANCZOS)  # プレビュー用にリサイズ
        preview_image = ImageTk.PhotoImage(preview)
        preview_label.config(image=preview_image)
        preview_label.image = preview_image

    def apply_text():
        draw = ImageDraw.Draw(edited_image)
        text = text_entry.get("1.0", tk.END).strip()
        x = int(x_slider.get())
        y = int(y_slider.get())
        font_size = int(font_size_combobox.get())

        try:
            custom_font = ImageFont.truetype(selected_font, font_size)
        except IOError:
            custom_font = ImageFont.load_default()

        draw.multiline_text((x, y), text, font=custom_font, fill=font_color)
        update_preview()

    def save_edited_image():
        filename = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Files", "*.png")])
        if filename:
            edited_image.save(filename)

    def change_font(event):
        nonlocal selected_font
        selected_font = AVAILABLE_FONTS[font_combobox.get()]
        update_preview()

    # テキスト入力
    ttk.Label(edit_window, text="テキストを入力:").grid(row=0, column=0, padx=5, pady=5)
    text_entry = tk.Text(edit_window, width=30, height=5)
    text_entry.grid(row=0, column=1, padx=5, pady=5)

    # フォントサイズ選択
    ttk.Label(edit_window, text="フォントサイズ:").grid(row=1, column=0, padx=5, pady=5)
    font_size_combobox = ttk.Combobox(edit_window, values=list(range(10, 101, 2)))
    font_size_combobox.set(20)
    font_size_combobox.grid(row=1, column=1, padx=5, pady=5)

    # フォントカラー選択
    ttk.Label(edit_window, text="フォントカラー:").grid(row=2, column=0, padx=5, pady=5)
    color_button = tk.Button(edit_window, text="色を選択", command=pick_color)
    color_button.grid(row=2, column=1, padx=5, pady=5)

    # フォント種類選択
    ttk.Label(edit_window, text="フォント選択:").grid(row=3, column=0, padx=5, pady=5)
    font_combobox = ttk.Combobox(edit_window, values=list(AVAILABLE_FONTS.keys()))
    font_combobox.set("Arial")
    font_combobox.bind("<<ComboboxSelected>>", change_font)
    font_combobox.grid(row=3, column=1, padx=5, pady=5)

    # 位置スライダー
    ttk.Label(edit_window, text="横軸:").grid(row=4, column=0, padx=5, pady=5)
    x_slider = ttk.Scale(edit_window, from_=0, to=generated_image.width, orient="horizontal", command=lambda _: update_preview())
    x_slider.set(generated_image.width // 2)
    x_slider.grid(row=4, column=1, padx=5, pady=5)

    ttk.Label(edit_window, text="縦軸:").grid(row=5, column=0, padx=5, pady=5)
    y_slider = ttk.Scale(edit_window, from_=0, to=generated_image.height, orient="horizontal", command=lambda _: update_preview())
    y_slider.set(generated_image.height // 2)
    y_slider.grid(row=5, column=1, padx=5, pady=5)

    # プレビューラベル
    preview_image = ImageTk.PhotoImage(edited_image.resize((400, 400), Image.LANCZOS))
    preview_label = ttk.Label(edit_window, image=preview_image)
    preview_label.grid(row=6, column=0, columnspan=2, pady=10)

    # 確定ボタン
    ttk.Button(edit_window, text="文章を埋込", command=apply_text).grid(row=7, column=0, padx=5, pady=10)

    # 保存ボタン
    ttk.Button(edit_window, text="壁紙を保存", command=save_edited_image).grid(row=7, column=1, padx=5, pady=10)

# 入力欄
prompt_label = ttk.Label(root, text="生成したい壁紙の詳細を入力:")
prompt_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
prompt_entry = ttk.Entry(root, width=50)
prompt_entry.grid(row=0, column=1, padx=5, pady=5)

# 「参照」ボタン
reference_button = ttk.Button(root, text="ファイルを参照", command=load_custom_image)
reference_button.grid(row=1, column=0, padx=5, pady=10, sticky="w")

# 生成ボタン
generate_button = ttk.Button(root, text="生成開始！", command=generate_image)
generate_button.grid(row=1, column=1, padx=5, pady=10, sticky="e")

# 画像表示ラベル
image_label = ttk.Label(root, text="壁紙を生成するか画像ファイルを参照してください", anchor="center", relief="sunken")
image_label.grid(row=2, column=0, columnspan=2, padx=5, pady=10, sticky="nsew")

# 保存ボタン
save_button = ttk.Button(root, text="壁紙を保存", command=save_image)

# 編集ボタン
edit_button = ttk.Button(root, text="テキスト編集", command=open_edit_window)

# エラー表示ラベル
error_label = ttk.Label(root, text="", foreground="red")
error_label.grid(row=4, column=0, columnspan=2, pady=5)

# ステータス表示ラベル
status_label = ttk.Label(root, text="", foreground="blue")

# ウィンドウ全体の列幅を均等にする
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

root.mainloop()
