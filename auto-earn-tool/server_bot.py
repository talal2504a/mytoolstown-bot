"""
Server Bot - 24/7 Auto Credit Earner
=====================================
No input prompts. Everything from config.json.
Auto-restart on crash. Logs to file.
Runs headless browser 24/7.

For free servers:
- Oracle Cloud Free Tier (best - 24GB RAM, always free)
- Google Cloud $300 trial
- Any Linux VPS with 1GB+ RAM
"""

import asyncio
import json
import os
import sys
import time
import random
from datetime import datetime
from playwright.async_api import async_playwright

# ===== LOGGING =====
LOG_FILE = "server_bot.log"

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    # Also write to log file
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(line + "\n")

def log_error(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] ❌ {msg}"
    print(line)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(line + "\n")

# ===== LOAD CONFIG =====
def load_config():
    default_config = {
        "instagram_username": "",
        "headless": True,
        "slow_mo": 100,
        "max_earn_cycles": 0,
        "verify_wait_time": 3,
        "cookies_file": "server_session.json",
        "cycle_delay_min": 25,
        "cycle_delay_max": 50,
        "long_break_interval": 8,
        "long_break_min": 120,
        "long_break_max": 240,
    }

    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
                log(f"Config loaded from {config_path}")
        except Exception as e:
            log_error(f"Config load error: {e}")
    else:
        log_error(f"No config.json found at {config_path}")
        log("Please create config.json with your Instagram username")
        sys.exit(1)

    if not default_config["instagram_username"]:
        log_error("instagram_username is empty in config.json!")
        sys.exit(1)

    return default_config


CONFIG = load_config()


async def save_cookies(page, filepath):
    cookies = await page.context.cookies()
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(cookies, f)
    log(f"Cookies saved to {filepath}")


async def load_cookies(context, filepath):
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                await context.add_cookies(json.load(f))
            log(f"Cookies loaded from {filepath}")
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
            log_error("Username field not found")
            return False

        await inp.fill(username)
        btn = await page.query_selector("#searchbtn")
        if btn:
            await btn.click()
            await asyncio.sleep(5)
            await page.wait_for_load_state("networkidle")
            log(f"Login success. URL: {page.url}")
            return True
        return False
    except Exception as e:
        log_error(f"Login error: {e}")
        return False


async def navigate_to_earn_page(page):
    try:
        await page.goto("https://mytoolstown.com/autoliker/earn", wait_until="networkidle", timeout=30000)
        await asyncio.sleep(2)
        return True
    except Exception as e:
        log_error(f"Navigate error: {e}")
        return False


async def perform_earn_cycle(page, cycle_num):
    try:
        await page.reload(wait_until="networkidle")
        await asyncio.sleep(3)

        # Check for cooldown
        retry_count = 0
        while retry_count < 5:
            body_text = await page.inner_text("body")
            if "no promotions" in body_text.lower() or "come back later" in body_text.lower():
                retry_count += 1
                log(f"No promotions (attempt {retry_count}/5)")

                if retry_count >= 3:
                    log("Session reset needed after 3 retries")
                    return "RESET"

                cooldown_wait = random.randint(60, 180)  # 1-3 min
                log(f"Cooldown wait: {cooldown_wait}s...")
                await asyncio.sleep(cooldown_wait)
                await page.reload(wait_until="networkidle")
                await asyncio.sleep(5)
                continue
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

        # Click FOLLOW
        log(f"[{cycle_num}] Clicking FOLLOW...")
        async with page.context.expect_page() as new_page_info:
            await follow_btn.click()

        try:
            insta_page = await new_page_info.value
            await insta_page.wait_for_load_state("domcontentloaded")
            await asyncio.sleep(1)
            await insta_page.close()
            log("Instagram tab closed")
        except:
            pass

        await asyncio.sleep(1)

        # Find VERIFY button
        verify_btn = None
        for selector in ['button:has-text("Verify")', 'a:has-text("Verify")', '.btn-primary:has-text("Verify")',
                         'button:has-text("verify")']:
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
            log(f"[{cycle_num}] ✅ Verify clicked! Cycle complete.")
            return True
        else:
            log(f"[{cycle_num}] No verify btn found - follow done at least")
            return True

    except Exception as e:
        log_error(f"Cycle error: {e}")
        return False


async def run_bot():
    log("=" * 55)
    log(f"SERVER BOT STARTED - Username: {CONFIG['instagram_username']}")
    log(f"Headless: {CONFIG['headless']}")
    log("=" * 55)

    while True:  # Outer loop for crash recovery
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=CONFIG['headless'],
                    slow_mo=CONFIG['slow_mo']
                )

                context = await browser.new_context(
                    viewport={"width": 1280, "height": 720}
                )
                page = await context.new_page()

                # Login
                await load_cookies(context, CONFIG['cookies_file'])
                if not await login_to_site(page, CONFIG['instagram_username']):
                    log_error("Login failed, restarting...")
                    await browser.close()
                    await asyncio.sleep(30)
                    continue

                await save_cookies(page, CONFIG['cookies_file'])
                await navigate_to_earn_page(page)

                # Main earn loop
                cycle = 0
                session_cycles = 0

                while True:
                    cycle += 1
                    session_cycles += 1
                    log(f"\n--- Cycle #{cycle} (Session cycle #{session_cycles}) ---")

                    result = await perform_earn_cycle(page, cycle)

                    if result == "RESET":
                        log("Session reset needed - will restart")
                        break  # Break inner loop, restart from login

                    if result:
                        log(f"✅ Cycle #{cycle} complete")

                        # Long break every N cycles
                        lb = CONFIG['long_break_interval']
                        if session_cycles > 0 and session_cycles % lb == 0:
                            break_time = random.randint(CONFIG['long_break_min'], CONFIG['long_break_max'])
                            log(f"Long break: {break_time//60}m {break_time%60}s")
                            await asyncio.sleep(break_time)

                        # Session rotation every 15 cycles
                        if session_cycles >= 15:
                            log("Session rotation after 15 cycles")
                            await save_cookies(page, CONFIG['cookies_file'])
                            await page.close()
                            await context.close()
                            break

                    # Human delay
                    delay = random.randint(CONFIG['cycle_delay_min'], CONFIG['cycle_delay_max'])
                    log(f"Next cycle in {delay}s...")
                    await asyncio.sleep(delay)

                # Cleanup before restart
                try:
                    await browser.close()
                except:
                    pass

                log("Restarting session in 10s...")
                await asyncio.sleep(10)

        except Exception as e:
            log_error(f"Fatal error: {e}")
            import traceback
            traceback.print_exc()
            log("Restarting in 30s...")
            await asyncio.sleep(30)


if __name__ == "__main__":
    log("=" * 55)
    log("MyToolsTown Server Bot - 24/7 Auto Earner")
    log("=" * 55)

    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        log("\nBot stopped by user")
    except Exception as e:
        log_error(f"Fatal: {e}")
        import traceback
        traceback.print_exc()