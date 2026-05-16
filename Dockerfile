FROM python:3.11-slim

WORKDIR /app

# 安装必要的系统依赖（如果 EmQuant SDK 需要）
# RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 如果需要安装 EmQuant SDK 轮子，可以在此处复制并安装
# COPY EmQuantAPI-*.whl .
# RUN pip install EmQuantAPI-*.whl

COPY . .

# 暴露端口
EXPOSE 8000

# 启动应用
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
