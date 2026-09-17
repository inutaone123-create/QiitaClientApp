FROM ubuntu:22.04

# タイムゾーン設定
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Tokyo

# 基本パッケージ
RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv \
    build-essential \
    wget apt-transport-https \
    git curl vim nano \
    zsh sudo \
    ca-certificates \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Node.js インストール（Claude Code用）
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Claude Code インストール
RUN npm install -g @anthropic-ai/claude-code

# GitHub CLI (gh) インストール
RUN mkdir -p -m 755 /etc/apt/keyrings && \
    wget -nv -O /etc/apt/keyrings/githubcli-archive-keyring.gpg https://cli.github.com/packages/githubcli-archive-keyring.gpg && \
    chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null && \
    apt-get update && \
    apt-get install -y gh && \
    rm -rf /var/lib/apt/lists/*

# Python パッケージ
RUN pip3 install \
    fastapi==0.115.6 \
    uvicorn[standard]==0.34.0 \
    sqlalchemy==2.0.36 \
    python-multipart==0.0.20 \
    markdown==3.7 \
    pydantic==2.10.3 \
    httpx==0.28.1 \
    respx==0.22.0 \
    python-dotenv==1.0.1 \
    pytest==8.3.4 \
    pytest-asyncio==0.25.0 \
    black>=23.0.0 \
    sphinx>=7.0.0 \
    sphinx-rtd-theme>=1.3.0

WORKDIR /workspace

CMD ["sleep", "infinity"]
