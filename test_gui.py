import tkinter as tk
import os
import sys
import locale

# 現在のロケール設定を表示
print("現在のロケール設定:", locale.getlocale())
print("Python version:", sys.version)
print("Tkinter version:", tk.TkVersion)
print("環境変数 DISPLAY:", os.environ.get('DISPLAY', 'なし'))
print("環境変数 LANG:", os.environ.get('LANG', 'なし'))
print("環境変数 LC_ALL:", os.environ.get('LC_ALL', 'なし'))

def create_window():
    # ウィンドウを作成
    root = tk.Tk()
    root.title("日本語テストウィンドウ")
    root.geometry("400x300")
    
    # フォント設定
    japanese_font = ("IPAGothic", 14)
    
    # ラベルを追加
    label1 = tk.Label(root, text="これは日本語のテストです", font=japanese_font)
    label1.pack(padx=20, pady=10)
    
    label2 = tk.Label(root, text="日本語が正しく表示されていますか？", font=japanese_font)
    label2.pack(padx=20, pady=10)
    
    # 英語のラベルも追加
    label3 = tk.Label(root, text="This is an English test", font=("Arial", 14))
    label3.pack(padx=20, pady=10)
    
    # ボタンを追加
    button = tk.Button(root, text="閉じる", font=japanese_font, command=root.destroy)
    button.pack(pady=20)
    
    print("GUIウィンドウを作成しました。表示されていますか？")
    
    # イベントループを開始
    root.mainloop()
    
    print("ウィンドウが閉じられました")

if __name__ == "__main__":
    try:
        create_window()
    except Exception as e:
        print(f"エラーが発生しました: {e}") 