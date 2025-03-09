import pyautogui
import time
import os

print("PyAutoGUIのバージョン:", pyautogui.__version__)
print("スクリーンショットのテスト開始...")

# スクリーンショットの保存先
SAVE_DIR = "screenshots"
os.makedirs(SAVE_DIR, exist_ok=True)

# 現在時刻をファイル名に使用
timestamp = time.strftime("%Y%m%d_%H%M%S")
filename = f"{SAVE_DIR}/screenshot_{timestamp}.png"

try:
    # フェイルセーフを無効化
    pyautogui.FAILSAFE = False
    
    # スクリーンショットを撮影
    print("スクリーンショットを撮影しています...")
    screenshot = pyautogui.screenshot()
    
    # スクリーンショットが取れたかどうかを確認
    if screenshot:
        print(f"スクリーンショットのサイズ: {screenshot.size}")
        
        # 画像を保存
        screenshot.save(filename)
        print(f"スクリーンショットを保存しました: {filename}")
        
        # 画像が実際に存在するか確認
        if os.path.exists(filename):
            print(f"ファイルサイズ: {os.path.getsize(filename)} バイト")
        else:
            print("ファイルの保存に失敗しました")
    else:
        print("スクリーンショットの撮影に失敗しました（Noneが返されました）")
        
except Exception as e:
    print(f"エラーが発生しました: {e}")
    
print("テスト終了") 