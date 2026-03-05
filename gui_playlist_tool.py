import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import re
import time
import random
import json
import requests
from params_encSecKey import Netease_params

class PlaylistToolGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("网易云歌单工具")
        self.root.geometry("900x700")
        
        self.setup_ui()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        ttk.Label(main_frame, text="网易云歌单链接:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.link_entry = ttk.Entry(main_frame, width=60)
        self.link_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        self.link_entry.insert(0, "https://music.163.com/playlist?id=6940665039")
        
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        self.process_button = ttk.Button(button_frame, text="开始处理", command=self.start_processing)
        self.process_button.pack(side=tk.LEFT, padx=5)
        
        self.save_button = ttk.Button(button_frame, text="保存报告", command=self.save_report, state=tk.DISABLED)
        self.save_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_button = ttk.Button(button_frame, text="清空", command=self.clear_output)
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(main_frame, text="处理状态:").grid(row=2, column=0, sticky=tk.W, pady=5)
        
        self.progress = ttk.Progressbar(main_frame, mode='determinate')
        self.progress.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        ttk.Label(main_frame, text="搜索报告:").grid(row=3, column=0, sticky=(tk.W, tk.N), pady=5)
        
        self.output_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, width=80, height=25)
        self.output_text.grid(row=3, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5, padx=5)
        
        self.report_data = None
        
    def log(self, message):
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)
        self.root.update()
        
    def clear_output(self):
        self.output_text.delete(1.0, tk.END)
        self.report_data = None
        self.save_button.config(state=tk.DISABLED)
        self.progress['value'] = 0
        
    def search_bilibili_video(self, keyword):
        try:
            url = "https://api.bilibili.com/x/web-interface/search/type"
            params = {
                "keyword": keyword,
                "search_type": "video",
                "page": 1,
                "limit": 5
            }
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
            ]
            headers = {
                "User-Agent": random.choice(user_agents),
                "Referer": "https://www.bilibili.com/",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache"
            }
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if data.get('code') == 0:
                result = data.get('data', {})
                items = result.get('result', [])
                if items:
                    for item in items:
                        if isinstance(item, dict):
                            bvid = item.get('bvid')
                            if bvid:
                                video_url = f"https://www.bilibili.com/video/{bvid}"
                                return bvid, video_url
                return None, "未找到相关视频"
            else:
                return None, f"搜索失败: {data.get('message', '未知错误')}"
        except Exception as e:
            return None, f"B站搜索错误: {e}"
    
    def get_playlist_info(self, playlist_url):
        match = re.search(r'playlist\?id=(\d+)', playlist_url)
        if not match:
            self.log("无法从URL中提取歌单ID")
            return None
        
        playlist_id = match.group(1)
        self.log(f"获取歌单ID: {playlist_id}")
        
        try:
            time.sleep(1)
            playlist_api = 'https://music.163.com/weapi/v6/playlist/detail?'
            data = {
                'csrf_token': "",
                'id': str(playlist_id),
                'n': "0"
            }
            wyy_params = Netease_params(data)
            response = wyy_params.run(playlist_api)
            
            if response.get('code') != 200:
                self.log(f"API请求失败: {response.get('message', '未知错误')}")
                return None
            
            playlist = response['playlist']
            playlist_name = playlist.get('name', '未知歌单')
            track_count = playlist.get('trackCount', 0)
            
            self.log(f"\n歌单名称: {playlist_name}")
            self.log(f"歌曲数量: {track_count}")
            self.log("\n歌曲列表:")
            self.log("-" * 80)
            
            id_list = [i['id'] for i in playlist['trackIds']]
            c = [{'id': i} for i in id_list]
            
            time.sleep(1)
            song_api = 'https://music.163.com/weapi/v3/song/detail'
            song_data = {
                'c': str(c),
                'csrf_token': ''
            }
            song_params = Netease_params(song_data)
            song_response = song_params.run(song_api)
            
            if song_response.get('code') != 200:
                self.log(f"获取歌曲信息失败: {song_response.get('message', '未知错误')}")
                return None
            
            songs = song_response['songs']
            output_data = []
            failed_searches = []
            success_count = 0
            fail_count = 0
            
            self.progress['maximum'] = len(songs)
            current_task = 0
            
            for i, song in enumerate(songs, 1):
                current_task += 1
                self.progress['value'] = current_task
                self.root.update()
                
                song_name = song.get('name', '未知歌曲')
                artists = song.get('ar', [])
                artist_names = [artist.get('name', '未知歌手') for artist in artists]
                artist_str = ' / '.join(artist_names)
                
                search_keyword = f"{song_name} {artist_str}"
                bvid, video_url = self.search_bilibili_video(search_keyword)
                
                self.log(f"{i}. {song_name} - {artist_str}")
                self.log(f"   B站视频: {video_url}")
                
                if bvid:
                    success_count += 1
                else:
                    fail_count += 1
                    failed_searches.append({
                        'index': i,
                        'song_name': song_name,
                        'artists': artist_str,
                        'search_keyword': search_keyword
                    })
                
                output_data.append({
                    'index': i,
                    'song_name': song_name,
                    'artists': artist_str,
                    'bilibili_url': video_url
                })
                
                time.sleep(random.uniform(3, 5))
            
            if failed_searches:
                self.progress['maximum'] = len(songs) + len(failed_searches)
                self.log("\n进行重复搜索...")
                for item in failed_searches:
                    current_task += 1
                    self.progress['value'] = current_task
                    self.root.update()
                    
                    self.log(f"重新搜索: {item['song_name']} - {item['artists']}")
                    
                    song_name = item['song_name']
                    artists = item['artists']
                    
                    order_options = [
                        (song_name, artists),
                        (artists, song_name)
                    ]
                    
                    bracket_options = [
                        lambda x: x,
                        lambda x: f"《{x}》"
                    ]
                    
                    suffix_options = [
                        "",
                        " mv",
                        " 纯享"
                    ]
                    
                    hyphen_options = [
                        lambda x: x,
                        lambda x: x.replace(" - ", " ")
                    ]
                    
                    keywords = []
                    for order in order_options:
                        for bracket in bracket_options:
                            for suffix in suffix_options:
                                for hyphen in hyphen_options:
                                    part1 = hyphen(bracket(order[0]))
                                    part2 = hyphen(order[1])
                                    keyword = f"{part1} {part2}{suffix}"
                                    if keyword not in keywords:
                                        keywords.append(keyword)
                    
                    success = False
                    final_url = "搜索失败"
                    
                    for keyword in keywords:
                        if not keyword:
                            continue
                        
                        self.log(f"   尝试关键词: {keyword}")
                        bvid, video_url = self.search_bilibili_video(keyword)
                        
                        if bvid:
                            final_url = video_url
                            success = True
                            break
                        
                        time.sleep(random.uniform(3, 5))
                    
                    for data_item in output_data:
                        if data_item['index'] == item['index']:
                            data_item['bilibili_url'] = final_url
                            if 'https://' in final_url:
                                success_count += 1
                                fail_count -= 1
                            break
                    
                    self.log(f"   最终搜索结果: {final_url}")

                    
                    time.sleep(random.uniform(3, 5))
            
            self.log("-" * 80)
            self.log(f"共 {len(songs)} 首歌曲")
            self.log(f"搜索成功: {success_count} 首")
            self.log(f"搜索失败: {fail_count} 首")
            
            self.report_data = {
                'playlist_name': playlist_name,
                'song_count': len(songs),
                'success_count': success_count,
                'fail_count': fail_count,
                'songs': output_data
            }
            
            self.save_button.config(state=tk.NORMAL)
            return self.report_data
            
        except requests.RequestException as e:
            self.log(f"网络请求错误: {e}")
            return None
        except Exception as e:
            self.log(f"处理错误: {e}")
            return None
    
    def start_processing(self):
        playlist_url = self.link_entry.get().strip()
        if not playlist_url:
            messagebox.showwarning("警告", "请输入网易云歌单链接")
            return
        
        self.process_button.config(state=tk.DISABLED)
        self.save_button.config(state=tk.DISABLED)
        self.clear_output()
        
        thread = threading.Thread(target=self._process_thread, args=(playlist_url,))
        thread.daemon = True
        thread.start()
    
    def _process_thread(self, playlist_url):
        try:
            self.get_playlist_info(playlist_url)
        finally:
            self.process_button.config(state=tk.NORMAL)
    
    def save_report(self):
        if not self.report_data:
            messagebox.showwarning("警告", "没有可保存的报告")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON文件", "*.json"), ("文本文件", "*.txt"), ("所有文件", "*.*")],
            initialfile=f"歌单_{self.report_data['playlist_name']}_报告.json"
        )
        
        if file_path:
            try:
                if file_path.endswith('.json'):
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(self.report_data, f, ensure_ascii=False, indent=2)
                else:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        for item in self.report_data['songs']:
                            if item['bilibili_url'] and 'https://' in item['bilibili_url']:
                                f.write(f"{item['bilibili_url']}\n")
                
                messagebox.showinfo("成功", f"报告已保存到: {file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"保存报告失败: {e}")

def main():
    root = tk.Tk()
    app = PlaylistToolGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()