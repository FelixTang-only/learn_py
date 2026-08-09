# 抖音自动回复（评论 + 私信）

基于 **Playwright** 浏览器自动化，按 `config.yaml` 中的 **关键词模板** 自动回复：

- 自己作品下的评论（创作者中心）
- 新私信（抖音 Web 消息）

## 风险说明

- 抖音用户协议通常禁止未经授权的自动化操作，使用可能导致限制或封号，请自行承担风险。
- 仅限管理**本人账号**；请控制频率，勿用于骚扰或违规引流。
- 页面改版会导致选择器失效，需更新 `src/comments.py` / `src/messages.py` 中的 `SELECTORS`。
- **不会**绕过验证码、风控或逆向私有协议。

## 环境要求

- Python 3.10+
- 可弹出浏览器的桌面环境（首次登录必须有界面）

## 安装

```bash
cd douyin_auto_reply
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
cp config.example.yaml config.yaml
```

按需编辑 `config.yaml` 中的关键词与默认话术。

## 使用

### 1. 扫码登录（只需一次，会话过期后重做）

```bash
python main.py login
```

登录态保存在 `.playwright/douyin-profile/`，请勿提交到 Git。

### 2. 试跑（不发送）

```bash
python main.py run --dry-run --once
```

### 3. 正式运行

```bash
python main.py run
```

常用参数：

| 参数 | 说明 |
|------|------|
| `--dry-run` | 只打印拟回复，不发送 |
| `--once` | 只跑一轮 |
| `--comments-only` | 只处理评论 |
| `--messages-only` | 只处理私信 |
| `-v` | 调试日志 |

## 配置说明

`config.yaml` 要点：

- `rules`：按顺序匹配，命中第一条即停
- `default_replies`：未命中关键词时随机选一条
- `blacklist_keywords`：包含这些词则不回复
- `poll_interval_seconds` / `action_delay_ms`：轮询与操作间隔
- `urls`：创作者中心评论页、私信入口 URL

已回复记录存在 `data/replies.db`，用于去重。

## 目录结构

```
douyin_auto_reply/
  main.py
  config.example.yaml
  src/
    config.py
    reply_engine.py
    store.py
    browser.py
    comments.py
    messages.py
    utils.py
  data/                 # 运行时生成
  .playwright/          # 登录态，运行时生成
```

## 故障排查

1. **提示未登录** → 重新执行 `python main.py login`
2. **找不到评论/会话节点** → 用有界面模式打开页面，对照 DOM 更新对应模块的 `SELECTORS`
3. **私信入口打不开** → 手动在浏览器打开消息面板，或修改 `urls.messages`
