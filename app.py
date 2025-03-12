import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import time
import os
import datetime
import threading
import pyautogui
import pygetwindow as gw
from PIL import Image, ImageGrab
import configparser
import sys
import traceback

# 停止中フラグをグローバル変数として追加
STOPPING = False

# pygetwindowの例外を安全に処理するラッパー関数
def safe_window_operation(window_obj, operation_name, operation_func, *args, **kwargs):
    """pygetwindowの操作を安全に実行するラッパー関数"""
    try:
        result = operation_func(*args, **kwargs)
        return result, None
    except Exception as e:
        error_msg = f"{operation_name}実行中にエラーが発生: {str(e)}"
        print(error_msg)
        if "Error code from Windows: 0" in str(e):
            # Windows Error Code 0 は実際には成功を意味するが、
            # 何らかの理由で例外になっている場合
            print("Windows Error Code 0（成功）だが例外として報告されました")
            return None, None
        return None, error_msg

class ScreenshotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ウィンドウスクリーンショットアプリ")
        self.root.geometry("500x400")
        
        self.screenshot_thread = None
        self.running = False
        self.save_dir = os.path.expanduser("~/Pictures/Screenshots")  # スクリーンショット保存用のディレクトリ
        
        # 保存ディレクトリが存在しない場合は作成
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
        
        # 設定ファイルがあれば読み込む
        self.load_config()
        
        self.create_ui()
        self.update_window_list()
    
    def load_config(self):
        """設定ファイルから設定を読み込む"""
        config = configparser.ConfigParser()
        config_file = 'config.ini'
        
        if os.path.exists(config_file):
            config.read(config_file)
            if 'Settings' in config:
                settings_section = config['Settings']
                self.save_dir = settings_section.get('save_dir', self.save_dir)
        else:
            # 設定ファイルがない場合は新規作成
            config['Settings'] = {
                'save_dir': self.save_dir
            }
            with open(config_file, 'w') as f:
                config.write(f)
    
    def create_ui(self):
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 保存ディレクトリセクション
        dir_frame = ttk.LabelFrame(main_frame, text="保存ディレクトリ")
        dir_frame.pack(fill=tk.X, pady=(0, 10))
        
        dir_entry_frame = ttk.Frame(dir_frame)
        dir_entry_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.dir_var = tk.StringVar(value=self.save_dir)
        dir_entry = ttk.Entry(dir_entry_frame, textvariable=self.dir_var, width=40)
        dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        browse_btn = ttk.Button(dir_entry_frame, text="参照", command=self.browse_directory)
        browse_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # ウィンドウ選択セクション
        ttk.Label(main_frame, text="スクリーンショットするウィンドウを選択:").pack(anchor=tk.W, pady=(0, 5))
        
        window_frame = ttk.Frame(main_frame)
        window_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.window_combo = ttk.Combobox(window_frame, state="readonly", width=40)
        self.window_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        refresh_btn = ttk.Button(window_frame, text="更新", command=self.update_window_list)
        refresh_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # 時間間隔設定
        interval_frame = ttk.Frame(main_frame)
        interval_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(interval_frame, text="スクリーンショット間隔(秒):").pack(side=tk.LEFT)
        
        self.interval_var = tk.IntVar(value=10)
        interval_spinbox = ttk.Spinbox(interval_frame, from_=1, to=3600, textvariable=self.interval_var, width=5)
        interval_spinbox.pack(side=tk.LEFT, padx=(5, 0))
        
        # 開始/停止ボタン
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.start_btn = ttk.Button(control_frame, text="開始", command=self.start_screenshots)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_btn = ttk.Button(control_frame, text="停止", command=self.stop_screenshots, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT)
        
        # ステータス表示
        status_frame = ttk.LabelFrame(main_frame, text="ステータス")
        status_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.status_var = tk.StringVar(value="待機中...")
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.pack(anchor=tk.W, padx=5, pady=5)
        
        self.last_screenshot_var = tk.StringVar(value="最後のスクリーンショット: なし")
        last_screenshot_label = ttk.Label(status_frame, textvariable=self.last_screenshot_var)
        last_screenshot_label.pack(anchor=tk.W, padx=5, pady=5)
    
    def browse_directory(self):
        """保存ディレクトリを選択するダイアログを表示"""
        dir_path = filedialog.askdirectory(initialdir=self.save_dir)
        if dir_path:
            self.save_dir = dir_path
            self.dir_var.set(dir_path)
            
            # 設定ファイルに保存
            config = configparser.ConfigParser()
            config['Settings'] = {'save_dir': self.save_dir}
            with open('config.ini', 'w') as f:
                config.write(f)
    
    def update_window_list(self):
        """利用可能なウィンドウのリストを更新する"""
        windows = gw.getAllTitles()
        # 空のタイトルをフィルタリングし、実際のウィンドウのみを表示
        windows = [w for w in windows if w.strip()]
        self.window_combo['values'] = windows
        if windows:
            self.window_combo.current(0)
    
    def take_screenshot(self, window_title):
        """指定されたウィンドウのスクリーンショットを撮り、ファイルに保存する"""
        global STOPPING
        
        try:
            # 停止処理中の場合は早期に終了
            if STOPPING:
                return None, datetime.datetime.now()
                
            # デバッグ情報をコンソールに出力
            print(f"スクリーンショット撮影開始: {window_title}")
            
            # ウィンドウの検索
            try:
                windows = gw.getWindowsWithTitle(window_title)
                if not windows:
                    if not STOPPING:  # 停止中でない場合のみエラーメッセージを表示
                        messagebox.showerror("エラー", "指定されたウィンドウが見つかりません")
                    return None, datetime.datetime.now()
                
                window = windows[0]
            except Exception as window_ex:
                if not STOPPING:
                    print(f"ウィンドウ検索中にエラー: {str(window_ex)}")
                    if "Error code from Windows: 0" not in str(window_ex):  # Error 0は無視
                        messagebox.showerror("エラー", f"ウィンドウの検索中にエラーが発生しました: {str(window_ex)}")
                return None, datetime.datetime.now()
            
            # ウィンドウ情報をできるだけ安全に取得
            try:
                left = window.left
                top = window.top
                width = window.width
                height = window.height
                print(f"ウィンドウ情報: 位置=({left}, {top}), サイズ=({width}, {height})")
            except Exception as info_ex:
                if not STOPPING:
                    print(f"ウィンドウ情報取得中にエラー: {str(info_ex)}")
                    if "Error code from Windows: 0" not in str(info_ex):  # Error 0は無視
                        messagebox.showerror("エラー", f"ウィンドウ情報の取得中にエラーが発生しました: {str(info_ex)}")
                return None, datetime.datetime.now()
            
            # 停止処理中の場合は早期に終了
            if STOPPING:
                return None, datetime.datetime.now()
            
            # 画面外にある場合や無効なサイズの場合は調整
            if width <= 0 or height <= 0:
                if not STOPPING:  # 停止中でない場合のみエラーメッセージを表示
                    messagebox.showerror("エラー", f"ウィンドウのサイズが無効です: 幅={width}, 高さ={height}")
                return None, datetime.datetime.now()
                
            # ウィンドウ操作は安全に行う
            try:
                # ウィンドウが最小化されていればアクティブに
                if hasattr(window, 'isMinimized') and window.isMinimized:
                    result, error = safe_window_operation(window, "ウィンドウ復元", window.restore)
                    if error and not STOPPING and "Error code from Windows: 0" not in error:
                        print(error)
                
                # 停止処理中の場合は早期に終了
                if STOPPING:
                    return None, datetime.datetime.now()
                    
                # ウィンドウをアクティブにして少し待つ
                result, error = safe_window_operation(window, "ウィンドウアクティブ化", window.activate)
                if error and not STOPPING and "Error code from Windows: 0" not in error:
                    print(error)
                
                time.sleep(0.5)  # ウィンドウがアクティブになるまでの待機時間を長く
            except Exception as window_op_ex:
                if not STOPPING:
                    print(f"ウィンドウ操作中にエラー: {str(window_op_ex)}")
                    if "Error code from Windows: 0" not in str(window_op_ex):  # Error 0は無視
                        messagebox.showerror("エラー", f"ウィンドウ操作中にエラーが発生しました: {str(window_op_ex)}")
                return None, datetime.datetime.now()
            
            # 停止処理中の場合は早期に終了
            if STOPPING:
                return None, datetime.datetime.now()
                
            # pygetwindowの例外を明示的にキャッチ
            try:
                # ウィンドウ情報が有効か最終確認
                _ = window.left
                _ = window.top
                _ = window.width
                _ = window.height
            except Exception as gw_e:
                if not STOPPING:
                    print(f"PyGetWindow例外: {str(gw_e)}")
                return None, datetime.datetime.now()
                
            # ウィンドウの位置とサイズを取得
            left, top, width, height = window.left, window.top, window.width, window.height
            
            # 画面外にある場合や無効なサイズの場合は調整
            if width <= 0 or height <= 0:
                if not STOPPING:  # 停止中でない場合のみエラーメッセージを表示
                    messagebox.showerror("エラー", f"ウィンドウのサイズが無効です: 幅={width}, 高さ={height}")
                return None, datetime.datetime.now()
            
            # スクリーンショットを撮る - 例外処理を追加
            screenshot = None
            try:
                # 座標チェック
                if left is None or top is None or width is None or height is None:
                    if not STOPPING:
                        print("ウィンドウの座標またはサイズがNoneです")
                    return None, datetime.datetime.now()
                    
                # スクリーンショットを撮る - 例外処理を追加
                try:
                    screenshot = pyautogui.screenshot(region=(left, top, width, height))
                except Exception as e:
                    # PyAutoGUIのスクリーンショット失敗時は別の方法を試す
                    if not STOPPING:
                        self.status_var.set("PyAutoGUIでのスクリーンショット失敗。代替方法を試行中...")
                        print(f"PyAutoGUIでのスクリーンショット失敗: {str(e)}")
                    
                    # 停止処理中の場合は早期に終了
                    if STOPPING:
                        return None, datetime.datetime.now()
                        
                    try:
                        # PILのImageGrabを使用する代替方法
                        screenshot = ImageGrab.grab(bbox=(left, top, left+width, top+height))
                    except Exception as inner_e:
                        if not STOPPING:  # 停止中でない場合のみエラーメッセージを表示
                            print(f"代替スクリーンショット方法も失敗: {str(inner_e)}")
                            if "Error code from Windows: 0" not in str(inner_e):
                                messagebox.showerror("エラー", f"スクリーンショットの撮影中にエラーが発生しました: {str(e)}\n\n代替方法も失敗: {str(inner_e)}\n\nエラータイプ: {type(inner_e).__name__}")
                        return None, datetime.datetime.now()
            except Exception as screenshot_ex:
                if not STOPPING:
                    print(f"スクリーンショット全体の処理で例外: {str(screenshot_ex)}")
                    if "Error code from Windows: 0" not in str(screenshot_ex):
                        messagebox.showerror("エラー", f"スクリーンショット撮影中に予期しないエラーが発生しました: {str(screenshot_ex)}")
                return None, datetime.datetime.now()
                
            # スクリーンショット取得に失敗した場合
            if screenshot is None:
                if not STOPPING:
                    print("スクリーンショットがNoneです")
                return None, datetime.datetime.now()
                
            # 停止処理中の場合は早期に終了
            if STOPPING:
                return None, datetime.datetime.now()
                
            # 現在の時刻
            capture_time = datetime.datetime.now()
            timestamp = capture_time.strftime("%Y%m%d_%H%M%S")
            
            # ファイル名を生成（ウィンドウタイトルから不適切な文字を除去）
            try:
                safe_title = ''.join(c if c.isalnum() or c.isspace() else '_' for c in window_title)[:50].strip()
                if not safe_title:  # 空の場合はデフォルト名
                    safe_title = "window"
                filename = f"{safe_title}_{timestamp}.png"
                filepath = os.path.join(self.save_dir, filename)
            except Exception as filename_ex:
                if not STOPPING:
                    print(f"ファイル名生成中にエラー: {str(filename_ex)}")
                    # エラー時は汎用的なファイル名を使用
                    filename = f"screenshot_{timestamp}.png"
                    filepath = os.path.join(self.save_dir, filename)
            
            # 停止処理中の場合は早期に終了
            if STOPPING:
                return None, datetime.datetime.now()
                
            # PILのImageオブジェクトとして保存
            try:
                try:
                    screenshot.save(filepath)
                    print(f"スクリーンショットを保存しました: {filepath}")
                    return filepath, capture_time
                except OSError as os_error:
                    # 画像形式エラーの場合、別の方法を試す
                    if not STOPPING:
                        print(f"画像保存中にOSエラー: {str(os_error)}")
                        
                    # PILのImageに変換して保存を試みる
                    if hasattr(screenshot, 'tobytes') and hasattr(screenshot, 'size'):
                        pil_img = Image.frombytes('RGB', screenshot.size, screenshot.tobytes())
                        pil_img.save(filepath)
                        print(f"代替方法でスクリーンショットを保存しました: {filepath}")
                        return filepath, capture_time
                        
                # 他の例外
                except Exception as save_ex:
                    if not STOPPING:
                        print(f"画像保存中に例外: {str(save_ex)}")
                        if "Error code from Windows: 0" not in str(save_ex):
                            messagebox.showerror("エラー", f"画像ファイルの保存中にエラーが発生しました: {str(save_ex)}")
                    return None, datetime.datetime.now()
            except Exception as outer_save_ex:
                if not STOPPING:
                    print(f"画像保存全体の処理で例外: {str(outer_save_ex)}")
                    if "Error code from Windows: 0" not in str(outer_save_ex):
                        messagebox.showerror("エラー", f"画像保存処理中に予期しないエラーが発生しました: {str(outer_save_ex)}")
                return None, datetime.datetime.now()
                
        except Exception as e:
            if not STOPPING:  # 停止中でない場合のみエラーメッセージを表示
                error_info = traceback.format_exc()
                print(f"スクリーンショットエラー詳細：\n{error_info}")
                if "Error code from Windows: 0" not in str(e):
                    messagebox.showerror("エラー", f"スクリーンショットの撮影中にエラーが発生しました: {str(e)}\n\nエラータイプ: {type(e).__name__}")
            return None, datetime.datetime.now()
    
    def screenshot_loop(self):
        """定期的にスクリーンショットを撮るループ処理"""
        global STOPPING
        
        while self.running:
            try:
                # 停止中は新しいスクリーンショットを撮らない
                if STOPPING:
                    time.sleep(0.1)
                    continue
                    
                window_title = self.window_combo.get()
                if window_title:
                    try:
                        self.status_var.set(f"スクリーンショット撮影中: {window_title}")
                        filepath, capture_time = self.take_screenshot(window_title)
                        
                        if filepath:
                            self.last_screenshot_var.set(f"最後のスクリーンショット: {os.path.basename(filepath)}, 時刻={capture_time.strftime('%Y-%m-%d %H:%M:%S')}")
                            self.status_var.set(f"保存完了: {os.path.basename(filepath)}")
                        else:
                            self.status_var.set(f"スクリーンショットに失敗しました")
                    except Exception as screenshot_ex:
                        if not STOPPING:
                            if "Error code from Windows: 0" not in str(screenshot_ex):
                                self.status_var.set(f"スクリーンショット中にエラー: {str(screenshot_ex)}")
                                print(f"スクリーンショットエラー: {str(screenshot_ex)}")
            except Exception as e:
                if not STOPPING:  # 停止中でない場合のみエラーメッセージを表示
                    if "Error code from Windows: 0" not in str(e):
                        self.status_var.set(f"エラーが発生しました: {str(e)}")
                        print(f"Screenshot loop error: {str(e)}")
            
            # 指定された間隔だけ待機
            try:
                interval = self.interval_var.get()
                for _ in range(interval):
                    if not self.running:
                        break
                    time.sleep(1)
            except Exception as interval_ex:
                print(f"待機中にエラー: {str(interval_ex)}")
                time.sleep(5)  # エラー時はデフォルトで5秒待機
    
    def start_screenshots(self):
        """スクリーンショット撮影を開始"""
        if not self.window_combo.get():
            messagebox.showwarning("警告", "スクリーンショットするウィンドウを選択してください")
            return
        
        # 保存ディレクトリを確認
        if not os.path.exists(self.save_dir):
            try:
                os.makedirs(self.save_dir)
            except Exception as e:
                messagebox.showerror("エラー", f"保存ディレクトリの作成に失敗しました: {str(e)}")
                return
        
        self.running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
        # 別スレッドでスクリーンショットループを実行
        self.screenshot_thread = threading.Thread(target=self.screenshot_loop)
        self.screenshot_thread.daemon = True
        self.screenshot_thread.start()
    
    def stop_screenshots(self):
        """スクリーンショット撮影を停止"""
        global STOPPING
        
        if not self.running:
            return  # すでに停止している場合は何もしない
            
        # 停止中フラグを設定
        STOPPING = True
        
        # UIの更新
        self.status_var.set("停止処理中...")
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.DISABLED)
        
        # runningフラグを設定してループを終了させる
        self.running = False
        
        # スレッドが完全に終了するのを待機
        if self.screenshot_thread and self.screenshot_thread.is_alive():
            try:
                # 非同期でスレッドの終了を待機（UIがフリーズするのを防ぐ）
                def wait_for_thread():
                    timeout = 3.0  # 最大3秒待機
                    start_time = time.time()
                    while self.screenshot_thread.is_alive() and time.time() - start_time < timeout:
                        time.sleep(0.1)
                    
                    # スレッドの状態に関わらずUIを更新
                    self.root.after(0, lambda: self._finalize_stop())
                
                # 別スレッドでスレッド終了待機を行う
                stopping_thread = threading.Thread(target=wait_for_thread)
                stopping_thread.daemon = True
                stopping_thread.start()
                
            except Exception as e:
                print(f"停止処理中にエラーが発生: {str(e)}")
                self._finalize_stop()  # エラーが発生した場合も停止処理を完了
        else:
            self._finalize_stop()
    
    def _finalize_stop(self):
        """停止処理を完了する"""
        global STOPPING
        STOPPING = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_var.set("停止しました")
        
    def on_closing(self):
        """アプリケーション終了時の処理"""
        global STOPPING
        
        if self.running:
            STOPPING = True
            self.running = False
            # アプリケーション終了時は少し待ってからクローズ
            self.root.after(500, self.root.destroy)
        else:
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenshotApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
