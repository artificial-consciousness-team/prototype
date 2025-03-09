# Docker を使用したチーム開発環境

このプロジェクトは、Docker を使用したチーム開発環境のプロトタイプです。
Python、Tkinter、MySQL、PyAutoGUI を使用したアプリケーションの開発環境が含まれています。

## 機能

- Python + Tkinter による GUI アプリケーション
- MySQL データベース連携
- PyAutoGUI によるスクリーンショット機能
- Docker コンテナによる環境の統一

## セットアップ方法

### 前提条件

- Docker と Docker Compose がインストールされていること
- Windows 環境で GUI を使用する場合は、X11 サーバーがインストールされていること

### 実行手順

1. リポジトリをクローン

```
git clone <リポジトリURL>
cd prototype
```

2. Docker コンテナをビルドして起動

```
docker-compose up -d
```

3. コンテナに接続（対話モード）

```
docker exec -it prototype-app-1 bash
```

4. アプリケーションの実行
   コンテナ内で以下のコマンドを実行：

```
# GUIアプリケーションを起動（X11サーバー必要）
python main.py --gui

# テスト用GUIを起動（X11サーバー必要）
python test_gui.py

# データベースへの接続確認
mysql -h db -u user -ppassword app_db
```

## スクリーンショット機能をセットアップする方法

スクリーンショット機能を使用するには、以下の追加セットアップが必要です：

### 1. 必要なツールのインストール

コンテナ内で以下のコマンドを実行して、必要なパッケージをインストールします：

```bash
# Linuxでスクリーンショットを撮るために必要なscrotツールをインストール
apt-get update && apt-get install -y scrot

# PyAutoGUIの依存関係をインストール（互換性問題の解決）
pip install pyscreeze==0.1.28 Pillow==9.0.0
```

### 2. PyAutoGUI のテスト

以下のコマンドでスクリーンショット機能が正常に動作するか確認できます：

```bash
# テストスクリプトの実行
python test_screenshot.py
```

成功すると「screenshots」フォルダにスクリーンショット画像が保存されます。

### 3. X11 サーバーがインストールされていることを確認

スクリーンショット機能を使用するには、X11 サーバーが正しく設定されている必要があります。以下のコマンドで X11 接続をテストできます：

```bash
# X11接続テスト（目のアイコンが表示されれば成功）
apt-get update && apt-get install -y x11-apps && xeyes
```

## スクリーンショット機能の使用方法

スクリーンショット機能を使用するには、以下の手順を実行してください：

1. VcXsrv などの X11 サーバーを、「Disable access control」オプションを有効にして起動
2. コンテナを起動した状態で、次のコマンドを実行して GUI を表示

```
python main.py --gui
```

3. 「スクリーンショット」タブを選択
4. 「スクリーンショットを撮影」ボタンをクリック

スクリーンショット機能がエラーになる場合は、以下のコマンドで X11 接続をテストしてください：

```
apt-get update && apt-get install -y x11-apps && xeyes
```

## Windows での X11 サーバーのセットアップ（GUI 表示に必要）

GUI アプリケーションを表示するには、X11 サーバーのセットアップが必要です。

### 1. VcXsrv のインストール

1. [VcXsrv Windows X Server](https://sourceforge.net/projects/vcxsrv/) から VcXsrv をダウンロード
2. ダウンロードしたインストーラーを実行し、インストール

### 2. VcXsrv の起動と設定

1. スタートメニューから「XLaunch」を実行
2. 以下の設定で起動：
   - **Display settings**: 「Multiple windows」を選択
   - **Display number**: 「0」を入力
   - **Client startup**: 「Start no client」を選択
   - **Extra settings**: 以下のオプションをすべてチェック
     - 「Clipboard」
     - 「Primary Selection」
     - 「Native opengl」
     - 「Disable access control」（**重要**: これがないとコンテナからの接続が拒否されます）
3. 「Save configuration」ボタンをクリックして設定を保存しておくと便利です
4. 「Finish」ボタンをクリックして X11 サーバーを起動

### 3. X11 サーバーの動作確認

コンテナに接続後、以下のコマンドを実行して X11 が正常に動作しているか確認できます：

```bash
# X11接続テスト（目のアイコンが表示されれば成功）
apt-get update && apt-get install -y x11-apps && xeyes
```

### トラブルシューティング

- **「couldn't connect to display」エラーが発生する場合**:

  - VcXsrv が起動しているか確認
  - VcXsrv の設定で「Disable access control」にチェックが入っているか確認
  - Windows ファイアウォールの設定で VcXsrv の通信を許可
  - `docker-compose.yml`の`DISPLAY`環境変数が正しく設定されているか確認

- **PyAutoGUI が「.Xauthority file not found」エラーを出す場合**:

  - コンテナを再起動して、start.sh スクリプトが`.Xauthority`ファイルを正しく作成するようにする
  - コンテナ内で手動で`touch /root/.Xauthority && chmod 600 /root/.Xauthority`を実行

- **PyAutoGUI が「scrot must be installed」エラーを出す場合**:

  - コンテナ内で`apt-get update && apt-get install -y scrot`を実行

- **PyAutoGUI が依存関係エラーを出す場合**:

  - コンテナ内で`pip install pyscreeze==0.1.28 Pillow==9.0.0`を実行

- **スクリーンショットが黒い画面になる場合**:

  - Xvfb の代わりにホストの実際の X11 サーバーを使用していることを確認
  - Windows ファイアウォールで VcXsrv の通信を許可

- **表示が遅い、または応答しない場合**:
  - グラフィックドライバを最新版に更新
  - VcXsrv の設定で「Native opengl」のチェックを外してみる

## コンテナ構成

- **app**: Python + Tkinter + PyAutoGUI を含むアプリケーションコンテナ
- **db**: MySQL データベースコンテナ

## ファイル構造

- `Dockerfile`: アプリケーションコンテナの定義
- `docker-compose.yml`: マルチコンテナ環境の構成
- `requirements.txt`: Python パッケージの依存関係
- `main.py`: サンプルアプリケーション
- `test_gui.py`: テスト用 GUI アプリケーション
- `test_screenshot.py`: スクリーンショット機能のテスト用スクリプト
- `init-db/`: データベース初期化スクリプト
- `start.sh`: コンテナ起動時に実行されるスタートアップスクリプト

## 開発の流れ

1. ローカルでコードを編集
2. 変更はリアルタイムでコンテナ内に反映（ボリュームマウント）
3. コンテナ内でコマンドを実行して動作確認
4. 必要に応じてコンテナを再起動：`docker-compose restart app`

## 注意事項

- GUI を使用するには X11 サーバーが必要です
- PyAutoGUI のスクリーンショット機能は X11 サーバーの接続が正常でないと利用できません
- データベース操作は X11 サーバーがなくても実行可能です
