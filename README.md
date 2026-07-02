# Epic Games Free Notifier

> Epic 喜加一通知机器人：基于 GitHub Actions 自动检测 Epic Games Store 免费游戏，并通过 Telegram Bot 推送图文通知。

<p align="center">
  <a href="https://github.com/DurianLollipop/EpicFreeGameNotice/actions/workflows/main.yml">
    <img alt="Epic Free Game Notifier" src="https://github.com/DurianLollipop/EpicFreeGameNotice/actions/workflows/main.yml/badge.svg">
  </a>
  <img alt="Python 3.9+" src="https://img.shields.io/badge/python-3.9+-blue.svg">
  <img alt="License MIT" src="https://img.shields.io/badge/license-MIT-green.svg">
</p>

<p align="center">
  <a href="#中文说明">中文说明</a>
  ·
  <a href="#english">English</a>
  ·
  <a href="#常见问题">常见问题</a>
</p>

---

## 中文说明

这是一个零服务器成本的自动化脚本。你只需要 Fork 仓库，并在 GitHub Secrets 中配置 Telegram Bot 信息，就可以每天自动接收 Epic 免费游戏通知。

脚本每天北京时间 10:00 运行一次，适合跟踪每周四常规免费游戏，也能覆盖节日活动期间的每日免费游戏。

## 功能亮点

| 功能 | 说明 |
| :--- | :--- |
| 零成本运行 | 使用 GitHub Actions 定时执行，无需购买服务器 |
| 自动监测 | 每天北京时间 10:00 检查 Epic 免费游戏 |
| 智能去重 | 仅推送新上架约 28 小时内的免费游戏，避免重复打扰 |
| 图文通知 | Telegram 消息包含封面、标题、简介、截止时间和领取链接 |
| Keepalive | 通过保活工作流降低 GitHub 定时任务因长期无提交而暂停的概率 |

## 工作流程

```text
GitHub Actions 定时触发
        |
        v
读取 TG_BOT_TOKEN / TG_CHAT_ID
        |
        v
请求 Epic 免费游戏接口
        |
        v
筛选新上架免费游戏
        |
        v
发送 Telegram 图文通知
```

## 快速部署

### 1. 准备 Telegram Bot

如果你已经有 Bot Token 和 Chat ID，可以跳过本步骤。

**获取 Bot Token**

1. 在 Telegram 搜索 `@BotFather`。
2. 发送 `/newbot`。
3. 按提示创建机器人。
4. 保存 BotFather 返回的 Token，例如 `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`。

**获取 Chat ID**

1. 在 Telegram 搜索 `@userinfobot`。
2. 点击 `Start`。
3. 保存它返回的数字 ID，例如 `123456789`。

### 2. Fork 仓库

1. 点击仓库右上角的 **Fork**。
2. 点击 **Create fork**，复制项目到你的 GitHub 账号下。

### 3. 配置 GitHub Secrets

进入你 Fork 后的仓库：

1. 打开 **Settings**。
2. 进入 **Secrets and variables** -> **Actions**。
3. 点击 **New repository secret**。
4. 添加以下两个变量。

| Name | Value | 说明 |
| :--- | :--- | :--- |
| `TG_BOT_TOKEN` | 你的机器人 Token | 来自 `@BotFather` |
| `TG_CHAT_ID` | 你的数字 ID | 来自 `@userinfobot` |

### 4. 开启工作流写权限

为了让 Keepalive 工作流可以提交保活记录，需要开启写权限：

1. 打开 **Settings**。
2. 进入 **Actions** -> **General**。
3. 找到 **Workflow permissions**。
4. 选择 **Read and write permissions**。
5. 点击 **Save**。

### 5. 首次运行

1. 打开仓库的 **Actions** 标签页。
2. 如果 GitHub 提示启用工作流，点击确认启用。
3. 选择 **Epic Free Game Notifier**。
4. 点击 **Run workflow** 手动运行一次。

## 配置说明

| 配置项 | 位置 | 默认值 |
| :--- | :--- | :--- |
| 定时任务 | `.github/workflows/main.yml` | `0 2 * * *` |
| 运行时间 | GitHub Actions cron 使用 UTC | 北京时间 10:00 |
| Python 版本 | `.github/workflows/main.yml` | `3.9` |
| 依赖文件 | `requirements.txt` | `requests` |

如果要修改运行时间，请编辑 `.github/workflows/main.yml`：

```yaml
schedule:
  - cron: '0 2 * * *'
```

注意：GitHub Actions 的 cron 使用 UTC 时间。

## 常见问题

### 手动运行了，为什么没收到消息？

脚本有去重逻辑。只有当 Epic 免费游戏的促销开始时间距离当前时间小于约 28 小时，才会发送通知。如果当前免费游戏已经上架多天，脚本会跳过它，避免重复推送。

### 每天什么时候自动运行？

默认每天 UTC 02:00 运行，也就是北京时间 10:00。

### 可以关闭 Keepalive 吗？

可以。如果你不需要保活机制，可以删除 `.github/workflows/keepalive.yml`。不过删除后，长期无活动的仓库定时任务可能会被 GitHub 暂停。

## English

Epic Games Free Notifier is a GitHub Actions based automation script that checks Epic Games Store free games every day and sends rich Telegram notifications.

No server is required. Fork the repository, configure two GitHub Secrets, and run the workflow.

### Features

| Feature | Description |
| :--- | :--- |
| Serverless | Runs on GitHub Actions for free |
| Daily check | Runs every day at 02:00 UTC |
| Smart deduplication | Sends notifications only for newly available free games |
| Rich notification | Includes cover image, title, description, end date, and claim link |
| Keepalive | Helps prevent scheduled workflows from being suspended due to inactivity |

### Setup

1. Create a Telegram Bot with `@BotFather` and copy the Bot Token.
2. Get your numeric Chat ID from `@userinfobot`.
3. Fork this repository.
4. Add `TG_BOT_TOKEN` and `TG_CHAT_ID` in **Settings** -> **Secrets and variables** -> **Actions**.
5. Enable **Read and write permissions** in **Settings** -> **Actions** -> **General**.
6. Open the **Actions** tab and run **Epic Free Game Notifier** manually once.

You may not receive a message during a manual test if the current free game has already been available for more than about 28 hours. That means the deduplication logic is working.

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=DurianLollipop/EpicFreeGameNotice&type=Date)](https://star-history.com/#DurianLollipop/EpicFreeGameNotice&Date)

## License

MIT License
