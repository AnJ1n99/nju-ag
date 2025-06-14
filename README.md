# botsh

一个命令行智能助手，支持自然语言交互与Shell命令执行，提供流式输出和交互式对话体验。(项目仍不完善,会根据实际使用情况完善功能)

## 功能



✅ **Shell命令执行**（以`!`开头的命令）

✅ **流式响应输出**

✅ **交互模式(REPL)**

✅ **翻译模式**（支持管道输入）

✅ **跨平台兼容**（支持中文输入编辑）

✅ **智能对话**

## 快速开始

### 环境要求
```bash
pip install -e .
pip install -r requirements.txt
```

### 修改配置

```python
# 修改以下配置：
MODEL_ID = "your-model-id"
ARK_API_KEY = "your-api-key"
ARK_BASE_URL = "your-service-url"
```

### 基本使用

```bash
# 交互模式
ag

# 单次查询
ag "如何查看磁盘使用情况？"

# 翻译模式
ag -t "Hello World"

# 首段对话后进入交互模式
ag -rt "Hello World"
```

## 交互模式功能
1. **自然语言对话**：
   
   ```
   Q: 如何查找大文件？
   A: 可以使用find命令：find /path -type f -size +500M...
   ```
   
2. **执行Shell命令**：
   
   ```
   Q: !ls -l
   A: [显示命令输出]
   ```
   
3. **快捷操作**：
   - `clear`：清空对话历史
   - `exit/quit`：退出程序
   - `Ctrl+C`：中断当前操作

4. **管道：**
```bash
# 翻译gcc --help输出
gcc --help | ag --translate

# 解释说明
gcc --help | ag "gcc应该如何使用"
```

## 致谢

- DeepSeek-R1
- 火山引擎
- OpenAI
