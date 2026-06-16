"""
Lightweight Auto Credit Earner - MyToolsTown
=============================================
Zero browser required. Uses only Python 'requests' library.
Automatically detects cooldown, waits, and resumes.

Features:
- No browser needed (runs in terminal, ~30MB RAM)
- Intelligent cooldown detection & progressive backoff
- Fresh session rotation every N successes
- Random User-Agent rotation
- Human-like delays (20-50 sec)
- Long breaks every 5-10 successes
- Auto-resume - never stops
"""

import requests
import time
import random
import sys
from datetime import datetime

# Windows Unicode fix
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except:
    pass


class C:
    G = '\033[92m'
    Y = '\033[93m'
    B = '\033[94m'
    P = '\033[95m'
    C = '\033[96m'
    R = '\033[91m'
    N = '\033[0m'
    BD = '\033[1m'


def log(msg, color=C.G):
    ts = datetime.now().strftime("%H:%M:%S")
    try:
        print(f"{color}[{ts}] {msg}{C.N}")
    except:
        print(f"[{ts}] {msg.encode('ascii', errors='replace').decode('ascii')}")


class LightweightBot:
    def __init__(self, username):
        self.username = username
        self.session = None
        self.coins_earned = 0
        self.success_count = 0
        self.cooldown_count = 0
        self.total_attempts = 0
        self.session_requests = 0
        self.max_requests_per_session = random.randint(6, 10)  # Fresh session after this many

        self.base_url = "https://mytoolstown.com/autoliker/earn"
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
        ]
        self.cooldown_phrases = [
            "no promotions available",
            "no promotion available",
            "promotions available",
            "come back later",
            "add a promotion",
            "promote your instagram",
            "try again later",
            "too many requests",
        ]

    def get_headers(self):
        """Generate random headers for each request"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,ur;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://mytoolstown.com/',
            'Origin': 'https://mytoolstown.com',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
        }

    def create_fresh_session(self):
        """Create a completely new session (new identity)"""
        self.session = requests.Session()
        self.session_requests = 0
        log("🔄 Fresh session created (new cookies, new identity)", C.B)
        # Small delay after new session
        time.sleep(random.uniform(1, 3))

    def check_cooldown(self, text):
        """Check if response contains cooldown/block message"""
        text_lower = text.lower()
        for phrase in self.cooldown_phrases:
            if phrase in text_lower:
                return True
        return False

    def extract_credits(self, text):
        """Extract current credit count from page HTML"""
        import re
        # Look for "Your Credits : 35" pattern
        match = re.search(r'Your Credits\s*:\s*(\d+)', text, re.IGNORECASE)
        if match:
            return int(match.group(1))
        # Alternative pattern
        match = re.search(r'Credits[^\d]*?(\d+)', text, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return None

    def wait_for_cooldown(self):
        """Progressive backoff - wait longer each time"""
        self.cooldown_count += 1
        self.success_count = 0  # Reset success streak

        if self.cooldown_count <= 2:
            wait_time = random.randint(300, 420)  # 5-7 min
        elif self.cooldown_count <= 4:
            wait_time = random.randint(600, 900)  # 10-15 min
        elif self.cooldown_count <= 6:
            wait_time = random.randint(900, 1200)  # 15-20 min
        else:
            wait_time = random.randint(1200, 1800)  # 20-30 min

        log(f"⏸️  Cooldown #{self.cooldown_count}! Waiting {wait_time//60} min {wait_time%60}s...", C.Y)
        log(f"   Resume at: {datetime.fromtimestamp(time.time() + wait_time).strftime('%I:%M:%S %p')}", C.C)

        for remaining in range(wait_time, 0, -1):
            if remaining % 60 == 0:
                mins = remaining // 60
                secs = remaining % 60
                print(f"\r   ⏳ {mins}m {secs}s remaining...", end='', flush=True)
            time.sleep(1)
        print()

        # If cooldown happened too many times, completely reset
        if self.cooldown_count >= 5:
            log("🔄 Hard reset - new session after prolonged cooldown", C.B)
            self.create_fresh_session()
            self.cooldown_count = 0

    def do_earn_attempt(self):
        """Single earn attempt - verifies actual credit increase on website"""
        self.total_attempts += 1

        # Create fresh session if needed
        if self.session is None:
            self.create_fresh_session()

        headers = self.get_headers()

        try:
            # Step 1: Visit earn page and get current credits
            resp_before = self.session.get(self.base_url, headers=headers, timeout=15)
            time.sleep(random.uniform(2, 4))

            if self.check_cooldown(resp_before.text):
                return False

            credits_before = self.extract_credits(resp_before.text)
            log(f"💰 Credits before: {credits_before if credits_before else 'unknown'}", C.B)

            # Step 2: Submit username (POST) - this logs in
            resp_login = self.session.post(
                self.base_url,
                data={'username': self.username},
                headers=headers,
                timeout=15
            )
            time.sleep(random.uniform(2, 3))

            if self.check_cooldown(resp_login.text):
                return False

            # Step 3: Try earn endpoints - the site might use various URLs
            earn_endpoints = [
                f"{self.base_url}/claim",
                f"{self.base_url}/follow",
                f"{self.base_url}/earn",
            ]
            for endpoint in earn_endpoints:
                try:
                    resp_earn = self.session.get(endpoint, headers=headers, timeout=15)
                    time.sleep(random.uniform(1, 2))
                    if self.check_cooldown(resp_earn.text):
                        return False
                except:
                    pass

            # Step 4: Visit earn page again to check if credits increased
            resp_after = self.session.get(self.base_url, headers=headers, timeout=15)
            time.sleep(random.uniform(2, 3))

            if self.check_cooldown(resp_after.text):
                return False

            credits_after = self.extract_credits(resp_after.text)

            # Step 5: Verify actual credit increase
            if credits_before is not None and credits_after is not None:
                diff = credits_after - credits_before
                if diff > 0:
                    # REAL success - credits actually increased!
                    self.coins_earned += diff
                    self.success_count += 1
                    self.session_requests += 1
                    self.cooldown_count = 0
                    log(f"✅ REAL +{diff} coins (Website: {credits_before} → {credits_after}) | Total: {self.coins_earned}", C.G)
                    return True
                else:
                    # Credits didn't increase - follow/verify flow failed
                    log(f"❌ Fake! Credits not changed ({credits_before} → {credits_after})", C.Y)
                    log(f"   This site requires browser (Instagram tab) to earn", C.R)
                    return "BROWSER_REQUIRED"
            else:
                # Couldn't find credits on page
                log(f"❌ Could not read credits from page", C.Y)
                if credits_before is None:
                    log(f"   Debug: page may require login first", C.C)
                return False

        except requests.exceptions.Timeout:
            log("⚠️  Request timeout", C.Y)
            return None
        except requests.exceptions.ConnectionError:
            log("⚠️  Connection error", C.Y)
            return None
        except Exception as e:
            log(f"⚠️  Error: {e}", C.R)
            return None

    def run(self):
        """Main bot loop"""
        print(f"""
{C.P}{C.BD}
+============================================+
|    LIGHTWEIGHT AUTO CREDIT EARNER          |
|    MyToolsTown - Requests Based Bot        |
|    Zero Browser Required!                  |
+============================================+
{C.N}
{C.C}Username: {self.username}{C.N}
{C.C}Max requests per session: {self.max_requests_per_session}{C.N}
{C.C}Cooldown detection: Smart Progressive Backoff{C.N}
{C.C}Auto-resume: ✅ Will never stop{C.N}
        """)

        log("🚀 Bot started! First attempt incoming...", C.BD + C.G)
        log("📌 Tip: Let it run in background. It handles cooldowns automatically.", C.C)
        print(f"{'='*55}\n")

        while True:
            try:
                # Check if we need a fresh session (rotation)
                if self.session_requests >= self.max_requests_per_session:
                    log(f"🔄 Session rotation after {self.session_requests} requests", C.B)
                    self.create_fresh_session()
                    self.max_requests_per_session = random.randint(6, 10)

                result = self.do_earn_attempt()

                if result == "BROWSER_REQUIRED":
                    # This site can't earn via requests - needs browser
                    log("", C.N)
                    log("═" * 55, C.R)
                    log("❌ THIS SITE REQUIRES A BROWSER TO EARN!", C.BD + C.R)
                    log("   Requests-based bot can't complete the Follow→Verify flow.", C.Y)
                    log("   Instagram tab needs to open & close - only browser can do that.", C.Y)
                    log("", C.Y)
                    log("✅ Use the Playwright bot instead:", C.G)
                    log("   Run Playwright Bot.bat  OR  python auto_earn.py", C.G)
                    log("═" * 55, C.R)
                    log("", C.N)
                    return  # Exit the bot loop

                if result is False:
                    # Cooldown detected
                    log("🚫 Cooldown detected! Waiting...", C.Y)
                    self.wait_for_cooldown()
                    continue
                elif result is None:
                    # Network error - wait shorter
                    log("⚠️  Network issue, waiting 30s...", C.Y)
                    time.sleep(30)
                    continue

                # Every 5-8 successes, take a longer break (human-like)
                if self.success_count % 5 == 0 and self.success_count > 0:
                    break_time = random.randint(120, 180)  # 2-3 min
                    log(f"☕ Long break: {break_time//60}m {break_time%60}s (anti-detection)", C.P)
                    for remaining in range(break_time, 0, -1):
                        if remaining % 30 == 0:
                            print(f"\r   💤 {remaining}s break remaining...", end='', flush=True)
                        time.sleep(1)
                    print()

                # Human-like delay between attempts (20-50 seconds)
                delay = random.randint(20, 50)
                print(f"{C.C}   ⏱️  Next attempt in {delay}s...{C.N}")
                for remaining in range(delay, 0, -1):
                    if remaining % 10 == 0 and remaining > 0:
                        print(f"\r   ⏳ {remaining}s...", end='', flush=True)
                    time.sleep(1)
                print()

            except KeyboardInterrupt:
                print(f"\n{C.Y}[{datetime.now().strftime('%H:%M:%S')}] Bot stopped by user{C.N}")
                self.print_summary()
                break
            except Exception as e:
                log(f"⚠️  Unexpected error: {e}", C.R)
                time.sleep(30)
                continue

    def print_summary(self):
        """Print final summary"""
        print(f"""
{C.BD}{'='*55}{C.N}
{C.P}📊 FINAL SUMMARY{C.N}
{C.BD}{'='*55}{C.N}
{C.G}✅ Total coins earned: {self.coins_earned}{C.N}
{C.B}📈 Total attempts:    {self.total_attempts}{C.N}
{C.Y}⚡ Success rate:      {self.success_count}/{self.total_attempts} ({self.success_count/max(self.total_attempts,1)*100:.0f}%){C.N}
{C.BD}{'='*55}{C.N}
        """)


def main():
    import os
    import json

    # Load config if exists
    default_username = None
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
                default_username = config_data.get('instagram_username', '')
        except:
            pass

    # Always ask for username (shows default in brackets)
    if default_username:
        prompt_text = f"{C.C}Instagram username? [Enter for {default_username}]: {C.N}"
    else:
        prompt_text = f"{C.C}Enter Instagram username: {C.N}"

    username = input(prompt_text).strip()
    if not username:
        if default_username:
            username = default_username
        else:
            print(f"{C.R}Username required!{C.N}")
            return

    bot = LightweightBot(username)
    bot.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{C.Y}[STOP] Bye!{C.N}")
    except Exception as e:
        log(f"[FATAL] {e}", C.R)
        import traceback
        traceback.print_exc()