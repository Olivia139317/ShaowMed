# ShadowMe 云服务器部署说明

目标：让 `@lihua_shadowme_bot` 在云服务器上 24 小时在线，你的电脑关机也能访问。

推荐平台：Oracle Cloud Always Free 或任意 2GB+ Ubuntu VPS。

## 1. 服务器要求

- Ubuntu 22.04 / 24.04
- 2GB RAM 起步，4GB 更稳
- Docker + Docker Compose
- 出站网络可访问 Telegram 和 DeepSeek

## 2. 安装 Docker

```bash
sudo apt update
sudo apt install -y ca-certificates curl git
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo tee /etc/apt/keyrings/docker.asc > /dev/null
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo ${UBUNTU_CODENAME:-$VERSION_CODENAME}) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER
```

退出 SSH 后重新登录，再检查：

```bash
docker version
docker compose version
```

## 3. 拉取项目

```bash
git clone https://github.com/Olivia139317/ShaowMed.git
cd ShaowMed
```

## 4. 准备 OpenClaw 云端配置

```bash
mkdir -p deploy/cloud/openclaw-data
cp deploy/cloud/openclaw.cloud.template.json deploy/cloud/openclaw-data/openclaw.json
```

编辑 `deploy/cloud/openclaw-data/openclaw.json`，替换：

- `${DEEPSEEK_API_KEY}`
- `<YOUR_TELEGRAM_BOT_TOKEN>`
- `<YOUR_TELEGRAM_USER_ID>`
- `<YOUR_DOMAIN>`，没有域名可以先保留占位

权限：

```bash
chmod 600 deploy/cloud/openclaw-data/openclaw.json
```

## 5. 启动云端服务

```bash
docker compose -f deploy/cloud/docker-compose.yml up -d --build
```

检查：

```bash
docker ps
curl http://localhost:5000/health
docker exec openclaw openclaw channels status --probe
```

## 6. 同步 Agent 文件到 OpenClaw 数据卷

```bash
mkdir -p deploy/cloud/openclaw-data/main deploy/cloud/openclaw-data/workspace
cp -r agents/main/* deploy/cloud/openclaw-data/main/
cp -r agents/main/* deploy/cloud/openclaw-data/workspace/
cp deploy/cloud/chat.sh deploy/cloud/openclaw-data/main/chat.sh
cp deploy/cloud/chat.sh deploy/cloud/openclaw-data/workspace/chat.sh
chmod +x deploy/cloud/openclaw-data/main/chat.sh deploy/cloud/openclaw-data/workspace/chat.sh
docker restart openclaw
```

## 7. Telegram 验证

打开 Telegram，给 Bot 发：

```text
测试
```

再发：

```text
晚上吃什么
```

能回复就说明评委可以通过 Telegram 直接在线访问。

## 8. Cloudflare 域名，可选

如果只提交 Telegram Bot 链接，域名不是必需的：

```text
https://t.me/lihua_shadowme_bot
```

如果要把健康检查挂到域名，可后续加 Nginx 或 Cloudflare Tunnel。

## 9. 成本控制

云端 `openclaw.json` 默认 heartbeat 是 `1m`，适合比赛演示。

如果不想产生 DeepSeek 调用：

```bash
docker stop openclaw
```

重新上线：

```bash
docker start openclaw
```
