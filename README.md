# Campus Buzz

Campus Buzz 是一个混合云 Mini-project，演示前端提交、工作流服务、数据持久化、以及 Serverless 事件处理的基础集成。

该项目目标是构建一个简单且可复现的"事件提交 -> 工作流记录 -> 事件触发 -> 处理函数 -> 结果回填"流程。项目不涉及复杂登录、权限系统或高端 UI 美化，适合快速验证系统架构和服务编排。

## 项目结构

```
campus-buzz/
├── docker-compose.yml
├── README.md
├── requirements.txt
├── start-services.sh          # 快速启动脚本
├── venv/                      # Python 虚拟环境（运行脚本后自动创建）
├── services/
│   ├── data-service/
│   │   ├── api.py            # Flask API 服务，提供事件记录 CRUD
│   │   ├── database.py       # SQLAlchemy 模型定义
│   │   ├── Dockerfile        # 数据服务容器配置
│   │   └── requirements.txt  # Python 依赖
│   ├── workflow/
│   │   ├── main.py           # Flask API 服务，处理事件提交
│   │   ├── Dockerfile        # 工作流服务容器配置
│   │   └── requirements.txt  # Python 依赖
│   └── presentation/
│       ├── Dockerfile        # 前端容器配置
│       ├── package.json      # Node.js 依赖和脚本
│       ├── public/
│       │   └── index.html    # React 应用入口
│       └── src/
│           ├── App.js        # 主 React 组件
│           ├── index.js      # React 应用入口点
│           ├── index.css     # 样式文件
│           └── setupProxy.js # 开发环境代理配置
└── functions/
    ├── submission-event/
    │   ├── index.js          # Serverless 函数模拟
    │   └── Dockerfile        # 函数容器配置
    ├── processor/
    │   ├── logic.py          # 事件处理逻辑
    │   ├── app.py            # 处理函数 Flask 应用
    │   └── Dockerfile        # 函数容器配置
    └── result-update/
        ├── updater.py        # 结果更新逻辑
        ├── app.py            # 更新函数 Flask 应用
        └── Dockerfile        # 函数容器配置
```

## 核心功能说明

- **Data Service** (`services/data-service`)：基于 Flask + SQLAlchemy 的 REST API 服务
  - 提供事件记录的完整 CRUD 操作
  - 使用 SQLite 数据库存储数据
  - 支持 CORS 跨域请求

- **Workflow Service** (`services/workflow`)：基于 Flask 的工作流编排服务
  - 接收前端事件提交请求
  - 创建初始 PENDING 状态的记录到 Data Service
  - 模拟触发 Serverless Submission Event Function

- **Presentation Service** (`services/presentation`)：基于 React + Material-UI 的现代化前端
  - 提供直观的事件提交表单
  - 实时显示事件列表
  - 直接调用后端 API（不使用代理）

- **Processing Function** (`functions/processor`)：事件处理逻辑
  - 实现完整的业务规则验证
  - 根据内容自动分类和优先级分配
  - 支持多种状态判断

- **Serverless Functions**：预留的云函数模拟接口
  - Submission Event：事件提交触发器
  - Result Update：处理结果回填器

## 先决条件

### 必需环境
- **Python 3.11+**（推荐 3.11 或 3.12）
  - 用于运行 Flask 后端服务
- **Node.js 18+**（推荐 18.x LTS）
  - 用于运行 React 前端
- **Git**
  - 用于克隆仓库

### 可选环境
- **Docker & Docker Compose**
  - 用于容器化部署（当前 README 重点介绍本地开发方式）

### 系统要求
- **macOS** (已测试)
- **Linux** / **Windows** (理论兼容，需要相应调整脚本)

## 本地复现步骤

### 🚀 快速启动（推荐）

```bash
# 1. 克隆项目
git clone <your-github-repo-url>
cd campus-buzz

# 2. 运行启动脚本（一键启动所有服务）
./start-services.sh
```

启动脚本会自动：
- ✅ 检查系统依赖（Python 3.11+, Node.js 18+）
- ✅ 创建 Python 虚拟环境
- ✅ 安装所有依赖包
- ✅ 启动三个服务（Data:5002, Workflow:5001, Frontend:3000）
- ✅ 自动打开浏览器访问前端

### 🛠️ 手动启动步骤（备选）

如果自动脚本有问题，可以手动启动：

#### 1. 环境准备
```bash
# 克隆项目
git clone <your-github-repo-url>
cd campus-buzz

# 创建 Python 虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 安装 Python 依赖
pip install -r requirements.txt
```

#### 2. 启动 Data Service
```bash
# 终端窗口 1
cd services/data-service
python api.py
```
服务地址：`http://localhost:5002`

#### 3. 启动 Workflow Service
```bash
# 终端窗口 2
cd services/workflow
DATA_SERVICE_URL=http://localhost:5002 python main.py
```
服务地址：`http://localhost:5001`

#### 4. 启动前端
```bash
# 终端窗口 3
cd services/presentation
npm install
npm start
```
前端地址：`http://localhost:3000`

### 🧪 快速验证

启动所有服务后，运行以下命令验证：

```bash
# 1. 检查服务是否运行
curl -s http://localhost:5001/ | head -1  # 应该返回 Workflow Service 信息
curl -s http://localhost:5002/ | head -1  # 应该返回 Data Service 信息

# 2. 测试完整流程
curl -X POST http://localhost:5001/api/submit \
  -H "Content-Type: application/json" \
  -d '{"title":"测试事件","description":"这是一个测试","location":"测试地点","date":"2024-12-31","organiser":"测试者"}'

# 3. 检查数据是否创建
curl http://localhost:5002/records | jq '.[0]'  # 查看第一条记录
```

### 📊 服务端口说明

- **Frontend**: `http://localhost:3000` - React 应用
- **Workflow Service**: `http://localhost:5001` - 事件提交处理
- **Data Service**: `http://localhost:5002` - 数据存储和查询

## 服务接口说明

### Data Service

- `GET /`：服务信息
- `POST /records`：创建记录，必需字段：`title`, `description`, `location`, `date`, `organiser`
- `GET /records`：查询所有记录
- `GET /records/<id>`：查询单条记录
- `PATCH /records/<id>`：更新记录的 `status`, `category`, `priority`, `note`

### Workflow Service

- `GET /`：服务信息
- `POST /api/submit`：接收前端事件提交，创建 `PENDING` 记录并调用 `Submission Event Function`

## System Workflow

1. **用户提交事件**：前端表单将 `title`, `description`, `location`, `date`, `organiser` 发送到 Workflow Service。
2. **Workflow Service 存储初始记录**：Workflow Service 调用 Data Service 的 `POST /records`，将事件保存为 `PENDING` 状态。
3. **触发 Submission Event**：Workflow Service 将事件元数据发送到 Submission Event Function 模拟入口。
4. **Processing Function 执行判定**：Processing Function 接收事件并按规则执行完整性、格式检查和关键词分类。
5. **更新判定结果**：Processing Function 将最终结果通过 Result Update Function 回传到 Data Service。
6. **前端展示结果**：Presentation Service 定期读取 Data Service 中的记录，并展示 `final_status`, `assigned_category`, `assigned_priority`, `note` 等判定结果。

## Event Processing Rules

- **INCOMPLETE**：若任一必填字段 `title`, `description`, `location`, `date`, `organiser` 缺失或为空，即返回 `INCOMPLETE`。
- **NEEDS REVISION**：若日期格式不符合 `YYYY-MM-DD`，或 `description` 字符数少于 40，则返回 `NEEDS REVISION`。
- **APPROVED**：当完整性检查和格式检查均通过后，事件进入分类与优先级判定，即返回 `APPROVED`。

### 关键词分类优先级（Precedence）

1. `OPPORTUNITY`：匹配关键词 `career`, `internship`, `recruitment`
2. `ACADEMIC`：匹配关键词 `workshop`, `seminar`, `lecture`
3. `SOCIAL`：匹配关键词 `club`, `society`, `social`
4. `GENERAL`：以上关键词均未匹配时归为 `GENERAL`

### Priority 映射

- `OPPORTUNITY` → `HIGH`
- `ACADEMIC` → `MEDIUM`
- `SOCIAL` → `NORMAL`
- `GENERAL` → `NORMAL`

## API Specification

### Workflow Service -> Processing Function

请求体结构：

```json
{
  "id": 123,
  "title": "Campus Recruitment Fair",
  "description": "A large-scale recruitment event with multiple companies and internship opportunities.",
  "location": "Main Hall",
  "date": "2024-04-20",
  "organiser": "Career Center"
}
```

### Processing Function 返回 / Result Update 传递结构

回传到 Data Service 的结果中包含：

```json
{
  "id": 123,
  "status": "APPROVED",
  "final_status": "APPROVED",
  "category": "OPPORTUNITY",
  "assigned_category": "OPPORTUNITY",
  "priority": "HIGH",
  "assigned_priority": "HIGH",
  "note": "Processing successful."
}
```

其中 `final_status`, `assigned_category`, `assigned_priority` 为前端展示的核心判定字段。

## Processing Function 规则说明

`functions/processor/logic.py` 实现了以下规则：

1. 完整性检查：若缺少任意字段，返回 `INCOMPLETE`。
2. 日期校验：若格式不是 `YYYY-MM-DD`，返回 `NEEDS_REVISION`。
3. 描述长度：若描述少于 40 字符，返回 `NEEDS_REVISION`。
4. 类别分配：优先关键字规则 `OPPORTUNITY > ACADEMIC > SOCIAL > GENERAL`。
5. 优先级分配：`OPPORTUNITY` => `HIGH`，`ACADEMIC` => `MEDIUM`，其余 => `NORMAL`。

该逻辑已确保 `INCOMPLETE` 优先级最高，并在缺失字段时直接返回结果，不继续后续规则判断。

## Docker Compose 说明

仓库提供了 `docker-compose.yml`，用于稍后容器化三个主要服务：

- `presentation`
- `workflow-service`
- `data-service`

当前文件也预留了 Serverless 回调 URL 环境变量 `SUBMISSION_EVENT_URL` 和 `RESULT_UPDATE_URL`，方便后续扩展到函数模拟容器。

> 注意：当前本地复现更稳妥，容器化版本仍需根据实际环境检查 `services/presentation` 前端构建是否完整。

## 如何把代码上传到 GitHub

以下步骤假设你已经在 GitHub 上创建了一个空仓库，例如 `https://github.com/<your-username>/campus-buzz.git`。

1. 检查当前仓库状态：

```bash
git status
```

2. 添加所有文件：

```bash
git add .
```

3. 提交改动：

```bash
git commit -m "Add React frontend with Material-UI for better visualization"
```

4. 添加远程仓库（如果还未添加）：

```bash
git remote add origin https://github.com/<your-username>/campus-buzz.git
```

5. 推送到 GitHub：

```bash
git push -u origin main
```

如果你的主分支叫 `master`，请改成：

```bash
git push -u origin master
```

## 其他建议

### 🔄 扩展开发

- **添加 Processing Function**：实现 `functions/processor/logic.py` 的完整事件处理逻辑
- **集成 Serverless Functions**：完善 `functions/` 目录下的云函数模拟
- **添加用户认证**：集成简单的登录系统（可选）
- **数据库升级**：从 SQLite 迁移到 PostgreSQL

### 🐳 容器化部署

当前项目支持 Docker 部署：

```bash
# 构建并启动容器
docker-compose up --build

# 或后台运行
docker-compose up -d
```

注意：容器化版本需要调整服务间的网络配置。

### 📈 性能优化

- **数据库连接池**：在高并发场景下优化 SQLAlchemy 配置
- **API 缓存**：添加 Redis 缓存层
- **前端优化**：实现代码分割和懒加载

### 🤝 贡献指南

1. Fork 项目
2. 创建特性分支：`git checkout -b feature/amazing-feature`
3. 提交更改：`git commit -m 'Add amazing feature'`
4. 推送分支：`git push origin feature/amazing-feature`
5. 创建 Pull Request

### 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 常见问题

### 🚨 启动问题

**Q: 运行 `./start-services.sh` 后报错 "command not found"**
- A: 确保脚本有执行权限：`chmod +x start-services.sh`

**Q: Python 版本问题或依赖安装失败**
- A: 检查 Python 版本：`python3 --version`
- 确保使用系统 Python 或正确配置环境

**Q: Node.js 未找到或版本过低**
- A: 检查 Node.js：`node --version`
- 如果使用 nvm，启动脚本会自动加载

**Q: 端口被占用**
- A: 检查端口使用：`lsof -i :5001 -i :5002 -i :3000`
- 停止占用进程或修改端口配置

### 🔧 运行时问题

**Q: 前端显示 504 Gateway Timeout**
- A: 后端服务未正确启动或连接失败
- 检查所有服务是否在运行：`ps aux | grep -E "(python|node)"`
- 确保 Workflow Service 使用正确的 Data Service URL

**Q: 提交事件后无响应或显示错误**
- A: 检查所有必需字段是否填写完整
- 验证后端服务状态：`curl http://localhost:5001/` 和 `curl http://localhost:5002/`

**Q: 事件列表不显示**
- A: 检查前端是否能访问 Data Service
- 验证 CORS 设置和网络连接

### 🐛 调试技巧

**检查服务状态**：
```bash
# 查看运行进程
ps aux | grep -E "(python|node)" | grep -v grep

# 测试 API 连接
curl http://localhost:5001/  # Workflow Service
curl http://localhost:5002/  # Data Service
curl http://localhost:3000   # Frontend
```

**查看服务日志**：
- 前端：浏览器开发者工具 Console
- 后端：终端窗口直接查看输出

**重置数据**：
```bash
# 删除数据库文件重新开始
rm services/data-service/events.db
```

### 📋 环境兼容性

**macOS (已测试)**：
- 使用 Homebrew 安装 Python 和 Node.js
- 虚拟环境路径：`venv/bin/activate`

**Linux**：
- 确保 Python 3.11+ 和 pip 已安装
- 可能需要：`sudo apt install python3-venv`

**Windows**：
- 使用 PowerShell 或 Git Bash
- 虚拟环境路径：`venv\Scripts\activate`
- 脚本可能需要调整为 `.bat` 或 `.ps1` 格式

