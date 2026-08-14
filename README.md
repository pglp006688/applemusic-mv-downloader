# applemusic-mv-downloader
一个图形化的Apple Music音乐视频下载工具，基于[gamdl](https://github.com/glomatico/gamdl) 开发，
提供可视化界面，提供分辨率 / 编码 / 封装格式选择、封面另存、等常用功能。

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)

> **重要说明**：此工具只是对 gamdl 的 GUI 封装，不包含绕过授权或规避付费保护的功能。下载 Apple Music 内容请遵守当地法律与 Apple 服务条款，且须使用已登录并有有效 Apple Music 订阅的账户（通过 Cookies 登录）。
## 目录

- [功能概述](#功能概述)
- [配置](#配置)
- [快速开始](#快速开始)
- [界面说明](#界面说明)
- [常见问题](#常见问题)
- [隐私与安全](#隐私与安全)
- [致谢](#致谢)
- [许可证](#许可证)

---

## 功能概述

- 支持单条或多条 Apple Music 链接（逐行输入）。
- 支持专辑/歌手一键全部下载
- 支持选择视频分辨率、视频编码优先顺序（h264 / h265）与输出封装格式（m4v / mp4）。
- 支持指定 ffmpeg 可执行文件路径（若需要转封装）。
- 支持将封面另存为单独文件（同时 gamdl 默认也会把封面嵌入到媒体标签中）。
- 临时目录策略（优先短路径以降低 Windows 下碎片写入失败风险）。
- 自动日志输出到 GUI 日志窗，便于查看错误与进度信息。

---

## 配置

- **Python 3.10** 或更高版本
- 有效的 **Apple Music 订阅**账户
- 浏览器导出的 Apple Music Cookies（**Netscape 格式**，通常文件名为 `cookies.txt`）
- 安装 **gamdl** Python 包：`pip install gamdl`
- **可选**：**ffmpeg**（若需要 转封装 / 某些解密过程），将 ffmpeg 放入系统 PATH 或在界面中指定其可执行路径
- **可选但建议**：安装最新版 **yt-dlp**（gamdl 内部使用时会调用）：
  ```bash
  pip install yt-dlp

> **Windows 注意**：若你的输出目录或临时目录位于 OneDrive 等同步盘上，强烈建议把临时目录改为本地短路径（脚本默认优先使用 `C:\gamdl_temp` ）并将该目录加入防病毒 / 同步工具的排除列表，以避免片段文件被自动删除或锁定导致下载失败。

## 快速开始

- 1.将本项目克隆
  ```bash
  git clone https://github.com/pglp006688/applemusic-mv-downloader.git
  cd applemusic-mv-downloader
  ```
- 2.在终端运行程序（需安装好依赖）
  ```bash
  python amv_downloader_gui.py
  ```
  
## 界面说明

- Apple Music 链接：每行一条 URL，可批量。

- Cookies 文件：选择 Netscape 格式 cookies.txt（必需）。

- 输出目录：最终保存媒体文件的位置。

- FFmpeg：可选项，若不提供则使用系统 PATH 中的 ffmpeg（如有）。

- 视频分辨率：选择所需的最高分辨率（脚本会尝试按优先级选择）。

- 封装格式：m4v 或 mp4（m4v 保留某些 Apple 特性）。

- 视频编码优先：可指定 h264 / h265 优先顺序。

- 保存封面：是否把封面另存为单独文件（Cover.jpg / Cover.png）。

- 开始下载 / 停止：控制下载任务。


## 常见问题

- **Q: 下载后文件很小（例如 ~50KB），不是视频。**
- **A: 通常表示下载不完整（yt-dlp 在合并或写入片段时失败），可以试一试 *gamdl* 原版**

- **Q: 为什么有时会出现“Requested format is not available”？**
- **A: 所请求的编码或分辨率在该媒体上不可用。请调整视频编码优先或降低分辨率。**

## 隐私与安全

- **本工具通过用户提供的 Cookies 文件登录 Apple Music； Cookies 包含敏感信息，请妥善保管，不要随意泄露。建议仅在受信任的本地环境下使用。**

- **请勿将 Cookies 上传到公共网络或第三方服务。脚本不会主动将 Cookies 或下载的内容上传或发送到远程服务器。**

## 致谢

- 本 GUI 脚本为对开源项目 gamdl（作者 glomatico）功能的封装。gamdl 为原始下载、流解析与解密逻辑提供核心能力（请参考 gamdl 仓库与文档以获取更多实现细节）。

- 本脚本使用并依赖于第三方开源组件（gamdl、yt-dlp、ffmpeg 等），请遵守各自许可证与条款。

## 许可证

本 GUI 脚本（README 所描述的项目）采用 MIT 许可证。

你可以自由使用、修改、分发，但需保留版权声明和许可声明。

pglp006688 By
