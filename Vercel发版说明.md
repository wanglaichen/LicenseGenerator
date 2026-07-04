# 发版说明

本文说明 **RegMachine Web**（注册码 / 激活码生成器）如何发布到线上，以及代码最终部署到哪里。

更完整的功能说明、API 与本地运行见 [README_WEB.md](./README_WEB.md)。

---

## 发到哪里？

| 环境 | 地址 | 说明 |
|------|------|------|
| **生产（Production）** | `https://<你的项目名>.vercel.app` | 用户访问的正式站点 |
| Web 页面 | 同源 `/` | Flask 模板 `templates/index.html` |
| API | 同源 `/api/*` | Flask Serverless 承载，无独立服务器 |

**不会**部署到 VPS 或本机常驻进程；`main` 分支的普通 push **也不会**自动上线。

---

## 怎么触发发版？

生产发布**只**通过推送 **`v*` 版本标签** 触发 GitHub Actions：

```bash
# 1. 确认改动已提交并推到远程
git status
git push origin main

# 2. 打版本标签（示例 v1.0.2，按实际版本递增）
git tag v1.0.2

# 3. 推送标签 → 自动部署到 Vercel Production
git push origin v1.0.2
```

Workflow 文件：`.github/workflows/main.yml`

流程概要：检出代码 → 安装 `uv` 与 Vercel CLI → 检查 Secrets → `vercel pull` → `vercel build --prod` → `vercel deploy --prebuilt --prod`（在**仓库根目录**执行）。

`vercel.json` 已关闭 `main` 分支的 Git 自动部署，避免未打标签的提交误上生产。

---

## 发版前检查清单

### 1. Vercel 项目设置（Dashboard → Settings → General）

| 项 | 正确值 |
|----|--------|
| Root Directory | **留空**（仓库根目录，含 `app.py`） |
| Framework Preset | **Flask**（或 Vercel 自动识别的 Python） |
| Build Command | 通常留空，由 `vercel build` 处理 |
| Output Directory | **留空** |

若 Root Directory 误设为子目录，CI 可能找不到 `app.py` 或依赖文件。

### 2. Vercel 环境变量（Production）

| 变量 | 是否必填 | 说明 |
|------|----------|------|
| `REGISTER_KEY` | **必填** | 8 字节内置密钥；Web 下拉「内置」项及 API 默认密钥 |
| `SECRET_KEY` | 建议填 | Flask 会话等用；生产请用随机字符串，勿用代码默认值 |
| `DEFAULT_SN` | 可选 | Web 页面注册码输入框默认值，可留空 |

在 Vercel 控制台 **Settings → Environment Variables** 配置即可，**不必**放进 GitHub Secrets。

示例（密钥请替换为实际值，勿提交到 Git）：

```text
REGISTER_KEY=你的8字节内置密钥
SECRET_KEY=随机长字符串
DEFAULT_SN=
```

### 3. GitHub Actions Secrets

仓库 **Settings → Secrets and variables → Actions** 需配置：

| Secret | 用途 | 在哪里找 |
|--------|------|----------|
| `VERCEL_TOKEN` | Vercel 账号 Token | [Vercel Account Settings → Tokens](https://vercel.com/account/settings/tokens) → **Create** 生成；复制后粘贴到 GitHub Secret（**勿提交到 Git**） |
| `VERCEL_ORG_ID` | 团队/个人 ID | Vercel 控制台 **所有项目** 页 → **Settings** → **General** → **Team ID** |
| `VERCEL_PROJECT_ID` | 项目 ID | 打开目标项目 → **Settings → General** → **Project ID** 字段（可直接复制） |

也可在仓库根目录执行 `vercel link` 关联项目后，查看本地 `.vercel/project.json` 中的 `orgId`（对应 `VERCEL_ORG_ID`）与 `projectId`（对应 `VERCEL_PROJECT_ID`）；`.vercel/` 已在 `.gitignore` 中忽略，勿提交。

---

## 发版后怎么验证？

1. 打开 `https://<你的项目名>.vercel.app`
2. 访问 `GET /api/health`，应返回 `status: "ok"`、`service: "regmachine-web"`
3. 在首页输入注册码，选择「内置」或自定义密钥，点击「生成注册码」，应得到激活码
4. 可选：`GET /api` 查看可用端点列表

也可在 GitHub Actions 查看本次 tag 对应的 **Deploy to Vercel on Tag** 是否成功；在 Vercel Dashboard 的 Deployments 中确认 Production 已更新。

命令行快速检查（将域名换成你的 Production 地址）：

```powershell
Invoke-RestMethod -Uri "https://<你的项目名>.vercel.app/api/health"
```

---

## 常见问题

| 现象 | 处理 |
|------|------|
| 推了 `main` 但没上线 | 正常。只有推 `v*` 标签才会生产部署 |
| CI 报 `VERCEL_* is not set` | 在 GitHub Actions Secrets 中补全三个 Vercel 相关 Secret |
| CI 构建失败 / 找不到 `app.py` | 核对 Vercel Root Directory 应为空（仓库根） |
| 页面能开但内置密钥不对 | 检查 Production 是否配置了 `REGISTER_KEY`，且长度为 8 字节 |
| 改了环境变量但线上未生效 | 在 Vercel Deployments 对 Production 执行 **Redeploy**，或重新打标签发布 |
| 本地端口 9212 无法监听 | Windows 可能保留该端口；本地可在 `.env` 改 `APP_PORT=5000`（与 Vercel 无关） |

---

## 本地开发（与发版无关）

本地调试**不会**走 Vercel，也**不会**因 push 标签而影响本地：

```powershell
cd E:\BB_pro\gitHub\registerTool
py -m pip install -r requirements.txt
copy env.example .env
# 编辑 .env 后
py app.py
```

浏览器打开 `http://localhost:9212`（或你在 `.env` 中设置的端口）。

---

## 相关文档

- [README_WEB.md](./README_WEB.md) — 功能说明、配置、API 与命令行客户端
- [env.example](./env.example) — 本地环境变量模板
