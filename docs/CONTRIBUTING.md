# 贡献指南

感谢您对 CRX Toolkit 项目的关注！我们欢迎各种形式的贡献，包括但不限于：

- 报告问题
- 提交功能建议
- 改进文档
- 提交代码修复
- 添加新功能

## 开发流程

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 提交规范

### 分支命名

- 功能分支：`feature/功能名称`
- 修复分支：`fix/问题描述`
- 文档分支：`docs/文档描述`

### 提交信息

```
<type>(<scope>): <subject>

<body>
```

type 类型：
- feat: 新功能
- fix: 修复
- docs: 文档
- style: 格式
- refactor: 重构
- test: 测试
- chore: 构建/工具

### 代码规范

- 遵循 PEP 8
- 添加类型注解
- 编写测试用例
- 更新文档

## 开发环境设置

1. 克隆项目：
```bash
git clone https://github.com/yourusername/crx-toolkit.git
cd crx-toolkit
```

2. 创建虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

## 测试

运行测试：
```bash
python -m pytest
```

## 文档

更新文档：
1. 修改相关 .md 文件
2. 确保示例代码可运行
3. 检查文档格式

## 问题反馈

创建 Issue 时请包含：

- 问题描述
- 复现步骤
- 期望行为
- 实际行为
- 环境信息

## 联系方式

如有问题，请通过以下方式联系：

- Issue: [GitHub Issues](https://github.com/bineanzhou/crx-toolkit/issues)
- Email: bineanzhou@gmail.com 