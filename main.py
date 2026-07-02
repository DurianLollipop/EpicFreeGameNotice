import requests
import os
from datetime import datetime, timedelta
import html

# 1. 获取 GitHub Secrets
BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")
CHAT_ID = os.environ.get("TG_CHAT_ID")
BARK_URL = os.environ.get("BARK_URL")
BARK_GROUP = os.environ.get("BARK_GROUP", "Epic Free Games")

def get_epic_free_games():
    url = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=en-US"
    try:
        res = requests.get(url).json()
        games = res['data']['Catalog']['searchStore']['elements']
        
        free_games = []
        for game in games:
            # 1. 基础过滤
            promotions = game.get('promotions')
            if not promotions: continue
            if not promotions.get('promotionalOffers'): continue
            
            offers = promotions['promotionalOffers']
            if not offers: continue

            is_free = False
            end_date_str = "未知"
            is_new_game = False # 标记是否为新上架的游戏

            for offer_group in offers:
                for offer in offer_group['promotionalOffers']:
                    if offer['discountSetting']['discountPercentage'] == 0:
                        is_free = True
                        
                        # Time formatting
                        raw_end_date = offer.get('endDate')
                        raw_start_date = offer.get('startDate') # 获取开始时间
                        
                        # 处理截止时间
                        if raw_end_date:
                            try:
                                dt_end = datetime.strptime(raw_end_date.split('.')[0], "%Y-%m-%dT%H:%M:%S")
                                end_date_str = dt_end.strftime("%Y-%m-%d %H:%M") + " (UTC)"
                            except:
                                end_date_str = raw_end_date
                        
                        # 【核心逻辑】判断游戏是否“刚上架”
                        # 只有在促销开始的 28 小时内检测到，才算“新消息”并推送。
                        # 28小时是为了容错（GitHub Action 可能会排队延迟几分钟）
                        if raw_start_date:
                            try:
                                dt_start = datetime.strptime(raw_start_date.split('.')[0], "%Y-%m-%dT%H:%M:%S")
                                # 获取当前 UTC 时间
                                now = datetime.utcnow()
                                # 计算时间差
                                time_diff = now - dt_start
                                
                                # 如果时间差小于 28 小时，说明是刚出的新游戏 -> 推送
                                # 如果时间差大于 28 小时，说明是昨天的旧消息 -> 不推送
                                if time_diff < timedelta(hours=28):
                                    is_new_game = True
                                else:
                                    print(f"跳过旧游戏: {game.get('title')} (已上架 {time_diff})")
                            except Exception as e:
                                print(f"时间解析错误: {e}")
                                # 如果时间解析失败，为了保险起见，默认它是新的，防止漏发
                                is_new_game = True
                        else:
                            is_new_game = True # 没有开始时间的数据，默认发送
                        
                        break
            
            # 只有当它是免费 且 是新上架的游戏时，才加入列表
            if is_free and is_new_game:
                title = game.get('title')
                description = game.get('description', '暂无描述')
                slug = game.get('productSlug') or game.get('urlSlug')
                link = f"https://store.epicgames.com/p/{slug}" if slug else "https://store.epicgames.com/free-games"
                
                image_url = ""
                for img in game.get('keyImages', []):
                    if img.get('type') == 'Thumbnail':
                        image_url = img.get('url')
                        break
                    elif img.get('type') == 'OfferImageWide':
                        image_url = img.get('url')

                free_games.append({
                    "title": title,
                    "description": description,
                    "link": link,
                    "image": image_url,
                    "end_date": end_date_str
                })
                
        return free_games
        
    except Exception as e:
        print(f"获取 Epic 数据出错: {e}")
        return []

def send_telegram_message(message):
    if not BOT_TOKEN or not CHAT_ID:
        print("未配置 Telegram，跳过 Telegram 推送")
        return
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML", 
        "disable_web_page_preview": False
    }
    try:
        res = requests.post(url, json=payload, timeout=15)
        res.raise_for_status()
        print("✅ Telegram 推送成功")
    except Exception as e:
        print(f"❌ 推送错误: {e}")

def send_bark_message(game):
    if not BARK_URL:
        print("未配置 Bark，跳过 Bark 推送")
        return

    title = f"Epic 喜加一提醒：{game['title']}"
    body = (
        f"截止: {game['end_date']}\n\n"
        f"{game['description']}\n\n"
        f"点击通知领取游戏"
    )
    payload = {
        "title": title,
        "body": body,
        "url": game["link"],
        "group": BARK_GROUP,
    }

    if game.get("image"):
        payload["icon"] = game["image"]

    try:
        res = requests.post(BARK_URL.rstrip("/"), json=payload, timeout=15)
        res.raise_for_status()
        print("✅ Bark 推送成功")
    except Exception as e:
        print(f"❌ Bark 推送错误: {e}")

if __name__ == "__main__":
    print("⏳ 开始检查 Epic 免费游戏 (每日去重版)...")
    games = get_epic_free_games()
    
    if games:
        print(f"🎉 发现 {len(games)} 个新上架的免费游戏")
        for g in games:
            safe_title = html.escape(g['title'])
            safe_desc = html.escape(g['description'])
            
            msg = (
                f"<a href='{g['image']}'>&#8205;</a>"
                f"🔥 <b>Epic 喜加一提醒</b> 🔥\n\n"
                f"🎮 <b>{safe_title}</b>\n"
                f"⏰ 截止: {g['end_date']}\n\n"
                f"📝 {safe_desc}\n\n"
                f"🔗 <a href='{g['link']}'>点击领取游戏</a>"
            )
            send_telegram_message(msg)
            send_bark_message(g)
    else:
        print("🤷‍♂️ 今天没有新上架的免费游戏 (可能是旧游戏已通知过)")
