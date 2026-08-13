#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Apple Music 音乐视频下载器
  pip install gamdl
说明：
 - Python 3.10+
 - 已安装 gamdl（pip install gamdl）
 - cookies.txt 必须为 Netscape 格式
 - ffmpeg 若需合并/转封装请安装并放入 PATH，或在界面中指定路径
 - 本脚本不使用 wrapper
"""
import asyncio
import threading
import queue
import traceback
import os
from tkinter import *
from tkinter import ttk, filedialog, messagebox, scrolledtext

try:
    from gamdl.api import AppleMusicApi
    from gamdl.interface import (
        AppleMusicBaseInterface,
        AppleMusicInterface,
        AppleMusicMusicVideoInterface,
        AppleMusicSongInterface,
        AppleMusicUploadedVideoInterface,
    )
    from gamdl.interface.enums import MusicVideoResolution, MusicVideoCodec
    from gamdl.downloader import (
        AppleMusicBaseDownloader,
        AppleMusicDownloader,
        AppleMusicMusicVideoDownloader,
    )
    from gamdl.downloader.enums import RemuxFormatMusicVideo
except Exception as e:
    AppleMusicApi = None
    MusicVideoResolution = None
    RemuxFormatMusicVideo = None
    AppleMusicBaseDownloader = None
    AppleMusicDownloader = None
    AppleMusicBaseInterface = None
    AppleMusicInterface = None
    AppleMusicMusicVideoInterface = None
    AppleMusicSongInterface = None
    AppleMusicUploadedVideoInterface = None
    AppleMusicMusicVideoDownloader = None
    MusicVideoCodec = None
    _IMPORT_ERROR = e
else:
    _IMPORT_ERROR = None


class AMVDownloaderGUI_ZH_Release:
    def __init__(self, root):
        self.root = root
        root.title("Apple Music 音乐视频下载器")
        root.geometry("820x640")

        frm = ttk.Frame(root, padding=10)
        frm.pack(fill=BOTH, expand=True)

        ttk.Label(frm, text="Apple Music 链接（每行一个）：").grid(column=0, row=0, sticky=W)
        self.url_text = scrolledtext.ScrolledText(frm, height=6)
        self.url_text.grid(column=0, row=1, columnspan=4, sticky="nsew", pady=4)

        ttk.Label(frm, text="Cookies 文件（Netscape 格式）：").grid(column=0, row=2, sticky=W, pady=(8,0))
        self.cookies_var = StringVar()
        self.cookies_entry = ttk.Entry(frm, textvariable=self.cookies_var, width=60)
        self.cookies_entry.grid(column=0, row=3, sticky=W)
        ttk.Button(frm, text="浏览...", command=self.browse_cookies).grid(column=1, row=3, sticky=W)

        ttk.Label(frm, text="输出目录：").grid(column=0, row=4, sticky=W, pady=(8,0))
        self.output_var = StringVar(value=os.path.abspath("./Apple Music"))
        self.output_entry = ttk.Entry(frm, textvariable=self.output_var, width=60)
        self.output_entry.grid(column=0, row=5, sticky=W)
        ttk.Button(frm, text="浏览...", command=self.browse_output).grid(column=1, row=5, sticky=W)

        ttk.Label(frm, text="FFmpeg 可执行文件（可选）：").grid(column=0, row=6, sticky=W, pady=(8,0))
        self.ffmpeg_var = StringVar(value="ffmpeg")
        self.ffmpeg_entry = ttk.Entry(frm, textvariable=self.ffmpeg_var, width=60)
        self.ffmpeg_entry.grid(column=0, row=7, sticky=W)
        ttk.Button(frm, text="浏览...", command=self.browse_ffmpeg).grid(column=1, row=7, sticky=W)

        ttk.Label(frm, text="视频分辨率：").grid(column=0, row=8, sticky=W, pady=(8,0))
        self.res_combo = ttk.Combobox(frm, state="readonly", width=20)
        self.res_options = self._get_resolution_options()
        self.res_combo['values'] = [label for label, _ in self.res_options]
        self.res_combo.current(self._default_res_index())
        self.res_combo.grid(column=0, row=9, sticky=W)

        ttk.Label(frm, text="封装格式：").grid(column=1, row=8, sticky=W, pady=(8,0))
        self.format_combo = ttk.Combobox(frm, state="readonly", width=12)
        self.format_combo['values'] = ["m4v", "mp4"]
        self.format_combo.current(0)
        self.format_combo.grid(column=1, row=9, sticky=W)

        ttk.Label(frm, text="视频编码优先（可选）：").grid(column=2, row=8, sticky=W, pady=(8,0))
        self.codec_combo = ttk.Combobox(frm, state="readonly", width=12)
        self.codec_combo['values'] = ["h264,h265", "h264", "h265"]
        self.codec_combo.current(0)
        self.codec_combo.grid(column=2, row=9, sticky=W)

        self.save_cover_var = BooleanVar(value=True)
        self.save_cover_cb = ttk.Checkbutton(frm, text="保存封面（另存为单独文件）", variable=self.save_cover_var)
        self.save_cover_cb.grid(column=0, row=10, sticky=W, pady=(10,0))

        self.start_btn = ttk.Button(frm, text="开始下载", command=self.start_download)
        self.start_btn.grid(column=0, row=11, sticky=W, pady=(12,0))
        self.stop_btn = ttk.Button(frm, text="停止", command=self.stop_download, state=DISABLED)
        self.stop_btn.grid(column=1, row=11, sticky=W, pady=(12,0))

        self.status_var = StringVar(value="准备就绪")
        ttk.Label(frm, textvariable=self.status_var).grid(column=0, row=12, columnspan=3, sticky=W, pady=(8,0))

        ttk.Label(frm, text="日志：").grid(column=0, row=13, sticky=W, pady=(8,0))
        self.log_text = scrolledtext.ScrolledText(frm, height=18, state=DISABLED)
        self.log_text.grid(column=0, row=14, columnspan=4, sticky="nsew", pady=(4,0))

        frm.rowconfigure(14, weight=1)
        frm.columnconfigure(3, weight=1)

        self.log_queue = queue.Queue()
        self.worker_thread = None
        self._stop_event = threading.Event()
        self.root.after(200, self._poll_log_queue)

        if _IMPORT_ERROR is not None:
            self._log("错误：无法导入 gamdl 库，请先运行: pip install gamdl")
            self._log(f"导入错误详情：{_IMPORT_ERROR}")

    def _get_resolution_options(self):
        if MusicVideoResolution is None:
            return [("1080p", "1080p"), ("720p", "720p"), ("480p", "480p")]
        opts = [
            ("2160p (4K)", MusicVideoResolution.R2160P),
            ("1440p", MusicVideoResolution.R1440P),
            ("1080p", MusicVideoResolution.R1080P),
            ("720p", MusicVideoResolution.R720P),
            ("540p", MusicVideoResolution.R540P),
            ("480p", MusicVideoResolution.R480P),
            ("360p", MusicVideoResolution.R360P),
            ("240p", MusicVideoResolution.R240P),
        ]
        return opts

    def _default_res_index(self):
        for i, (_, val) in enumerate(self.res_options):
            if (hasattr(val, "value") and val.value == "1080p") or val == "1080p":
                return i
        return 0

    def browse_cookies(self):
        p = filedialog.askopenfilename(title="选择 cookies.txt（Netscape）", filetypes=[("Cookies 文件", "*.txt;*.cookies;*.*")])
        if p:
            self.cookies_var.set(p)

    def browse_output(self):
        p = filedialog.askdirectory(title="选择输出目录")
        if p:
            self.output_var.set(p)

    def browse_ffmpeg(self):
        p = filedialog.askopenfilename(title="选择 ffmpeg 可执行文件", filetypes=[("可执行文件", "*.exe;*")])
        if p:
            self.ffmpeg_var.set(p)

    def _log(self, msg: str):
        self.log_queue.put(msg)

    def _poll_log_queue(self):
        try:
            while True:
                msg = self.log_queue.get_nowait()
                self.log_text.configure(state=NORMAL)
                self.log_text.insert(END, msg + "\n")
                self.log_text.see(END)
                self.log_text.configure(state=DISABLED)
        except queue.Empty:
            pass
        self.root.after(200, self._poll_log_queue)

    def start_download(self):
        if _IMPORT_ERROR is not None:
            messagebox.showerror("缺少依赖", "未安装 gamdl，请运行: pip install gamdl")
            return

        urls_raw = self.url_text.get("1.0", END).strip()
        if not urls_raw:
            messagebox.showwarning("未输入链接", "请粘贴至少一个 Apple Music 链接。")
            return
        urls = [line.strip() for line in urls_raw.splitlines() if line.strip()]

        cookies_path = self.cookies_var.get().strip()
        if not cookies_path or not os.path.isfile(cookies_path):
            messagebox.showwarning("Cookies 缺失", "请选择有效的 cookies 文件（Netscape 格式）。")
            return

        output_path = self.output_var.get().strip()
        if not output_path:
            messagebox.showwarning("输出缺失", "请选择输出目录。")
            return

        ffmpeg_path = self.ffmpeg_var.get().strip() or "ffmpeg"
        resolution_label, resolution_val = self.res_options[self.res_combo.current()]
        format_choice = self.format_combo.get()
        codec_choice = self.codec_combo.get()
        save_cover = self.save_cover_var.get()

        worker_args = {
            "urls": urls,
            "cookies_path": cookies_path,
            "output_path": output_path,
            "ffmpeg_path": ffmpeg_path,
            "resolution_val": resolution_val,
            "format_choice": format_choice,
            "codec_choice": codec_choice,
            "save_cover": save_cover,
        }

        self.start_btn.config(state=DISABLED)
        self.stop_btn.config(state=NORMAL)
        self.status_var.set("正在启动下载...")
        self._stop_event.clear()

        self.worker_thread = threading.Thread(target=self._run_worker_thread, args=(worker_args,), daemon=True)
        self.worker_thread.start()

    def stop_download(self):
        self._log("收到停止请求，正在停止...")
        self._stop_event.set()
        self.stop_btn.config(state=DISABLED)
        self.status_var.set("正在停止...")

    def _run_worker_thread(self, args):
        try:
            asyncio.run(self._async_worker(args))
        except Exception:
            self._log("后台任务异常：")
            self._log(traceback.format_exc())
        finally:
            self.root.after(0, self._worker_finished_ui)

    def _worker_finished_ui(self):
        self.start_btn.config(state=NORMAL)
        self.stop_btn.config(state=DISABLED)
        self.status_var.set("准备就绪")

    async def _async_worker(self, args):
        urls = args["urls"]
        cookies_path = args["cookies_path"]
        output_path = args["output_path"]
        ffmpeg_path = args["ffmpeg_path"]
        resolution_val = args["resolution_val"]
        format_choice = args["format_choice"]
        codec_choice = args["codec_choice"]
        save_cover = args["save_cover"]

        def check_stop():
            return self._stop_event.is_set()

        self._log(f"输出目录：{output_path}")
        self._log(f"Cookies：{cookies_path}")
        self._log(f"FFmpeg：{ffmpeg_path}")

        try:
            apple_music_api = await AppleMusicApi.create_from_netscape_cookies(cookies_path=cookies_path)
        except Exception as e:
            self._log(f"创建 AppleMusicApi 失败：{e}")
            self._log(traceback.format_exc())
            return

        if not apple_music_api.active_subscription:
            self._log("未检测到活跃的 Apple Music 订阅，无法下载。")
            return

        try:
            base_interface = await AppleMusicBaseInterface.create(apple_music_api=apple_music_api)
            song_interface = AppleMusicSongInterface(base=base_interface)
            uploaded_interface = AppleMusicUploadedVideoInterface(base=base_interface)
            resolution_enum = resolution_val if hasattr(resolution_val, "value") else MusicVideoResolution.R1080P
            music_video_interface = AppleMusicMusicVideoInterface(base=base_interface, resolution=resolution_enum)
            interface = AppleMusicInterface(song=song_interface, music_video=music_video_interface, uploaded_video=uploaded_interface)
        except Exception as e:
            self._log(f"初始化接口失败：{e}")
            self._log(traceback.format_exc())
            return

        preferred_temp = None
        try:
            if os.name == 'nt':
                preferred_temp = r"C:\gamdl_temp"
            else:
                preferred_temp = "/tmp/gamdl_temp"
            os.makedirs(preferred_temp, exist_ok=True)
        except Exception:
            try:
                preferred_temp = os.path.join(os.path.abspath(output_path), "gamdl_temp")
                os.makedirs(preferred_temp, exist_ok=True)
            except Exception:
                preferred_temp = None

        temp_path_arg = preferred_temp if preferred_temp else "."
        # 正式版：减少底层噪声（silent=True），并使用自动清理（skip_cleanup=False）
        base_downloader = AppleMusicBaseDownloader(
            interface=interface,
            output_path=output_path,
            ffmpeg_path=ffmpeg_path,
            temp_path=temp_path_arg,
            silent=True,
        )
        mv_remux = RemuxFormatMusicVideo.M4V if format_choice.lower() == "m4v" else RemuxFormatMusicVideo.MP4
        music_video_downloader = AppleMusicMusicVideoDownloader(base=base_downloader, remux_format=mv_remux)

        from gamdl.downloader.song import AppleMusicSongDownloader
        from gamdl.downloader.uploaded_video import AppleMusicUploadedVideoDownloader

        song_downloader = AppleMusicSongDownloader(base=base_downloader)
        uploaded_downloader = AppleMusicUploadedVideoDownloader(base=base_downloader)

        downloader = AppleMusicDownloader(
            song=song_downloader,
            music_video=music_video_downloader,
            uploaded_video=uploaded_downloader,
            save_cover=bool(save_cover),
            skip_cleanup=False,
        )

        requested_codecs = [c.strip() for c in codec_choice.split(",") if c.strip()]
        codec_priority = []
        for c in requested_codecs:
            if MusicVideoCodec and c.lower() == "h264":
                codec_priority.append(MusicVideoCodec.H264)
            elif MusicVideoCodec and c.lower() == "h265":
                codec_priority.append(MusicVideoCodec.H265)
        if codec_priority:
            music_video_interface.codec_priority = codec_priority

        for idx, url in enumerate(urls, start=1):
            if check_stop():
                break
            self._log(f"[{idx}/{len(urls)}] 处理链接：{url}")
            try:
                async for download_item in downloader.get_download_item_from_url(url):
                    if check_stop():
                        break
                    if download_item.media and download_item.media.error:
                        self._log(f"资源错误：{download_item.media.error}")
                        continue
                    if download_item.media and download_item.media.partial:
                        self._log("资源不完整（partial），跳过。")
                        continue
                    self._log(f"开始下载：{download_item.final_path or '未知文件'}")
                    try:
                        await downloader.download(download_item)
                        self._log(f"完成：{download_item.final_path}")
                    except Exception as e:
                        self._log(f"下载失败：{e}")
                        self._log(traceback.format_exc())
            except Exception as e:
                self._log(f"解析链接或获取资源失败：{e}")
                self._log(traceback.format_exc())

        self._log("所有任务结束。")

def main():
    root = Tk()
    app = AMVDownloaderGUI_ZH_Release(root)
    root.mainloop()

if __name__ == "__main__":
    main()