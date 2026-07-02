import requests
import os
from datetime import datetime
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
            for offer_group in offers:
                for offer in offer_group['promotionalOffers']:
                    if offer['discountSetting']['discountPercentage'] == 0:
                        is_free = True
                        
                        # Time formatting
                        raw_end_date = offer.get('endDate')
                        
                        # 处理截止时间
                        if raw_end_date:
                            try:
                                dt_end = datetime.strptime(raw_end_date.split('.')[0], "%Y-%m-%dT%H:%M:%S")
                                end_date_str = dt_end.strftime("%Y-%m-%d %H:%M") + " (UTC)"
                            except:
                                end_date_str = raw_end_date
                        
                        break
            
            # 测试模式：只要当前是免费游戏就推送，暂不限制上架时间。
            if is_free:
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
