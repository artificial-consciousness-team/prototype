import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import os
import sys
import time
import locale

print("現在のロケール設定:", locale.getlocale())
print("Python version:", sys.version)
print("Tkinter version:", tk.TkVersion)
print("環境変数 DISPLAY:", os.environ.get('DISPLAY', 'なし'))
print("環境変数 LANG:", os.environ.get('LANG', 'なし'))

# PyAutoGUIのインポートを条件付きにする
try:
    import pyautogui
    # フェイルセーフを無効化して、どのような環境でも動作するようにする
    pyautogui.FAILSAFE = False
    # PyAutoGUIがスクリーンショットを取る方法を指定
    pyautogui.screenshot = pyautogui.screenshot
    PYAUTOGUI_AVAILABLE = True
    print("PyAutoGUI読み込み成功")
    
    # テスト用のスクリーンショットを試みる
    try:
        test_img = pyautogui.screenshot()
        print(f"テストスクリーンショット撮影成功: サイズ {test_img.size}")
    except Exception as e:
        print(f"テストスクリーンショット撮影失敗: {e}")
        
except Exception as e:
    print(f"PyAutoGUIのインポートに失敗しました: {e}")
    print("スクリーンショット機能は無効になります")
    PYAUTOGUI_AVAILABLE = False

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # 日本語フォントの設定
        self.japanese_font = ("IPAGothic", 10)
        self.japanese_font_bold = ("IPAGothic", 12, "bold")
        
        # アプリケーションの設定
        self.title("チーム開発サンプルアプリ")
        self.geometry("800x600")
        print("GUIウィンドウを初期化しました")
        
        # データベース接続情報
        self.db_config = {
            'host': os.environ.get('MYSQL_HOST', 'localhost'),
            'user': os.environ.get('MYSQL_USER', 'user'),
            'password': os.environ.get('MYSQL_PASSWORD', 'password'),
            'database': os.environ.get('MYSQL_DB', 'app_db')
        }
        
        # UI要素の初期化
        self.create_widgets()
        
        # データベース接続ステータス
        self.status_var = tk.StringVar(value="データベース: 接続待機中...")
        ttk.Label(self, textvariable=self.status_var, font=self.japanese_font).pack(anchor=tk.W, padx=10, pady=5)
        
        # データベース接続を別スレッドで試みる
        self.after(1000, self.try_connect_to_db)
        
        print("アプリケーションの初期化が完了しました")
    
    def try_connect_to_db(self):
        # MySQLが起動するまで待機するための簡易リトライロジック
        print("データベースへの接続を試みています...")
        
        try:
            # データベースに接続
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            
            # 単純なクエリでテスト
            cursor.execute("SELECT 1")
            cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            print("データベースへの接続に成功しました")
            self.status_var.set("データベース: 接続成功")
            
            # データを読み込む
            self.load_data()
            
        except Exception as e:
            print(f"データベース接続エラー: {e}")
            self.status_var.set(f"データベースエラー: {e}")
            # 3秒後に再試行
            self.after(3000, self.try_connect_to_db)

    def create_widgets(self):
        # タブコントロールの作成
        self.tab_control = ttk.Notebook(self)
        
        # ユーザータブ
        self.user_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.user_tab, text="ユーザー管理")
        
        # スクリーンショットタブ
        self.screenshot_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.screenshot_tab, text="スクリーンショット")
        
        self.tab_control.pack(expand=1, fill="both")
        
        # ユーザータブの内容
        self.setup_user_tab()
        
        # スクリーンショットタブの内容
        self.setup_screenshot_tab()
    
    def setup_user_tab(self):
        # フレームの作成
        frame = ttk.Frame(self.user_tab, padding="10")
        frame.pack(fill="both", expand=True)
        
        # ユーザーリスト
        self.tree = ttk.Treeview(frame, columns=("ID", "ユーザー名", "メール", "作成日時"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("ユーザー名", text="ユーザー名")
        self.tree.heading("メール", text="メール")
        self.tree.heading("作成日時", text="作成日時")
        
        self.tree.column("ID", width=50)
        self.tree.column("ユーザー名", width=150)
        self.tree.column("メール", width=200)
        self.tree.column("作成日時", width=150)
        
        self.tree.pack(fill="both", expand=True)
        
        # 新規ユーザー追加フォーム
        form_frame = ttk.LabelFrame(frame, text="新規ユーザー追加", padding="10")
        form_frame.pack(fill="x", pady=10)
        
        ttk.Label(form_frame, text="ユーザー名:", font=self.japanese_font).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.username_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.username_var).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(form_frame, text="メールアドレス:", font=self.japanese_font).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.email_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.email_var).grid(row=1, column=1, sticky=tk.W, pady=5)
        
        ttk.Button(form_frame, text="追加", command=self.add_user).grid(row=2, column=1, sticky=tk.E, pady=10)
    
    def setup_screenshot_tab(self):
        frame = ttk.Frame(self.screenshot_tab, padding="10")
        frame.pack(fill="both", expand=True)
        
        if PYAUTOGUI_AVAILABLE:
            ttk.Button(frame, text="スクリーンショットを撮影", command=self.take_screenshot).pack(pady=10)
            
            # スクリーンショット表示エリア
            self.image_label = ttk.Label(frame)
            self.image_label.pack(fill="both", expand=True)
        else:
            ttk.Label(frame, text="PyAutoGUIが利用できないため、スクリーンショット機能は無効です。", 
                     foreground="red", font=self.japanese_font).pack(pady=20)
            ttk.Label(frame, text="環境設定を確認してください。", font=self.japanese_font).pack()
    
    def load_data(self):
        # ツリービューをクリア
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            # データベースに接続
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            
            # ユーザーデータを取得
            cursor.execute("SELECT id, username, email, created_at FROM users")
            users = cursor.fetchall()
            
            # ツリービューに追加
            for user in users:
                self.tree.insert("", "end", values=user)
            
            cursor.close()
            conn.close()
            
            self.status_var.set("データベース: 接続成功")
            
        except Exception as e:
            print(f"データ読み込みエラー: {e}")
            self.status_var.set(f"データベースエラー: {e}")
    
    def add_user(self):
        username = self.username_var.get()
        email = self.email_var.get()
        
        if not username or not email:
            messagebox.showwarning("入力エラー", "ユーザー名とメールアドレスを入力してください")
            return
        
        try:
            # データベースに接続
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            
            # ユーザーデータを追加
            cursor.execute(
                "INSERT INTO users (username, email) VALUES (%s, %s)",
                (username, email)
            )
            conn.commit()
            
            cursor.close()
            conn.close()
            
            # フォームをクリア
            self.username_var.set("")
            self.email_var.set("")
            
            # データを再読み込み
            self.load_data()
            
        except Exception as e:
            messagebox.showerror("データベースエラー", str(e))
    
    def take_screenshot(self):
        if not PYAUTOGUI_AVAILABLE:
            messagebox.showwarning("機能無効", "PyAutoGUIが利用できないため、スクリーンショット機能は使用できません。")
            return
            
        try:
            print("スクリーンショットを撮影しています...")
            # スクリーンショットを撮影（FAILSAFE=Falseの設定で）
            screenshot = pyautogui.screenshot()
            print(f"スクリーンショット撮影成功: サイズ {screenshot.size}")
            
            # PIL ImageをTkinter用に変換
            from PIL import ImageTk
            tk_image = ImageTk.PhotoImage(screenshot)
            
            # 画像を表示
            self.image_label.config(image=tk_image)
            self.image_label.image = tk_image  # 参照を保持
            print("スクリーンショットを表示しました")
            
        except Exception as e:
            print(f"スクリーンショットエラー詳細: {e}")
            messagebox.showerror("スクリーンショットエラー", str(e))

# メインのGUIアプリケーションを起動する関数
def run_gui_app():
    app = Application()
    app.mainloop()

# このスクリプトが直接実行された場合のみGUIを起動
if __name__ == "__main__":
    # コマンドライン引数で--guiフラグが指定された場合のみGUIを起動
    if len(sys.argv) > 1 and sys.argv[1] == '--gui':
        run_gui_app()
    else:
        print("GUIを起動するには 'python main.py --gui' を実行してください")
        print("利用可能なコマンド:")
        print("  --gui: GUIアプリケーションを起動")
        print("例: python main.py --gui") 