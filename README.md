# 🔍 YOLO Object Counter

🌐 **[English](README_EN.md)**

基于 YOLO ONNX 的通用小物体自动检测与计数 Web 服务。支持手机/平板/桌面浏览器访问，提供 CLI 命令行工具供 AI Agent 调用。

---

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 安装 CLI 工具（可选，推荐）
pip install -e agent-harness/

# 3. 下载模型文件放到 models/ 目录（见下方"模型下载"）

# 4. 启动管理面板（推荐新手）
python server_panel.py

# 5. 或直接启动 Web 服务器
python web_server.py --port 8000

# 6. 浏览器打开 http://localhost:8000
```

首次启动会自动生成 API Key，在管理面板或终端可以看到。

---

## 模型下载

模型文件未包含在 Git 仓库中。将 `.onnx` 模型文件放入 `models/` 目录即可。

**支持的模型格式**：YOLO ONNX（YOLOv8/v9/v10/v11/v12/26m 等通用 YOLO 导出格式均可使用）。推荐模型：`yolo26m_v2.onnx`

---

## 使用方式

### 方式一：管理面板（桌面 GUI）

```bash
python server_panel.py
python server_panel.py --auto-start  # 启动面板同时自动启动服务器
```

管理面板提供一键启停、配置管理、实时监控、模型切换、在线设备管理等功能。

![管理面板](docs/服务器GUI页面.png)

### 方式二：命令行（CLI）

```bash
# 安装后可用四个命令
count       # 主 CLI（检测、配置、模型管理、服务器管理、统计）
counton     # 一键启动全栈（面板 + 服务器 + Cloudflared）
countoff    # 一键停止全栈
countkey    # 查看当前 API Key
```

```bash
count detect image.jpg           # 直接检测图片
count server start               # 启动 Web 服务器
count config show                # 查看当前配置
count model list                 # 列出可用模型
count health                     # 服务器健康状态
```

### 方式三：Web 界面

浏览器打开 `http://localhost:8000`。

![初始页面](docs/Web页面未检测.jpg)
![检测结果](docs/检测完毕，页面未打开高级设置.jpg)

功能特性：
- 📷 图片上传（拖拽 / 粘贴 / 点击选择）
- 🚀 一键检测，实时进度条
- 📊 置信度分布柱状图
- 🔍 结果图片全屏缩放（支持拖拽、滚轮、触屏手势）
- ⚙️ 高级设置：置信度阈值、IoU 阈值、模型切换
- 🌐 中英文语言切换（设置全局生效）
- 💾 低置信度样本保存（用于模型优化）

#### 键盘快捷键

| 操作 | 按键 |
|------|------|
| 触发检测 | `Enter` |
| 粘贴图片 | `Ctrl+V` |
| 关闭缩放 | `ESC` |
| 放大 / 缩小 | `+` / `-` |
| 适应屏幕 | `0` |

---

## 启动参数

```bash
python web_server.py --port 8080              # 指定端口
python web_server.py --no-auth                # 关闭认证（调试用）
python web_server.py --api-key my-custom-key  # 指定 API Key
```

---

## 配置说明

配置文件：`config.yaml`

```yaml
port: 8000                          # 端口
host: "0.0.0.0"                     # 监听地址
require_api_key: true               # 是否要求 API Key 认证
language: "zh"                      # 界面语言（zh/en）

model_path: models/yolo26m_v2.onnx  # 模型文件路径
input_size: 640                     # 模型输入尺寸
score_threshold: 0.25               # 置信度阈值
nms_threshold: 0.5                  # NMS 阈值

max_upload_mb: 10                   # 最大上传文件大小（MB）
rate_limit_per_minute: 60           # 每分钟最大请求数

valuable_dir: "Valuable photos"     # 优质照片存储目录
valuable_enable: false              # 是否启用优质照片筛选

enable_response_compression: true   # 响应压缩
tunnel_url: ""                      # Cloudflared 隧道地址
```

> `config.local.yaml` 可用于存放个人配置（已被 `.gitignore` 排除）。

---

## API 接口

### 公开端点

| 路由 | 方法 | 说明 |
|------|------|------|
| `/` | GET | Web 前端页面 |
| `/api/health` | GET | 健康检查 |
| `/api/ping` | GET | 心跳检测 |
| `/api/config` | GET | 公开配置 |
| `/api/models` | GET | 可用模型列表 |

### 认证端点（需要 Bearer Token）

| 路由 | 方法 | 说明 |
|------|------|------|
| `/api/detect` | POST | 上传图片进行目标检测 |
| `/api/language` | PUT | 切换界面语言 |
| `/api/key` | GET | 获取 API Key |
| `/api/key/regenerate` | POST | 重新生成 API Key |
| `/api/toggle-auth` | POST | 切换认证开关 |
| `/api/stats` | GET | 检测统计 |
| `/api/select-model` | POST | 切换模型 |
| `/api/online-devices` | GET | 在线设备列表 |
| `/api/kick-device` | POST | 踢出指定设备 |
| `/api/valuable-stats` | GET | 优质照片统计 |
| `/api/valuable-toggle` | POST | 切换优质照片筛选 |

### 调用示例

```bash
# 获取 API Key
curl http://localhost:8000/api/key

# 图片检测
curl -X POST http://localhost:8000/api/detect \
  -H "Authorization: Bearer <API_KEY>" \
  -F "file=@sample.jpg"

# 切换语言
curl -X PUT http://localhost:8000/api/language \
  -H "Authorization: Bearer <API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{"language": "en"}'
```

---

## 远程访问

### Cloudflared Tunnel

```bash
cloudflared tunnel login
cloudflared tunnel create yolo-object-counter
cloudflared tunnel route dns yolo-object-counter your-domain.example.com
cloudflared tunnel run yolo-object-counter
```

### Tailscale

```bash
tailscale up
```

管理面板会自动检测 Tailscale / Cloudflared 状态并显示访问地址。

---

## 安全特性

- **API Key 认证**：`secrets.token_urlsafe(32)` 生成，防时序攻击
- **ScanGuard 扫描防护**：异常访问自动进入保护模式
- **限速保护**：IP 级别限速，支持自动封禁
- **路径穿越防护**：模型选择接口禁止 `../` 路径
- **日志脱敏**：API Key 在日志中自动遮蔽

---

## 项目结构

```
├── web_server.py             # FastAPI 入口
├── server_panel.py           # 桌面管理面板（Tkinter）
├── config.yaml               # 配置文件
├── requirements.txt          # Python 依赖
├── objcounter/               # 核心包
│   ├── config.py             #   配置管理
│   ├── i18n.py               #   国际化翻译
│   ├── detector.py           #   YOLO ONNX 检测器
│   ├── guard.py              #   ScanGuard 扫描防护
│   ├── middleware.py          #   认证 + 限速中间件
│   ├── state.py              #   集中应用状态
│   ├── routes/               #   API 路由
│   │   ├── detect.py         #     图片检测
│   │   ├── admin.py          #     管理接口
│   │   ├── models.py         #     模型管理
│   │   ├── devices.py        #     设备管理
│   │   └── pages.py          #     页面 + 优质照片
│   └── panel_ui.py / panel_controls.py  # 面板
├── templates/
│   └── index.html            # Web 前端
├── agent-harness/            # CLI 工具
├── models/                   # 模型文件目录
└── Valuable photos/          # 优质照片存储目录
```

## 技术栈

- **后端**：Python 3.8+ / FastAPI / Uvicorn
- **推理**：ONNX Runtime（支持 CUDA / CPU）
- **模型**：Ultralytics YOLO 系列 ONNX 导出格式
- **前端**：原生 HTML/CSS/JS（无外部 CDN 依赖）
- **桌面面板**：Tkinter / CustomTkinter
- **图像处理**：OpenCV / NumPy

## 版本历史

| 版本 | 日期 | 里程碑 |
|------|------|--------|
| v0.1.0 | 2026-04-27 | 初始原型 |
| v0.7.0 | 2026-05-03 | 低带宽优化、骨架屏 |
| v0.8.0 | 2026-05-11 | 项目重构、模块化 |
| v2.0.0 | 2026-05-15 | objcounter/ 包拆分 |
| v3.0.0 | 2026-05-17 | Cloudflared 隧道 |
| v4.1.0 | 2026-05-19 | CLI 工具 + 公开发布 |
| v5.0.0 | 2026-05-22 | 通用化重构 |
| v5.5.0 | 2026-05-26 | 中英文语言切换 |

## 许可证

[PolyForm Noncommercial License 1.0.0](LICENSE) — 允许非商业使用，禁止商业用途。
