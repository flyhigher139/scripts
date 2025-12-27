# Mowen Converter

这是一个用于将 Markdown 文档转换为墨问笔记风格的工具。

## 功能

- 将一级、二级标题转换为 `▎ **标题**`
- 将三级标题转换为 `▏ **标题**`
- 自动调整列表缩进和样式
- 优化段落间距

## 安装

在当前目录下运行以下命令进行可编辑安装：

```bash
pip install -e .
```

或者在项目根目录下运行：

```bash
pip install -e tools/mowen-converter
```

### 配置环境变量

如果安装后提示 `command not found`，可能是因为 Python 的脚本目录不在 PATH 环境变量中。请执行以下命令将其添加到 `~/.zshrc`：

```bash
# 将 Python bin 目录添加到 PATH (请根据实际 Python 版本调整路径中的 3.9)
echo 'export PATH="$HOME/Library/Python/3.9/bin:$PATH"' >> ~/.zshrc

# 使配置生效
source ~/.zshrc
```

## 使用

安装完成后，可以使用 `convert-to-mowen` 命令进行转换：

```bash
convert-to-mowen <Markdown文件路径>
```

示例：

```bash
convert-to-mowen ./article.md
```

转换后的文件将在原文件同级目录下生成，文件名后缀为 `-mowen.md`。

## 卸载

如果不再需要该工具，可以使用 pip 进行卸载：

```bash
pip uninstall mowen-converter
```

### 清理环境变量

如果你之前在 `~/.zshrc` 中添加了 PATH 配置，卸载后可以手动移除：

1. 打开配置文件：
   ```bash
   nano ~/.zshrc
   ```
2. 找到并删除包含 `Library/Python/3.9/bin` 的 `export PATH` 行。
3. 保存并退出，然后刷新配置：
   ```bash
   source ~/.zshrc
   ```
