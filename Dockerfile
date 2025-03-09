FROM python:3.9

# システムの依存パッケージをインストール
RUN apt-get update && apt-get install -y \
    python3-tk \
    xvfb \
    x11-utils \
    libx11-dev \
    default-libmysqlclient-dev \
    build-essential \
    default-mysql-client \
    # 日本語フォントと言語サポート
    fonts-ipafont-gothic \
    fonts-ipafont-mincho \
    locales \
    # X11関連のパッケージを追加
    xauth \
    x11-apps \
    && rm -rf /var/lib/apt/lists/*

# 日本語ロケールの設定
RUN sed -i -E 's/# (ja_JP.UTF-8)/\1/' /etc/locale.gen && \
    locale-gen

# 作業ディレクトリの設定
WORKDIR /app

# 環境変数の設定
ENV PYTHONUNBUFFERED=1
ENV NO_AT_BRIDGE=1
ENV LANG=ja_JP.UTF-8
ENV LC_ALL=ja_JP.UTF-8
ENV LANGUAGE=ja_JP:en
# X11認証を無効化（スクリーンショット機能用）
ENV PYAUTOGUI_FAILSAFE=False

# .Xauthorityファイルを作成
RUN touch /root/.Xauthority

# スタートアップスクリプトをコピー
COPY start.sh /app/
RUN chmod +x /app/start.sh

# Pythonパッケージをインストール
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# コンテナ起動時にスタートアップスクリプトを実行
CMD ["/app/start.sh"] 