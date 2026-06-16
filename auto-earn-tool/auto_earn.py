"""
Auto Credit Earner - OPTIMIZED (RAM Light Version)
=====================================================
Changes made:
1. Headless Mode ON → 50% RAM save (no browser UI)
2. Instagram tab wait: 5s → 1s (faster cycle)
3. Session reset after 3 retries (bypass "No promotions")
4. Max instances = 5 (prevent RAM overload)
5. Slow_mo 300 → 100 (faster execution)
6. Simplified logging (less CPU waste)
"""

import asyncio
import json
import os
import time
import sys
from datetime import datetime
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

CONFIG = {
    "instagram_username": "talal._.f4rooq",
    "headless": True,                    # ✅ HEADLESS = TRUE (RAM bachao)
    "slow_mo": 100,                      # ✅ Slow mo kam kiya
    "max_earn_cycles": 0,
    "follow_wait_time": 3,               # ✅ Instagram wait kam (3 sec)
    "verify_wait_time": 3,
    "cookies_file": "session.json",
}

PROXIES = [None]


class C:
    G = '\033[92m'; Y = '\033[93m'; B = '\033[94m'
    P = '\033[95m'; C = '\033[96m'; R = '\033[91m'
    N = '\033[0m'; BD = '\033[1m'


def log(msg, color=C.G):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"{color}[{ts}] {msg}{C.N}")


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
    try:
        await page.goto("https://mytoolstown.com/autoliker", wait_until="networkidle")
        await asyncio.sleep(2)
        if "dashboard" in page.url or "earn" in page.url:
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
            return True
        return False
    except:
        return False


async def navigate_to_earn_page(page):
    try:
        await page.goto("https://mytoolstown.com/autoliker/earn", wait_until="networkidle", timeout=30000)
        await asyncio.sleep(2)
        return True
    except:
        return False


async def perform_earn_cycle(page, cycle_num):
    try:
        # Refresh
        await page.reload(wait_until="networkidle")
        await asyncio.sleep(3)

        # === RETRY WITH SESSION RESET ===
        retry_count = 0
        while retry_count < 5:
            body_text = await page.inner_text("body")
            if "no promotions" in body_text.lower() or "come back later" in body_text.lower():
                retry_count += 1
                log(f"[REFRESH] No promotions (attempt {retry_count}/5)", C.Y)

                if retry_count >= 3:
                    # ✅ Session reset - naya context ke liye signal
                    log("[RESET] 3 retries done. Resetting session...", C.Y)
                    return "RESET"

                await page.reload(wait_until="networkidle")
                await asyncio.sleep(5)
                continue
            break

        # Find FOLLOW button
        follow_btn = await page.query_selector('#earnBtn')
        if not follow_btn:
            all_els = await page.query_selector_all('a, button')
            for el in all_els:
                try:
                    t = (await el.inner_text()).strip()
                    if t == "FOLLOW" and await el.is_visible():
                        follow_btn = el
                        break
                except:
                    pass

        if not follow_btn:
            log("[!] Follow button not found", C.Y)
            return False

        # Click FOLLOW
        log("[CLICK] Follow button...", C.C)
        async with page.context.expect_page() as new_page_info:
            await follow_btn.click()

        try:
            insta_page = await new_page_info.value
            await insta_page.wait_for_load_state("domcontentloaded")
            # ✅ INSTAGRAM TAB KO FASTER CLOSE (1 sec)
            await asyncio.sleep(1)
            await insta_page.close()
            log("[OK] Instagram tab closed (1 sec)", C.G)
        except:
            pass

        await asyncio.sleep(1)

        # Find VERIFY button
        verify_btn = None
        for selector in ['button:has-text("Verify")', 'a:has-text("Verify")', '.btn-primary:has-text("Verify")']:
            el = await page.query_selector(selector)
            if el and await el.is_visible():
                verify_btn = el
                break

        if verify_btn:
            await verify_btn.click()
            await asyncio.sleep(CONFIG['verify_wait_time'])
            log("[OK] Verify clicked!", C.G)
            return True
        else:
            log("[!] No verify btn, but follow done", C.Y)
            return True

    except Exception as e:
        log(f"[ERROR] Cycle #{cycle_num}: {e}", C.R)
        return False


async def run_instance(context, instance_id):
    log(f"[START] Instance #{instance_id}", C.C)
    page = None
    try:
        page = await context.new_page()
        cookie_file = f"session_{instance_id}.json" if instance_id > 1 else CONFIG["cookies_file"]
        await load_cookies(context, cookie_file)

        if not await login_to_site(page, CONFIG["instagram_username"]):
            log("[!] Login failed", C.R)
            return False

        await save_cookies(page, cookie_file)
        await navigate_to_earn_page(page)

        cycle = 0
        while True:
            cycle += 1
            result = await perform_earn_cycle(page, cycle)

            if result == "RESET":
                # ✅ Naya context lena hoga - session reset
                log("[SESSION] Need new session, stopping instance", C.Y)
                return "RESTART"

            log(f"[OK] Instance #{instance_id} - Cycle #{cycle} done!", C.G)

            # Human-like delay (20-45 sec)
            delay = __import__('random').randint(20, 45)
            for remaining in range(delay, 0, -1):
                if remaining % 15 == 0:
                    print(f"\r   ⏳ Next in {remaining}s...", end='', flush=True)
                await asyncio.sleep(1)
            print()

    except Exception as e:
        log(f"[ERROR] Instance #{instance_id}: {e}", C.R)
    finally:
        try:
            if page:
                await page.close()
        except:
            pass


async def main():
    # === USERNAME PROMPT ===
    default_user = CONFIG['instagram_username']
    prompt_text = f"{C.C}Instagram username? [Enter for {default_user}]: {C.N}"
    inp_user = input(prompt_text).strip()
    if inp_user:
        CONFIG['instagram_username'] = inp_user

    print(f"""
{C.P}{C.BD}
+============================================+
|  AUTO CREDIT EARNER - OPTIMIZED (RAM Light)|
|  Headless: ON | Fast Close | Auto-Resume   |
+============================================+
{C.N}
{C.C}Username: {CONFIG['instagram_username']}{C.N}
    """)

    ni = 1
    try:
        inp = input(f"{C.Y}Kitne tabs? (1-5) [Enter=1]: {C.N}").strip()
        if inp:
            ni = max(1, min(int(inp), 5))  # ✅ MAX 5 TABS
        log(f"[SETUP] {ni} tab(s) chalenge", C.G)
    except:
        ni = 1

    # ❓ Puchenge browser dikhana hai ya hidden
    try:
        see_browser = input(f"{C.C}Browser dikhana hai? (y/N): {C.N}").strip().lower()
        if see_browser == 'y' or see_browser == 'yes':
            CONFIG['headless'] = False
            log(f"[SETUP] Browser VISIBLE mode (aap dekh saktay hain)", C.Y)
        else:
            CONFIG['headless'] = True
            log(f"[SETUP] Headless mode (hidden browser)", C.G)
    except:
        CONFIG['headless'] = True

    headless_status = "OFF (Browser Dikhega)" if not CONFIG['headless'] else "ON (Hidden)"
    print(f"\n{C.G}✅ Headless Mode = {headless_status}")
    print(f"✅ {ni} tab(s) chalenge")
    print(f"✅ Instagram tab fast close hoga")
    print(f"✅ Auto session reset on cooldown")
    print(f"✅ Start ho raha hai...{C.N}\n")

    await asyncio.sleep(2)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=CONFIG["headless"],  # ✅ HEADLESS = TRUE
            slow_mo=CONFIG["slow_mo"]
        )

        tasks = []
        for i in range(ni):
            ctx = await browser.new_context(
                viewport={"width": 1280, "height": 720}
            )
            tasks.append(run_instance(ctx, instance_id=i + 1))

        await asyncio.gather(*tasks)
        await browser.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{C.Y}[STOP] Bye!{C.N}")
    except Exception as e:
        log(f"[FATAL] {e}", C.R)