#!/bin/bash

# start.sh - チーム開発環境用スタートアップスクリプト

# X11関連の設定（スクリーンショット機能のため）
echo "X11サーバー接続を確認しています..."
touch /root/.Xauthority
chmod 600 /root/.Xauthority
echo "X11設定完了"

# 仮想ディスプレイを起動（バックアップとして）
export DISPLAY=${DISPLAY:-:0}
Xvfb ${DISPLAY} -screen 0 1024x768x16 -ac &
sleep 1

# バージョン情報を表示
echo "--------------------------------------"
echo "チーム開発環境 - スタートアップスクリプト"
echo "--------------------------------------"
echo "Python: $(python --version)"
echo "MySQL Client: $(mysql --version)"
echo "環境変数 DISPLAY: $DISPLAY"
echo "ロケール: $(locale | grep LANG)"
echo "--------------------------------------"

# コマンドリストを表示
echo "使用可能なコマンド:"
echo "  python main.py --gui   : GUIアプリケーションを起動"
echo "  python test_gui.py     : テスト用GUIを起動"
echo "  mysql -h db -u user -ppassword app_db  : MySQLデータベースに接続"
echo "  ls -la                 : ファイル一覧を表示"
echo "  cd /app                : アプリケーションディレクトリに移動"
echo "--------------------------------------"

# X11接続テスト
echo "X11接続をテストするには: apt-get update && apt-get install -y x11-apps && xeyes"
echo "--------------------------------------"

# シェルを起動
echo "コマンドを入力してください..."
exec /bin/bash 