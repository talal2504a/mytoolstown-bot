"""
Server Bot - 24/7 Auto Credit Earner
=====================================
No input prompts. Everything from config.json.
Auto-restart on crash. Logs to file.
Uses progressive cooldown - NEVER stops.
"""

import asyncio
import json
import os
import sys
import random
from datetime import datetime
from playwright.async_api import async_playwright

LOG_FILE = "server_bot.log"
COOLDOWN_COUNTER = [0]  # Global counter using list for mutability in nested functions

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(line + "\n")

def log_error(msg):
    log(f"❌ {msg}")

def load_config():
    default = {
        "instagram_username": "",
        "headless": True,
        "slow_mo": 100,
        "verify_wait_time": 3,
        "cookies_file": "server_session.json",
        "cycle_delay_min": 25,
        "cycle_delay_max": 50,
    }
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            default.update(json.load(f))
            log(f"Config loaded")
    if not default["instagram_username"]:
        log_error("instagram_username is empty in config.json!")
        sys.exit(1)
    return default

CONFIG = load_config()


async def save_cookies(page, filepath):
    cookies = await page.context.cookies()
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(cookies, f)


async def load_cookies(context, filepath):
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                await context.add_cookies(json.load(f))
            return True
        except:
            pass
    return False


async def login_to_site(page, username):
    log(f"Logging in as {username}...")
    try:
        await page.goto("https://mytoolstown.com/autoliker", wait_until="networkidle")
        await asyncio.sleep(2)
        if "dashboard" in page.url or "earn" in page.url:
            log("Already logged in!")
            return True
        inp = await page.query_selector("#username")
        if not inp:
            return False
        await inp.fill(username)
        btn = await page.query_selector("#searchbtn")
        if btn:
            await btn.click()
            await asyncio.sleep(5)
            await page.wait_for_load_state("networkidle")
            log(f"Login success")
            return True
        return False
    except Exception as e:
        log_error(f"Login: {e}")
        return False


async def navigate_to_earn_page(page):
    try:
        await page.goto("https://mytoolstown.com/autoliker/earn", wait_until="networkidle", timeout=30000)
        await asyncio.sleep(2)
        return True
    except Exception as e:
        log_error(f"Nav: {e}")
        return False


async def perform_earn_cycle(page, cycle_num):
    try:
        await page.reload(wait_until="networkidle")
        await asyncio.sleep(3)

        # === COOLDOWN HANDLING - NEVER STOPS ===
        while True:
            body_text = await page.inner_text("body")
            if "no promotions" in body_text.lower() or "come back later" in body_text.lower():
                COOLDOWN_COUNTER[0] += 1
                cc = COOLDOWN_COUNTER[0]

                # Progressive: 1min -> 2min -> 5min -> 10min -> 15min
                if cc <= 2:    wait_min = 1
                elif cc <= 5:  wait_min = 2
                elif cc <= 10: wait_min = 5
                elif cc <= 20: wait_min = 10
                else:          wait_min = 15

                wait_sec = random.randint(wait_min * 60, (wait_min + 1) * 60)
                log(f"⏸️  Cooldown #{cc}: waiting {wait_min} min...")
                await asyncio.sleep(wait_sec)
                await page.reload(wait_until="networkidle")
                await asyncio.sleep(5)
                continue
            # No cooldown - reset counter
            if COOLDOWN_COUNTER[0] > 0:
                log(f"✅ Cooldown cleared! Resuming.")
            COOLDOWN_COUNTER[0] = 0
            break

        # Find FOLLOW button
        follow_btn = await page.query_selector('#earnBtn')
        if not follow_btn:
            all_els = await page.query_selector_all('a, button, [class*="btn"]')
            for el in all_els:
                try:
                    t = (await el.inner_text()).strip()
                    if t == "FOLLOW" and await el.is_visible():
                        follow_btn = el
                        break
                except:
                    pass

        if not follow_btn:
            log_error("Follow button not found")
            return False

        log(f"[{cycle_num}] Clicking FOLLOW...")
        async with page.context.expect_page() as new_page_info:
            await follow_btn.click()

        try:
            insta_page = await new_page_info.value
            await insta_page.wait_for_load_state("domcontentloaded")
            await asyncio.sleep(1)
            await insta_page.close()
        except:
            pass

        await asyncio.sleep(1)

        # Find VERIFY button
        verify_btn = None
        for selector in ['button:has-text("Verify")', 'a:has-text("Verify")',
                         '.btn-primary:has-text("Verify")', 'button:has-text("verify")']:
            try:
                el = await page.query_selector(selector)
                if el and await el.is_visible():
                    verify_btn = el
                    break
            except:
                pass

        if verify_btn:
            await verify_btn.click()
            await asyncio.sleep(CONFIG['verify_wait_time'])
            log(f"[{cycle_num}] ✅ Verify clicked!")
            return True
        else:
            log(f"[{cycle_num}] No verify btn - follow done")
            return True

    except Exception as e:
        log_error(f"Cycle error: {e}")
        return False


async def run_bot():
    log("=" * 55)
    log(f"SERVER BOT - Username: {CONFIG['instagram_username']}")
    log("=" * 55)

    while True:
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=CONFIG['headless'],
                    slow_mo=CONFIG['slow_mo']
                )
                context = await browser.new_context(viewport={"width": 1280, "height": 720})
                page = await context.new_page()

                await load_cookies(context, CONFIG['cookies_file'])
                if not await login_to_site(page, CONFIG['instagram_username']):
                    await browser.close()
                    await asyncio.sleep(30)
                    continue

                await save_cookies(page, CONFIG['cookies_file'])
                await navigate_to_earn_page(page)

                cycle = 0
                while True:
                    cycle += 1
                    log(f"\n--- Cycle #{cycle} ---")
                    result = await perform_earn_cycle(page, cycle)

                    if not result:
                        await asyncio.sleep(5)
                        continue

                    log(f"✅ Cycle #{cycle} done")

                    # Short human-like delay
                    delay = random.randint(CONFIG['cycle_delay_min'], CONFIG['cycle_delay_max'])
                    log(f"Next in {delay}s...")
                    await asyncio.sleep(delay)

        except Exception as e:
            log_error(f"Fatal: {e}")
            import traceback
            traceback.print_exc()
            await asyncio.sleep(30)


if __name__ == "__main__":
    log("MyToolsTown Server Bot - 24/7")
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        log("\nStopped by user")
    except Exception as e:
        log_error(f"Fatal: {e}")