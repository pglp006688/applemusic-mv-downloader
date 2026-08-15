#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新增功能：播放列表内 MV 一键下载（前提：播放列表包含 MV）
"""
import asyncio
import threading
import queue
import traceback
import os
from tkinter import *
from tkinter import ttk, filedialog, messagebox, simpledialog, scrolledtext

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


class AMVDownloaderGUI_ZH:
    def __init__(self, root):
        self.root = root
        root.title("Apple Music 音乐视频下载器")
        root.geometry("960x760")

        frm = ttk.Frame(root, padding=10)
        frm.pack(fill=BOTH, expand=True)

        ttk.Label(frm, text="Apple Music 链接（每行一个，可放歌/专辑/艺人/播放列表链接）：").grid(column=0, row=0, sticky=W)
        self.url_text = scrolledtext.ScrolledText(frm, height=6)
        self.url_text.grid(column=0, row=1, columnspan=6, sticky="nsew", pady=4)

        ttk.Label(frm, text="Cookies 文件（Netscape 格式）：").grid(column=0, row=2, sticky=W, pady=(8,0))
        self.cookies_var = StringVar()
        self.cookies_entry = ttk.Entry(frm, textvariable=self.cookies_var, width=68)
        self.cookies_entry.grid(column=0, row=3, sticky=W)
        ttk.Button(frm, text="浏览...", command=self.browse_cookies).grid(column=1, row=3, sticky=W)

        ttk.Label(frm, text="输出目录：").grid(column=0, row=4, sticky=W, pady=(8,0))
        self.output_var = StringVar(value=os.path.abspath("./Apple Music"))
        self.output_entry = ttk.Entry(frm, textvariable=self.output_var, width=68)
        self.output_entry.grid(column=0, row=5, sticky=W)
        ttk.Button(frm, text="浏览...", command=self.browse_output).grid(column=1, row=5, sticky=W)

        ttk.Label(frm, text="FFmpeg 可执行文件（可选）：").grid(column=0, row=6, sticky=W, pady=(8,0))
        self.ffmpeg_var = StringVar(value="ffmpeg")
        self.ffmpeg_entry = ttk.Entry(frm, textvariable=self.ffmpeg_var, width=68)
        self.ffmpeg_entry.grid(column=0, row=7, sticky=W)
        ttk.Button(frm, text="浏览...", command=self.browse_ffmpeg).grid(column=1, row=7, sticky=W)

        ttk.Label(frm, text="视频分辨率：").grid(column=0, row=8, sticky=W, pady=(8,0))
        self.res_combo = ttk.Combobox(frm, state="readonly", width=24)
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
        self.codec_combo = ttk.Combobox(frm, state="readonly", width=14)
        self.codec_combo['values'] = ["h264,h265", "h264", "h265"]
        self.codec_combo.current(0)
        self.codec_combo.grid(column=2, row=9, sticky=W)

        # 保存封面 与 覆盖复选框
        self.save_cover_var = BooleanVar(value=True)
        self.save_cover_cb = ttk.Checkbutton(frm, text="保存封面（另存为单独文件）", variable=self.save_cover_var)
        self.save_cover_cb.grid(column=0, row=10, sticky=W, pady=(10,0))

        self.overwrite_var = BooleanVar(value=False)
        self.overwrite_cb = ttk.Checkbutton(frm, text="覆盖已有文件（全局）", variable=self.overwrite_var)
        self.overwrite_cb.grid(column=1, row=10, sticky=W, pady=(10,0))

        # 下载按钮与艺人/专辑/播放列表一键下载按钮
        self.start_btn = ttk.Button(frm, text="开始下载", command=self.start_download)
        self.start_btn.grid(column=0, row=11, sticky=W, pady=(12,0))

        self.artist_btn = ttk.Button(frm, text="下载艺人全部MV", command=self.start_download_artist)
        self.artist_btn.grid(column=1, row=11, sticky=W, padx=(8,0), pady=(12,0))

        self.album_btn = ttk.Button(frm, text="专辑内MV一键下载", command=self.start_download_album)
        self.album_btn.grid(column=2, row=11, sticky=W, padx=(8,0), pady=(12,0))

        self.playlist_btn = ttk.Button(frm, text="播放列表内MV一键下载", command=self.start_download_playlist)
        self.playlist_btn.grid(column=3, row=11, sticky=W, padx=(8,0), pady=(12,0))

        self.stop_btn = ttk.Button(frm, text="停止", command=self.stop_download, state=DISABLED)
        self.stop_btn.grid(column=4, row=11, sticky=W, padx=(8,0), pady=(12,0))

        self.status_var = StringVar(value="准备就绪")
        ttk.Label(frm, textvariable=self.status_var).grid(column=0, row=12, columnspan=5, sticky=W, pady=(8,0))

        ttk.Label(frm, text="日志：").grid(column=0, row=13, sticky=W, pady=(8,0))
        self.log_text = scrolledtext.ScrolledText(frm, height=20, state=DISABLED)
        self.log_text.grid(column=0, row=14, columnspan=6, sticky="nsew", pady=(4,0))

        frm.rowconfigure(14, weight=1)
        frm.columnconfigure(5, weight=1)

        # 后台控制
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

    # ---------- 启动/停止逻辑 ----------
    def start_download(self):
        self._start_worker_with_mode(mode="normal")

    def start_download_artist(self):
        default = self._get_first_url_or_empty()
        url = simpledialog.askstring("艺人全部MV下载", "请输入艺人页面 URL（或留空使用文本框第一行）:", initialvalue=default)
        if not url:
            if default:
                url = default
            else:
                messagebox.showwarning("未输入 URL", "请在文本框或输入框中提供艺人页面 URL。")
                return
        self._start_worker_with_mode(mode="artist", single_url=url)

    def start_download_album(self):
        default = self._get_first_url_or_empty()
        url = simpledialog.askstring("专辑内MV一键下载", "请输入专辑页面 URL（或留空使用文本框第一行）:", initialvalue=default)
        if not url:
            if default:
                url = default
            else:
                messagebox.showwarning("未输入 URL", "请在文本框或输入框中提供专辑页面 URL。")
                return
        self._start_worker_with_mode(mode="album", single_url=url)

    def start_download_playlist(self):
        default = self._get_first_url_or_empty()
        url = simpledialog.askstring("播放列表内MV一键下载", "请输入播放列表页面 URL（或留空使用文本框第一行）:", initialvalue=default)
        if not url:
            if default:
                url = default
            else:
                messagebox.showwarning("未输入 URL", "请在文本框或输入框中提供播放列表页面 URL。")
                return
        self._start_worker_with_mode(mode="playlist", single_url=url)

    def _get_first_url_or_empty(self):
        urls_raw = self.url_text.get("1.0", END).strip()
        if not urls_raw:
            return ""
        for line in urls_raw.splitlines():
            s = line.strip()
            if s:
                return s
        return ""

    def _start_worker_with_mode(self, mode="normal", single_url: str | None = None):
        if _IMPORT_ERROR is not None:
            messagebox.showerror("缺少依赖", "未安装 gamdl，请运行: pip install gamdl")
            return

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
        overwrite = self.overwrite_var.get()

        urls_raw = self.url_text.get("1.0", END).strip()
        urls = [line.strip() for line in urls_raw.splitlines() if line.strip()]

        worker_args = {
            "mode": mode,
            "single_url": single_url,
            "urls": urls,
            "cookies_path": cookies_path,
            "output_path": output_path,
            "ffmpeg_path": ffmpeg_path,
            "resolution_val": resolution_val,
            "format_choice": format_choice,
            "codec_choice": codec_choice,
            "save_cover": save_cover,
            "overwrite": overwrite,
        }

        # 禁用启动按钮
        self._set_buttons_state(start_disabled=True)
        self.stop_btn.config(state=NORMAL)
        self.status_var.set("正在启动下载...")
        self._stop_event.clear()

        self.worker_thread = threading.Thread(target=self._run_worker_thread, args=(worker_args,), daemon=True)
        self.worker_thread.start()

    def _set_buttons_state(self, start_disabled: bool):
        state = DISABLED if start_disabled else NORMAL
        self.start_btn.config(state=state)
        self.artist_btn.config(state=state)
        self.album_btn.config(state=state)
        self.playlist_btn.config(state=state)

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
        self._set_buttons_state(start_disabled=False)
        self.stop_btn.config(state=DISABLED)
        self.status_var.set("准备就绪")

    # ---------- 主线程弹窗协助函数 ----------
    def _ask_overwrite_sync(self, path, result_container, event):
        """在主线程中弹窗询问是否覆盖，结果放入 result_container['res']，并设置 event。"""
        try:
            title = "目标文件已存在"
            msg = f"目标文件已存在：\n{path}\n是否覆盖？\n\n选择“是”将覆盖该文件；选择“否”将跳过该文件。"
            res = messagebox.askyesno(title, msg)
            result_container['res'] = res
        except Exception:
            result_container['res'] = False
        finally:
            event.set()

    async def _ask_overwrite(self, path):
        """从异步任务调用以在主线程弹窗并异步等待结果（返回 True/False）。"""
        event = threading.Event()
        result = {}
        self.root.after(0, self._ask_overwrite_sync, path, result, event)
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, event.wait)
        return bool(result.get('res', False))

    # ---------- 异步下载主逻辑 ----------
    async def _async_worker(self, args):
        mode = args.get("mode", "normal")
        single_url = args.get("single_url")
        urls = args.get("urls", [])
        cookies_path = args["cookies_path"]
        output_path = args["output_path"]
        ffmpeg_path = args["ffmpeg_path"]
        resolution_val = args["resolution_val"]
        format_choice = args["format_choice"]
        codec_choice = args["codec_choice"]
        save_cover = args["save_cover"]
        global_overwrite = args["overwrite"]

        def check_stop():
            return self._stop_event.is_set()

        self._log(f"输出目录：{output_path}")
        self._log(f"Cookies：{cookies_path}")
        self._log(f"FFmpeg：{ffmpeg_path}")
        self._log(f"保存封面（另存为文件）：{'是' if save_cover else '否'}")
        self._log(f"覆盖已有文件（全局）：{'是' if global_overwrite else '否'}")
        self._log(f"任务模式：{mode}")

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

        # 临时目录策略
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
            overwrite=bool(global_overwrite),
            skip_cleanup=False,
        )

        # codec priority
        requested_codecs = [c.strip() for c in codec_choice.split(",") if c.strip()]
        codec_priority = []
        for c in requested_codecs:
            if MusicVideoCodec and c.lower() == "h264":
                codec_priority.append(MusicVideoCodec.H264)
            elif MusicVideoCodec and c.lower() == "h265":
                codec_priority.append(MusicVideoCodec.H265)
        if codec_priority:
            music_video_interface.codec_priority = codec_priority

        # build target URL list according to mode
        target_urls = []
        if mode == "normal":
            target_urls = urls
        elif mode in ("artist", "album", "playlist"):
            if not single_url:
                self._log("未提供 URL，已取消任务。")
                return
            target_urls = [single_url]

        # iterate and download
        for idx, turl in enumerate(target_urls, start=1):
            if check_stop():
                self._log("检测到停止请求，退出中...")
                break
            self._log(f"[{idx}/{len(target_urls)}] 处理链接：{turl} （模式：{mode}）")
            try:
                async for download_item in downloader.get_download_item_from_url(turl):
                    if check_stop():
                        break
                    if download_item.media and download_item.media.error:
                        self._log(f"资源错误：{download_item.media.error}")
                        continue
                    if download_item.media and download_item.media.partial:
                        self._log("资源不完整（partial），跳过。")
                        continue

                    media_type = None
                    if download_item.media and download_item.media.media_metadata:
                        media_type = download_item.media.media_metadata.get("type")

                    # 对 artist/album/playlist 模式仅下载 MV 条目
                    if mode in ("artist", "album", "playlist"):
                        if media_type not in {"music-videos", "library-music-videos"}:
                            # 不是 MV，跳过
                            continue

                    final_path = getattr(download_item, "final_path", None)
                    per_item_overwrite = False
                    if final_path and os.path.exists(final_path) and not global_overwrite:
                        self._log(f"检测到目标文件已存在：{final_path}")
                        try:
                            user_choice = await self._ask_overwrite(final_path)
                        except Exception:
                            user_choice = False
                        if not user_choice:
                            self._log("用户选择跳过已存在文件。")
                            continue
                        else:
                            self._log("用户选择覆盖该文件（仅针对当前条目）。")
                            per_item_overwrite = True

                    self._log(f"开始下载：{final_path or '未知文件'}")
                    try:
                        prev_overwrite = downloader.overwrite
                        if per_item_overwrite:
                            downloader.overwrite = True
                        await downloader.download(download_item)
                        downloader.overwrite = prev_overwrite
                        self._log(f"完成：{final_path}")
                    except Exception as e:
                        try:
                            downloader.overwrite = prev_overwrite
                        except Exception:
                            pass
                        self._log(f"下载失败：{e}")
                        self._log(traceback.format_exc())
            except Exception as e:
                self._log(f"解析链接或获取资源失败：{e}")
                self._log(traceback.format_exc())

        self._log("所有任务结束。")
        if preferred_temp:
            self._log(f"临时目录：{preferred_temp}（如稳定建议加入杀软白名单）")


def main():
    root = Tk()
    app = AMVDownloaderGUI_ZH(root)
    root.mainloop()


if __name__ == "__main__":
    main()