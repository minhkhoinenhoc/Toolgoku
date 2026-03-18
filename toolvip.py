# -*- coding: utf-8 -*-
import threading, time, os, re, json, requests
from colorama import init
from datetime import datetime

init(autoreset=True)
    
import time
import sys

def show_banner():
    banner_text = """
╔══════════════════════════════════════════════════════════════╗
║                   🌟 TOOL SPAM MESS & DIS & TELE 🌟          ║
║                    Facebook:Nh Qui               ║
║                    © Copyright: Nhất Vy                 ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner_text)

# ==== GLOBAL STATE ====
messenger_ids = []
discord_ids = []
messenger_lock = threading.Lock()
discord_lock = threading.Lock()
messengers = []
file_dict_mess = {}
delay_mess = 1
tokens = []
delays_dis = {}
file_dict_dis = {}

# ==== UTILITIES ====

def input_multi_line(prompt):
    print(prompt)
    lines = []
    while True:
        line = input()
        if not line: break
        lines.extend(line.strip().split(','))
    return [l.strip() for l in lines if l.strip()]

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

clear()

def write_log(message):
    max_lines = 1000
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}\n"
    with open("log.txt", "a+", encoding="utf-8") as log_file:
        log_file.write(line)

    try:
        with open("log.txt", "r", encoding="utf-8") as log_file:
            lines = log_file.readlines()
        if len(lines) > max_lines:
            with open("log.txt", "w", encoding="utf-8") as log_file:
                log_file.writelines(lines[-max_lines:])
    except:
        pass

def log_memory_usage():
    mem = psutil.virtual_memory()
    write_log(f"[RAM] Dung luong RAM: {mem.percent}% - Con lai: {mem.available // (1024 * 1024)} MB")


import re
import requests
import time

def get_uid(cookie):
    try:
        return re.search(r'c_user=(\d+)', cookie).group(1)
    except:
        return '0'

def get_fb_dtsg_jazoest(cookie, target_id):
    try:
        response = requests.get(
            f'https://mbasic.facebook.com/privacy/touch/block/confirm/?bid={target_id}',
            headers={ 'cookie': cookie, 'user-agent': 'Mozilla/5.0' }
        ).text
        fb_dtsg = re.search('name="fb_dtsg" value="([^"]+)"', response).group(1)
        jazoest = re.search('name="jazoest" value="([^"]+)"', response).group(1)
        return fb_dtsg, jazoest
    except:
        return None, None

def get_eaag_token(cookie):
    try:
        res = requests.get(
            'https://business.facebook.com/business_locations',
            headers={ 'cookie': cookie, 'user-agent': 'Mozilla/5.0' }
        )
        return re.search(r'EAAG\w+', res.text).group()
    except:
        return None

def send_message(idbox, fb_dtsg, jazoest, cookie, message_body):
    try:
        uid = get_uid(cookie)
        timestamp = int(time.time() * 1000)
        data = {
            'thread_fbid': idbox,
            'action_type': 'ma-type:user-generated-message',
            'body': message_body,
            'client': 'mercury',
            'author': f'fbid:{uid}',
            'timestamp': timestamp,
            'offline_threading_id': str(timestamp),
            'message_id': str(timestamp),
            'source': 'source:chat:web',
            '__user': uid,
            '__a': '1',
            '__req': '1b',
            '__rev': '1015919737',
            'fb_dtsg': fb_dtsg,
            'jazoest': jazoest
        }
        headers = {
            'Cookie': cookie,
            'User-Agent': 'Mozilla/5.0',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        response = requests.post('https://www.facebook.com/messaging/send/', data=data, headers=headers)
        return response.status_code == 200
    except Exception as e:
        print(f'Lỗi gửi tới ID {idbox}: {e}')
        return False

def worker(cookie_data, id_list, message_list, base_delay):
    name = cookie_data['name']
    cookie = cookie_data['cookie']

    while True:
        try:
            fb_dtsg, jazoest = get_fb_dtsg_jazoest(cookie, id_list[0])
            if not fb_dtsg or not jazoest:
                print(f"Không lấy được fb_dtsg/jazoest")
                time.sleep(60)
                continue

            for idbox in id_list:
                for message_body in message_list:
                    success = send_message(idbox, fb_dtsg, jazoest, cookie, message_body)
                    if success:
                        print(f"Gửi tin nhắn thành công tới: {idbox}")
                    else:
                        print(f"Gửi tin nhắn thất bại tới: {idbox}")
                    
                    delay = base_delay + random.uniform(-0.5, 0.5)
                    if delay < 0:
                        delay = 0
                    time.sleep(delay)
        except Exception as err:
            print(f"Lỗi không xác định: {err}")
            time.sleep(60)

# ==== SPAM LOOP ====

def loop_mess():
    import gc
    index = {}
    logged = set()
    while True:
        with messenger_lock:
            ids = list(messenger_ids)
            cookies = list(messengers)  # messengers giờ là danh sách cookie string
        for cookie in cookies:
            uid = get_uid(cookie)
            for rid in ids:
                index.setdefault(rid, 0)
                fpath_list = file_dict_mess.get(rid, [])
                if not fpath_list:
                    continue
                fpath = fpath_list[index[rid] % len(fpath_list)]
                if fpath:
                    try:
                        with open(fpath, 'r', encoding='utf-8') as f:
                            msg = f.read().strip()
                        if msg:
                            fb_dtsg, jazoest = get_fb_dtsg_jazoest(cookie, rid)
                            if not fb_dtsg or not jazoest:
                                print(f"[×] Không lấy được fb_dtsg cho {uid}")
                                continue
                            success = send_message(rid, fb_dtsg, jazoest, cookie, msg)
                            if success and (uid, rid) not in logged:
                                print(f"[✓] UID: {uid} => Box: {rid}")
                                logged.add((uid, rid))
                                gc.collect()
                            elif not success:
                                print(f"[×] Gửi thất bại UID {uid} đến {rid}")
                    except Exception as e:
                        print(f"[Messenger] Lỗi gửi: {e}")
                index[rid] += 1
                time.sleep(delay_mess)

def loop_dis(token):
    import gc
    index = {}
    logged = set()
    while True:
        with discord_lock:
            ids = list(discord_ids)
        for cid in ids:
            index.setdefault(cid, 0)
            fpath_list = file_dict_dis.get(cid, [])
            if not fpath_list:
                continue
            fpath = fpath_list[index[cid] % len(fpath_list)]
            if fpath:
                try:
                    with open(fpath, 'r', encoding='utf-8') as f:
                        msg = f.read().strip()
                    if msg:
                        msg = msg[:2000]
                        url = f"https://discord.com/api/v10/channels/{cid}/messages"
                        headers = {"Authorization": token, "Content-Type": "application/json"}
                        r = requests.post(url, headers=headers, json={"content": msg})
                        if r.status_code in [200, 201]:
                            key = (token, cid)
                            if key not in logged:
                                print(f"[Discord] Token: {token[:15]}... => ID: {cid}")
                                logged.add(key)
                                gc.collect()  # 🔄 Xả RAM sau khi gửi thành công
                        else:
                            print(f"[×] Discord lỗi {cid}: {r.text}")
                except Exception as e:
                    print(f"[Discord] Lỗi đọc {fpath}: {e}")
            index[cid] += 1
            time.sleep(delays_dis.get(token, 1))
            
treo_anh_threads = {}

def send_photo(token, chat_id, caption, photo, retries=5):
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    send_success = False

    for attempt in range(retries):
        try:
            if photo and photo.startswith("http"):
                data = {"chat_id": chat_id, "caption": caption, "photo": photo}
                response = requests.post(url, data=data, timeout=30)
            elif photo:
                with open(photo, "rb") as f:
                    files = {"photo": f}
                    data = {"chat_id": chat_id, "caption": caption}
                    response = requests.post(url, data=data, files=files, timeout=30)
            else:
                url = f"https://api.telegram.org/bot{token}/sendMessage"
                data = {"chat_id": chat_id, "text": caption}
                response = requests.post(url, data=data, timeout=30)

            if response.status_code == 200:
                send_success = True
                break
            else:
                print(f"[!] Lỗi gửi: {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"[!] Lỗi gửi (lần {attempt+1}/{retries}): {e}")
            time.sleep(2)

    if not send_success:
        print(f"[!] Gửi đến {chat_id} thất bại sau {retries} lần thử.")

def loop_tele_advanced(token, info):
    import gc
    chat_ids = info["chat_ids"]
    chat_contents = info["chat_contents"]
    image_url = info["image_url"]
    delay = info["delay"]
    stop_event = info["stop_event"]

    short_token = token.split(":")[0]
    print(f"[✓] {short_token} =>> Đang spam {len(chat_ids)} nhóm (Telegram)...")

    while not stop_event.is_set():
        for chat_id in chat_ids:
            if not chat_id.strip():
                continue

            text = chat_contents.get(chat_id, "")
            if not text.strip():
                continue

            try:
                if image_url:
                    send_photo_url = f"https://api.telegram.org/bot{token}/sendPhoto"
                    caption = text if len(text) <= 1024 else text[:1021] + "..."
                    payload_photo = {
                        "chat_id": chat_id,
                        "photo": image_url,
                        "caption": caption
                    }
                    requests.post(send_photo_url, json=payload_photo, timeout=15)
                else:
                    send_text_url = f"https://api.telegram.org/bot{token}/sendMessage"
                    payload_text = {
                        "chat_id": chat_id,
                        "text": text
                    }
                    requests.post(send_text_url, json=payload_text, timeout=15)
            except Exception as e:
                print(f"[×] Lỗi gửi tới {chat_id}: {e}")

            if stop_event.is_set():
                break

            time.sleep(delay)
        gc.collect()
    
                
def global_input_handler_line(cmd):
    cmd = cmd.strip()

    if cmd.startswith("stop "):
        target_id = cmd[5:].strip()
        removed = False
        with messenger_lock:
            if target_id in messenger_ids:
                messenger_ids.remove(target_id)
                print(f"[✓] Đã stop Messenger box ID: {target_id}")
                removed = True
        with discord_lock:
            if target_id in discord_ids:
                discord_ids.remove(target_id)
                print(f"[✓] Đã stop Discord channel ID: {target_id}")
                removed = True
        for uid, info in treo_anh_threads.items():
            if target_id in info['chat_ids']:
                info['stop_event'].set()
                print(f"[✓] Đã stop Telegram ID: {target_id}")
                removed = True
                break
        if not removed:
            print(f"[×] Không tìm thấy ID: {target_id}")

    elif cmd == "stop":
        print("[ℹ] Dùng: stop <box_id | channel_id | telegram_id>")

    elif cmd.startswith("mess "):
        arg = cmd[5:].strip()
        if arg.isdigit():
            with messenger_lock:
                if arg not in messenger_ids:
                    messenger_ids.append(arg)
                    print(f"[✓] Thêm box ID: {arg}")
                    file_path = input(f"[+] Nhập file.txt cho {arg}: ").strip()
                    if file_path:
                        file_dict_mess[arg] = [file_path]
        elif "c_user=" in arg:
            if arg not in messengers:
                uid = get_uid(arg)
                messengers.append(arg)
                print(f"[✓] Thêm cookie có UID: {uid}")
            else:
                print("[!] Cookie đã tồn tại.")
        else:
            print("[×] Định dạng không hợp lệ. Nhập box ID hoặc cookie có chứa 'c_user='.")

    elif cmd == "mess":
        print("[ℹ] Dùng: mess <box_id> hoặc mess <cookie>")

    elif cmd.startswith("dis "):
        arg = cmd[4:].strip()
        if arg.isdigit():
            with discord_lock:
                if arg not in discord_ids:
                    discord_ids.append(arg)
                    print(f"[✓] Thêm channel ID: {arg}")
                    file_path = input(f"[+] Nhập file.txt cho {arg}: ").strip()
                    if file_path:
                        file_dict_dis[arg] = [file_path]
        elif len(arg) > 40:
            try:
                headers = {"Authorization": arg}
                r = requests.get("https://discord.com/api/v10/users/@me", headers=headers)
                if r.status_code == 200:
                    tokens.append(arg)
                    d = input(f"[+] Delay cho token {arg[:15]}... (giây): ")
                    delays_dis[arg] = float(d) if d else 1
                    print(f"[✓] Token hợp lệ: {arg[:20]}...")
                    threading.Thread(target=loop_dis, args=(arg,), daemon=True).start()
                else:
                    print(f"[×] Token die: {arg[:20]}... ({r.status_code})")
            except Exception as e:
                print(f"[×] Lỗi token: {e}")
        else:
            print("[×] Định dạng không hợp lệ. Nhập channel ID hoặc token dài > 40 ký tự.")

    elif cmd == "dis":
        print("[ℹ] Dùng: dis <channel_id> hoặc dis <token>")

    elif cmd.startswith("tele "):
        arg = cmd[5:].strip()
        if len(arg) > 30:  # xử lý như token
            try:
                r = requests.get(f"https://api.telegram.org/bot{arg}/getMe", timeout=10)
                if r.status_code == 200 and r.json().get("ok"):
                    print(f"[✓] Token hợp lệ: {arg[:20]}...")
                    chat_ids = input_multi_line("[+] Nhập ID nhóm Telegram (Enter 2 lần):")
                    file_path = input("[+] File .txt nội dung: ").strip()
                    if not os.path.isfile(file_path):
                        print("[×] File không tồn tại.")
                        return
                    with open(file_path, "r", encoding="utf-8") as f:
                        text = f.read()
                    img = input("[+] Link ảnh (Enter nếu không có): ").strip()
                    delay = float(input("[+] Nhập delay (giây): ").strip() or "5")
                    run_loop([arg], chat_ids, text, img or None, delay)
                else:
                    print(f"[×] Token không hợp lệ: {arg}")
            except Exception as e:
                print(f"[×] Lỗi kiểm tra token: {e}")
        else:  # xử lý như ID box Telegram
            print("[ℹ] Để treo Telegram cần nhập token bot trước. Gõ: tele <token>")

    elif cmd.startswith("tele "):
        arg = cmd[5:].strip()
        
        if len(arg) > 30:  # là token
            try:
                r = requests.get(f"https://api.telegram.org/bot{arg}/getMe", timeout=10)
                if r.status_code == 200 and r.json().get("ok"):
                    print(f"[✓] Token hợp lệ: {arg[:20]}...")
                    
                    chat_ids = []
                    chat_contents = {}
                    
                    while True:
                        chat_id = input("[+] Nhập ID nhóm Telegram (done để kết thúc): ").strip()
                        if chat_id.lower() == "done":
                            break
                        file_path = input(f"[+] Nhập file.txt cho {chat_id}: ").strip()
                        if not os.path.isfile(file_path):
                            print(f"[×] File không tồn tại.")
                            continue
                        with open(file_path, "r", encoding="utf-8") as f:
                            chat_contents[chat_id] = f.read()
                        chat_ids.append(chat_id)

                    if not chat_ids:
                        print("[×] Không có chat_id nào.")
                        return

                    img = input("[+] Link ảnh (Enter nếu không có): ").strip()
                    delay = float(input("[+] Delay (giây): ").strip() or "5")

                    stop_event = threading.Event()
                    treo_anh_threads[arg] = {
                        "chat_ids": chat_ids,
                        "chat_contents": chat_contents,
                        "image_url": img or None,
                        "delay": delay,
                        "stop_event": stop_event
                    }
                    threading.Thread(target=loop_tele_advanced, args=(arg, treo_anh_threads[arg]), daemon=True).start()
                    print(f"[✓] Đã treo Telegram với token {arg[:15]}...")
                else:
                    print(f"[×] Token không hợp lệ.")
            except Exception as e:
                print(f"[×] Lỗi kiểm tra token: {e}")

        else:  # xử lý như thêm chat_id vào tiến trình đang chạy
            found = False
            for token, info in treo_anh_threads.items():
                if arg not in info["chat_ids"]:
                    file_path = input(f"[+] Nhập file.txt cho {arg}: ").strip()
                    if os.path.isfile(file_path):
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                        info["chat_ids"].append(arg)
                        info["chat_contents"][arg] = content
                        print(f"[✓] Đã thêm ID {arg} vào tiến trình Telegram token {token[:15]}...")
                        found = True
                        break
            if not found:
                print(f"[×] Không tìm thấy token Telegram nào đang chạy.")

    elif cmd == "list":
        with messenger_lock:
            print(f"[Messenger]: {messenger_ids if messenger_ids else 'Không có'}")
        with discord_lock:
            print(f"[Discord]: {discord_ids if discord_ids else 'Không có'}")
        print(f"[Telegram]: {[chat_id for info in treo_anh_threads.values() for chat_id in info['chat_ids']]}")

    elif cmd == "help":
        print("""
🔹 Danh sách lệnh:
   ▸ mess <box_id>              → thêm  id box Messenger 
   ▸ mess <cookie>              → thêm cookie Messenger
   ▸ dis <channel_id>           → thêm id chanel Discord 
   ▸ dis <token>                → thêm token Discord
   ▸ tele <chat_id>             → thêm id box Telegram 
   ▸ tele <token>               → thêm token Telegram 
   ▸ stop <id>                  → dừng Messenger / Discord / Telegram theo ID
   ▸ list                       → xem các ID đang hoạt động
   ▸ help                       → hiện hướng dẫn lệnh
""")

    elif cmd == "menu":
        print("[ℹ] Đang ở trong menu.")

    elif cmd == "":
        pass

    else:
        print("[×] Lệnh không hợp lệ. Gõ `help` để xem hướng dẫn.")

# ==== MENU LOOP GỘP LỆNH ====
last_token_tele = {"token": None}  # để hỗ trợ tele <id> sau khi đã nhập token

def menu_loop():
    global delay_mess
    while True:
        print("""
╔═════════════════════════════════╗
║         CHỌN CHỨC NĂNG         ║
╠════════════════════════════════╣
║  1. Treo Messenger             ║
║  2. Treo Discord               ║
║  3. Treo Telegram              ║
║  4. Thoát Menu                 ║
╚════════════════════════════════╝
        """)
        chon = input("Nhập (1/2/3/4 hoặc lệnh: mess/dis/tele/stop/list/help): ").strip()

        if chon == "1":
            cookies = []
            print("[+] Nhập cookie Messenger (gõ 'done' để kết thúc):")
            while True:
                c = input("Cookie: ").strip()
                if c.lower() == 'done':
                    break
                if c:
                    uid = get_uid(c)
                    if uid != '0':
                        if c not in messengers:
                            messengers.append(c)
                            print(f"[✓] Cookie hợp lệ, UID: {uid}")
                        else:
                            print(f"[!] Cookie đã tồn tại.")
                    else:
                        print(f"[×] Cookie không hợp lệ: {c[:30]}...")

            if not messengers:
                print("[!] Không có cookie hợp lệ nào được nhập. Quay lại menu.\n")
                continue

            print("[+] Nhập ID box Messenger (gõ 'done' để kết thúc):")
            while True:
                box_id = input("ID box: ").strip()
                if box_id.lower() == 'done':
                    break
                file_path = input(f"[+] Nhập file.txt cho {box_id}: ").strip()
                if box_id and file_path:
                    with messenger_lock:
                        messenger_ids.append(box_id)
                        file_dict_mess[box_id] = [file_path]

            delay_mess = float(input("[+] Delay mỗi tin nhắn (giây): ") or "1")
            threading.Thread(target=loop_mess, daemon=True).start()
            print("[✓] Treo Messenger đã khởi động.\n")

        elif chon == "2":
            raw_tokens = []
            print("[+] Nhập token Discord (gõ 'done' để kết thúc):")
            while True:
                t = input("Token: ").strip()
                if t.lower() == 'done':
                    break
                if t:
                    try:
                        headers = {"Authorization": t}
                        r = requests.get("https://discord.com/api/v10/users/@me", headers=headers)
                        if r.status_code == 200:
                            if t not in tokens:
                                tokens.append(t)
                                d = input(f"[+] Delay cho token {t[:15]}... (giây): ")
                                delays_dis[t] = float(d) if d else 1
                                print(f"[✓] Token hợp lệ: {t[:20]}...")
                                threading.Thread(target=loop_dis, args=(t,), daemon=True).start()
                            else:
                                print(f"[!] Token đã tồn tại.")
                        else:
                            print(f"[×] Token die: {t[:20]}... ({r.status_code})")
                    except Exception as e:
                        print(f"[×] Lỗi kiểm tra token: {e}")

            if not tokens:
                print("[!] Không có token hợp lệ nào được nhập. Quay lại menu.\n")
                continue

            print("[+] Nhập ID channel Discord (gõ 'done' để kết thúc):")
            while True:
                cid = input("ID channel: ").strip()
                if cid.lower() == 'done':
                    break
                file_path = input(f"[+] Nhập file.txt cho {cid}: ").strip()
                if cid and file_path:
                    with discord_lock:
                        discord_ids.append(cid)
                        file_dict_dis[cid] = [file_path]

            print("[✓] Treo Discord đã khởi động.\n")

        elif chon == "3":
            tokens_tele = []
            print("[+] Nhập token bot Telegram (nhập 'done' để kết thúc):")
            while True:
                token = input("  → Token: ").strip()
                if token.lower() == "done":
                    break
                try:
                    r = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=10)
                    if r.status_code == 200 and r.json().get("ok"):
                        print(f"[✓] Token hợp lệ: {token[:20]}...")
                        tokens_tele.append(token)
                    else:
                        print(f"[×] Token không hợp lệ: {token}")
                except:
                    print(f"[×] Lỗi kết nối Telegram.")

            if not tokens_tele:
                print("[×] Không có token hợp lệ nào.")
                return

            chat_ids = []
            chat_contents = {}

            while True:
                chat_id = input("[+] Nhập ID nhóm Telegram (done để kết thúc): ").strip()
                if chat_id.lower() == "done":
                    break
                file_path = input(f"[+] Nhập file.txt cho {chat_id}: ").strip()
                if os.path.isfile(file_path):
                    with open(file_path, "r", encoding="utf-8") as f:
                        chat_contents[chat_id] = f.read()
                    chat_ids.append(chat_id)
                else:
                    print(f"[×] File không tồn tại: {file_path}")

            if not chat_ids:
                print("[×] Chưa có ID nào được thêm.")
                return

            img = input("[+] Nhập link ảnh hoặc để trống nếu không treo ảnh: ").strip()
            delay = float(input("[+] Nhập delay (giây): ") or "5")

            for token in tokens_tele:
                stop_event = threading.Event()
                treo_anh_threads[token] = {
                    "chat_ids": chat_ids,
                    "chat_contents": chat_contents,
                    "image_url": img or None,
                    "delay": delay,
                    "stop_event": stop_event
                }
                threading.Thread(
                    target=loop_tele_advanced,
                    args=(token, treo_anh_threads[token]),
                    daemon=True
                ).start()
                print(f"[✓] Treo Telegram đã khởi động với token {token[:15]}...\n")

        elif chon == "4":
            print("[⏪] Đã thoát khỏi menu.")
            break

        elif chon.startswith("mess ") or chon.startswith("dis ") or chon.startswith("tele ") or chon.startswith("stop ") or chon in ["mess", "dis", "tele", "list", "help", "menu"]:
            global_input_handler_line(chon)  # xử lý lệnh ẩn

        else:
            print("[!] Lựa chọn không hợp lệ.")
# ==== MAIN START ====
if __name__ == "__main__":
    show_banner()
    print("🔧 Tool đã khởi động!")
    menu_loop()
