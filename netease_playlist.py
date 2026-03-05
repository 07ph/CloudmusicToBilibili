import requests
import re
import time
import random
import json
from params_encSecKey import Netease_params

# 搜索B站视频并返回第一个结果的链接
def search_bilibili_video(keyword):
    try:
        # 使用B站视频搜索API
        url = "https://api.bilibili.com/x/web-interface/search/type"
        params = {
            "keyword": keyword,
            "search_type": "video",
            "page": 1,
            "limit": 5
        }
        # 随机User-Agent，避免包含python关键字
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
        # 添加cookies
        cookies = {
            "SESSDATA": "9735d36d%2C1787889398%2C6227d%2A32CjACX3chmaPakvqXR3k5nT7MIqcy6bKTdaQcypUEIbGNIzjCXBA36-qvRIneIU0cD1gSVlg2dTZTTVFFNjBjbkVJTTFicnl6QUxMeW8wMWRxWXNYS2c1QkxiczgtSXFaNlF1ZkFyWXIzTkUwalhxTDhpbjdyYVd6TTJjVVVLY2FWbl9GQk4zQkxRIIEC",
            "bili_jct": "580fe4d4fb6309944ed831244a40648a"
        }
        response = requests.get(url, params=params, headers=headers, cookies=cookies)
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
        print(f"B站搜索错误: {e}")
        return None, "搜索失败"

# 收藏B站视频
def collect_video(bvid, sessdata, bili_jct):
    # 直接返回手动收藏链接
    collect_url = f"https://www.bilibili.com/video/{bvid}"
    return False, f"请手动收藏: {collect_url}"

def get_playlist_info(playlist_url):
    # 从URL中提取歌单ID
    match = re.search(r'playlist\?id=(\d+)', playlist_url)
    if not match:
        print("无法从URL中提取歌单ID")
        return
    
    playlist_id = match.group(1)
    print(f"获取歌单ID: {playlist_id}")
    
    # 读取配置文件
    print("\n读取配置文件...")
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        sessdata = config.get('bilibili', {}).get('sessdata', '')
        bili_jct = config.get('bilibili', {}).get('bili_jct', '')
        print("认证信息已加载")
    except Exception as e:
        print(f"读取配置文件失败: {e}")
        # 使用默认值
        sessdata = "9735d36d%2C1787889398%2C6227d%2A32CjACX3chmaPakvqXR3k5nT7MIqcy6bKTdaQcypUEIbGNIzjCXBA36-qvRIneIU0cD1gSVlg2dTZTTVFFNjBjbkVJTTFicnl6QUxMeW8wMWRxWXNYS2c1QkxiczgtSXFaNlF1ZkFyWXIzTkUwalhxTDhpbjdyYVd6TTJjVVVLY2FWbl9GQk4zQkxRIIEC"
        bili_jct = "580fe4d4fb6309944ed831244a40648a"
        print("使用默认认证信息")
    
    try:
        # 获取歌单基本信息和所有歌曲ID
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
            print(f"API请求失败: {response.get('message', '未知错误')}")
            return
        
        playlist = response['playlist']
        playlist_name = playlist.get('name', '未知歌单')
        track_count = playlist.get('trackCount', 0)
        
        print(f"\n歌单名称: {playlist_name}")
        print(f"歌曲数量: {track_count}")
        print("\n歌曲列表:")
        print("-" * 160)
        
        # 提取所有歌曲ID
        id_list = [i['id'] for i in playlist['trackIds']]
        c = [{'id': i} for i in id_list]
        
        # 批量获取歌曲详细信息
        time.sleep(1)
        song_api = 'https://music.163.com/weapi/v3/song/detail'
        song_data = {
            'c': str(c),
            'csrf_token': ''
        }
        song_params = Netease_params(song_data)
        song_response = song_params.run(song_api)
        
        if song_response.get('code') != 200:
            print(f"获取歌曲信息失败: {song_response.get('message', '未知错误')}")
            return
        
        songs = song_response['songs']
        # 准备保存到文件的数据
        output_data = []
        # 记录搜索失败的歌曲
        failed_searches = []
        
        for i, song in enumerate(songs, 1):
            song_name = song.get('name', '未知歌曲')
            # 提取歌手信息
            artists = song.get('ar', [])
            artist_names = [artist.get('name', '未知歌手') for artist in artists]
            artist_str = ' / '.join(artist_names)
            
            # 构建搜索关键词
            search_keyword = f"{song_name} {artist_str}"
            # 搜索B站视频
            bvid, video_url = search_bilibili_video(search_keyword)
            
            print(f"{i}. {song_name} - {artist_str}")
            print(f"   B站视频: {video_url}")
            
            if not bvid:
                # 记录搜索失败的歌曲
                failed_searches.append({
                    'index': i,
                    'song_name': song_name,
                    'artists': artist_str,
                    'search_keyword': search_keyword
                })
            print()
            
            # 添加到输出数据
            output_data.append({
                'index': i,
                'song_name': song_name,
                'artists': artist_str,
                'bilibili_url': video_url
            })
            
            # 添加3-5秒随机延迟，避免反爬
            time.sleep(random.uniform(3, 5))
        
        # 对搜索失败的歌曲进行重复搜索，直到成功
        if failed_searches:
            print("\n进行重复搜索...")
            for item in failed_searches:
                print(f"重新搜索: {item['song_name']} - {item['artists']}")
                
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
                    
                    print(f"   尝试关键词: {keyword}")
                    bvid, video_url = search_bilibili_video(keyword)
                    
                    if bvid:
                        final_url = video_url
                        success = True
                        break
                    
                    # 添加3-5秒随机延迟
                    time.sleep(random.uniform(3, 5))
                
                # 更新输出数据
                for data_item in output_data:
                    if data_item['index'] == item['index']:
                        data_item['bilibili_url'] = final_url
                        break
                
                print(f"   最终搜索结果: {final_url}")
                print()
                
                # 添加3-5秒随机延迟
                time.sleep(random.uniform(3, 5))
        
        # 保存到txt文件
        output_file = f"歌单_{playlist_name}_B站链接.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            for item in output_data:
                if item['bilibili_url'] and 'https://' in item['bilibili_url']:
                    f.write(f"{item['bilibili_url']}\n")
        
        # 保存到JSON文件
        json_output_file = f"歌单_{playlist_name}_B站链接.json"
        json_data = {
            "playlist_name": playlist_name,
            "song_count": len(songs),
            "songs": output_data
        }
        with open(json_output_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        print("-" * 160)
        print(f"共 {len(songs)} 首歌曲")
        print(f"B站链接已保存到: {output_file}")
        print(f"JSON格式数据已保存到: {json_output_file}")
        
    except requests.RequestException as e:
        print(f"网络请求错误: {e}")
    except Exception as e:
        print(f"处理错误: {e}")

if __name__ == "__main__":
    # 测试链接
    test_url = "https://music.163.com/playlist?id=6940665039&uct2=U2FsdGVkX1/5ruHylj2D6Z89v2UUuqes2/Jq1tXu++g="
    get_playlist_info(test_url)