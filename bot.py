from aiohttp import (
    ClientResponseError,
    ClientSession,
    ClientTimeout
)
from aiohttp_socks import ProxyConnector
from fake_useragent import FakeUserAgent
from datetime import datetime
from colorama import *
import asyncio, random, base64, uuid, json, os, pytz

wib = pytz.timezone('Asia/Jakarta')

class OepnLedger:
    def __init__(self) -> None:
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": "https://testnet.openledger.xyz",
            "Referer": "https://testnet.openledger.xyz/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": FakeUserAgent().random
        }
        self.extension_id = "chrome-extension://ekbbplmjjgoobhdlffmgeokalelnmjjc"
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(
            f"""
        {Fore.GREEN + Style.BRIGHT}Auto Ping {Fore.BLUE + Style.BRIGHT}Oepn Ledger - BOT
            """
            f"""
        {Fore.GREEN + Style.BRIGHT}Rey? {Fore.YELLOW + Style.BRIGHT}<INI WATERMARK>
            """
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    async def load_proxies(self, use_proxy_choice: int):
        filename = "proxy.txt"
        try:
            if use_proxy_choice == 1:
                async with ClientSession(timeout=ClientTimeout(total=30)) as session:
                    async with session.get("https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/all.txt") as response:
                        response.raise_for_status()
                        content = await response.text()
                        with open(filename, 'w') as f:
                            f.write(content)
                        self.proxies = content.splitlines()
            else:
                if not os.path.exists(filename):
                    self.log(f"{Fore.RED + Style.BRIGHT}File {filename} Not Found.{Style.RESET_ALL}")
                    return
                with open(filename, 'r') as f:
                    self.proxies = f.read().splitlines()
            
            if not self.proxies:
                self.log(f"{Fore.RED + Style.BRIGHT}No Proxies Found.{Style.RESET_ALL}")
                return

            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Proxies Total  : {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(self.proxies)}{Style.RESET_ALL}"
            )
        
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed To Load Proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        return f"http://{proxies}"

    def get_next_proxy_for_account(self, account):
        if account not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[account] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[account]

    def rotate_proxy_for_account(self, account):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[account] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy
    
    def generate_random_id(self):
        random_id = str(uuid.uuid4())
        return random_id
        
    def generate_worker_id(self, account: str):
        identity = base64.b64encode(account.encode("utf-8")).decode("utf-8")
        return identity
    
    def mask_account(self, account):
        mask_account = account[:6] + '*' * 6 + account[-6:]
        return mask_account

    def print_message(self, account, proxy, color, message):
        self.log(
            f"{Fore.CYAN + Style.BRIGHT}[ Account:{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(account)} {Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT} Proxy: {Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT}{proxy}{Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}Status:{Style.RESET_ALL}"
            f"{color + Style.BRIGHT} {message} {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
        )

    def print_question(self):
        while True:
            try:
                print("1. Run With Monosans Proxy")
                print("2. Run With Private Proxy")
                print("3. Run Without Proxy")
                choose = int(input("Choose [1/2/3] -> ").strip())

                if choose in [1, 2, 3]:
                    proxy_type = (
                        "Run With Monosans Proxy" if choose == 1 else 
                        "Run With Private Proxy" if choose == 2 else 
                        "Run Without Proxy"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}{proxy_type} Selected.{Style.RESET_ALL}")
                    return choose
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2 or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2 or 3).{Style.RESET_ALL}")

    async def generate_token(self, account: str, proxy=None):
        url = "https://apitn.openledger.xyz/api/v1/auth/generate_token"
        data = json.dumps({"address":account})
        headers = {
            "Content-Type": "application/json"
        }
        connector = ProxyConnector.from_url(proxy) if proxy else None
        try:
            async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                async with session.post(url=url, headers=headers, data=data) as response:
                    response.raise_for_status()
                    result = await response.json()
                    return result['data']['token']
        except (Exception, ClientResponseError) as e:
            return self.print_message(account, proxy, Fore.RED, f"GET Access Token Failed: {Fore.YELLOW + Style.BRIGHT}{str(e)}")
        
    async def user_reward(self, account: str, token: str, proxy=None, retries=5):
        url = "https://rewardstn.openledger.xyz/api/v1/reward"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"

        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        if response.status == 401:
                            token = await self.get_access_token(account, proxy)
                            headers["Authorization"] = f"Bearer {token}"
                            continue

                        response.raise_for_status()
                        result = await response.json()
                        return result['data']
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                
                return self.print_message(account, proxy, Fore.RED, f"GET User Reward Failed: {Fore.YELLOW + Style.BRIGHT}{str(e)}")
                
    async def realtime_reward(self, account: str, token: str, proxy=None, retries=5):
        url = "https://rewardstn.openledger.xyz/api/v1/reward_realtime"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"

        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        if response.status == 401:
                            token = await self.get_access_token(account, proxy)
                            headers["Authorization"] = f"Bearer {token}"
                            continue

                        response.raise_for_status()
                        result = await response.json()
                        return result['data'][0]['total_heartbeats']
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                
                return self.print_message(account, proxy, Fore.RED, f"GET Today Heartbeat Failed: {Fore.YELLOW + Style.BRIGHT}{str(e)}")
    
    async def checkin_details(self, account: str, token: str, proxy=None, retries=5):
        url = "https://rewardstn.openledger.xyz/api/v1/claim_details"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"

        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        if response.status == 401:
                            token = await self.get_access_token(account, proxy)
                            headers["Authorization"] = f"Bearer {token}"
                            continue
                        
                        response.raise_for_status()
                        result = await response.json()
                        return result['data']
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                
                return self.print_message(account, proxy, Fore.RED, f"GET Daily Check-In Data Failed: {Fore.YELLOW + Style.BRIGHT}{str(e)}")
    
    async def claim_checkin_reward(self, account: str, token: str, proxy=None, retries=5):
        url = "https://rewardstn.openledger.xyz/api/v1/claim_reward"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"

        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        if response.status == 401:
                            token = await self.get_access_token(account, proxy)
                            headers["Authorization"] = f"Bearer {token}"
                            continue
                        
                        response.raise_for_status()
                        result = await response.json()
                        return result['data']
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                
                return self.print_message(account, proxy, Fore.RED, f"Claim Daily Check-In Reward Failed: {Fore.YELLOW + Style.BRIGHT}{str(e)}")
    
    async def tier_details(self, account: str, token: str, proxy=None, retries=5):
        url = "https://rewardstn.openledger.xyz/api/v1/tier_details"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"

        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        if response.status == 401:
                            token = await self.get_access_token(account, proxy)
                            headers["Authorization"] = f"Bearer {token}"
                            continue
                        
                        response.raise_for_status()
                        result = await response.json()
                        return result['data']['tierDetails']
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                
                return self.print_message(account, proxy, Fore.RED, f"GET Tier Data Failed: {Fore.YELLOW + Style.BRIGHT}{str(e)}")
    
    async def claim_tier_reward(self, account: str, token: str, tier_id: int, proxy=None, retries=5):
        url = "https://rewardstn.openledger.xyz/api/v1/claim_tier"
        data = json.dumps({"tierId":tier_id})
        headers = {
            **self.headers,
            "Authorization": f"Bearer {token}",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"

        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.put(url=url, headers=headers, data=data) as response:
                        if response.status == 401:
                            token = await self.get_access_token(account, proxy)
                            headers["Authorization"] = f"Bearer {token}"
                            continue
                        elif response.status == 420:
                            return None
                        
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                
                return self.print_message(account, proxy, Fore.RED, f"Claim Tier Reward Failed: {Fore.YELLOW + Style.BRIGHT}{str(e)}")
            
    async def process_user_earning(self, account: str, token: str, use_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(account) if use_proxy else None

            epoch_name = "Epoch N/A"
            total_point = 0
            today_heartbeat = 0

            user = await self.user_reward(account, token, proxy)
            if user:
                epoch_name = user.get('name', 'Epoch N/A')
                total_point = float(user.get('totalPoint', 0))
            await asyncio.sleep(3)

            realtime_reward = await self.realtime_reward(account, token, proxy)
            if realtime_reward:
                today_heartbeat = float(realtime_reward)
            await asyncio.sleep(3)

            self.print_message(account, proxy, Fore.WHITE,
                f"Earning {epoch_name}"
                f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}Today {today_heartbeat} PTS{Style.RESET_ALL}"
                f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}Total {total_point} PTS{Style.RESET_ALL}"
            )
            await asyncio.sleep(15 * 60)

    async def process_claim_checkin_reward(self, account: str, token: str, use_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(account) if use_proxy else None
            checkin = await self.checkin_details(account, token, proxy)
            if checkin:
                is_claimed = checkin['claimed']
                reward = checkin['dailyPoint']

                if not is_claimed:
                    claim = await self.claim_checkin_reward(account, token, proxy)

                    if claim and claim['claimed']:
                        self.print_message(account, proxy, Fore.GREEN,
                            f"Daily Check-In Reward Is Claimed "
                            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT} Reward: {Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT}{reward} PTS{Style.RESET_ALL}"
                        )
                    else:
                        self.print_message(account, proxy, Fore.RED,
                            "Daily Check-In Reward Isn't Claimed"
                        )
                else:
                    self.print_message(account, proxy, Fore.YELLOW,
                        "Daily Check-In Reward Is Already Claimed"
                    )
            await asyncio.sleep(12 * 60 * 60)

    async def process_claim_tier_reward(self, account: str, token: str, use_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(account) if use_proxy else None
            tiers = await self.tier_details(account, token, proxy)
            if tiers:
                for tier in tiers:
                    tier_id = tier['id']
                    tier_name = tier['name']
                    reward = tier['value']
                    is_claimed = tier['claimStatus']

                    if tier and not is_claimed:
                        claim = await self.claim_tier_reward(account, token, tier_id, proxy)

                        if claim and claim['status'] == "SUCCESS":
                            self.print_message(account, proxy, Fore.WHITE,
                                f"Tier {tier_name}"
                                f"{Fore.GREEN + Style.BRIGHT} Is Claimed {Style.RESET_ALL}"
                                f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                f"{Fore.CYAN + Style.BRIGHT} Reward: {Style.RESET_ALL}"
                                f"{Fore.WHITE + Style.BRIGHT}{reward} PTS{Style.RESET_ALL}"
                            )
                        else:
                            self.print_message(account, proxy, Fore.WHITE,
                                f"Tier {tier_name} "
                                f"{Fore.YELLOW + Style.BRIGHT}Not Eligible To Claim{Style.RESET_ALL}"
                            )

                        await asyncio.sleep(3)

            await asyncio.sleep(24 * 60 * 60)

    async def connect_websocket(self, account: str, token: str, use_proxy: bool):
        wss_url = f"wss://apitn.openledger.xyz/ws/v1/orch?authToken={token}"
        headers = {
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Cache-Control": "no-cache",
            "Connection": "Upgrade",
            "Host": "apitn.openledger.xyz",
            "Origin": self.extension_id,
            "Pragma": "no-cache",
            "Sec-Websocket-Extensions": "permessage-deflate; client_max_window_bits",
            "Sec-Websocket-Key": "pyAFsQgNHYvbq16if2s6Bw==",
            "Sec-Websocket-Version": "13",
            "Upgrade": "websocket",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        }
        connected = False
        
        identity = self.generate_worker_id(account)
        memory = round(random.uniform(0, 32), 2)
        storage = str(round(random.uniform(0, 500), 2))

        while True:
            proxy = self.get_next_proxy_for_account(account) if use_proxy else None
            connector = ProxyConnector.from_url(proxy) if proxy else None
            session = ClientSession(connector=connector, timeout=ClientTimeout(total=60))
            try:
                async with session.ws_connect(wss_url, headers=headers) as wss:
                    async def send_heartbeat_message():
                        while True:
                            heartbeat_message = {
                                "message": {
                                    "Worker": {
                                        "Identity": identity,
                                        "ownerAddress": account,
                                        "type": "LWEXT",
                                        "Host": self.extension_id
                                    },
                                    "Capacity": {
                                        "AvailableMemory": memory,
                                        "AvailableStorage": storage,
                                        "AvailableGPU": "",
                                        "AvailableModels": []
                                    }
                                },
                                "msgType": "HEARTBEAT",
                                "workerType": "LWEXT",
                                "workerID": identity
                            }
                            await asyncio.sleep(30)
                            await wss.send_json(heartbeat_message)
                            self.print_message(account, proxy, Fore.WHITE, 
                                f"Worker ID {self.mask_account(identity)}"
                                f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                                f"{Fore.GREEN + Style.BRIGHT}Sent Heartbeat Success{Style.RESET_ALL}"
                            )

                    if not connected:
                        register_message = {
                            "workerID": identity,
                            "msgType": "REGISTER",
                            "workerType": "LWEXT",
                            "message": {
                                "id": self.generate_random_id(),
                                "type": "REGISTER",
                                "worker": {
                                    "host": self.extension_id,
                                    "identity": identity,
                                    "ownerAddress": account,
                                    "type": "LWEXT"
                                }
                            }
                        }
                        await wss.send_json(register_message)
                        self.print_message(account, proxy, Fore.WHITE, 
                            f"Worker ID {self.mask_account(identity)}"
                            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                            f"{Fore.GREEN + Style.BRIGHT}Websocket Is Connected{Style.RESET_ALL}"
                        )
                        connected = True
                        send_ping = asyncio.create_task(send_heartbeat_message())

                    while connected:
                        try:
                            response = await wss.receive_json()
                            if response.get("status", False):
                                self.print_message(account, proxy, Fore.WHITE, 
                                    f"Worker ID {self.mask_account(identity)} "
                                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                    f"{Fore.GREEN + Style.BRIGHT} Received Message: {Style.RESET_ALL}"
                                    f"{Fore.BLUE + Style.BRIGHT}{response}{Style.RESET_ALL}"
                                )

                        except Exception as e:
                            self.print_message(account, proxy, Fore.WHITE, 
                                f"Worker ID {self.mask_account(identity)} "
                                f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                                f"{Fore.RED + Style.BRIGHT} Websocket Connection Closed: {Style.RESET_ALL}"
                                f"{Fore.YELLOW + Style.BRIGHT}{str(e)}{Style.RESET_ALL}"
                            )
                            if send_ping:
                                send_ping.cancel()
                                try:
                                    await send_ping
                                except asyncio.CancelledError:
                                    self.print_message(account, proxy, Fore.WHITE, 
                                        f"Worker ID {self.mask_account(identity)}"
                                        f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                                        f"{Fore.YELLOW + Style.BRIGHT}Sent Heartbeat Cancelled{Style.RESET_ALL}"
                                    )

                            await asyncio.sleep(5)
                            connected = False
                            break

            except Exception as e:
                self.print_message(account, proxy, Fore.WHITE, 
                    f"Worker ID {self.mask_account(identity)} "
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.RED + Style.BRIGHT} Websocket Not Connected: {Style.RESET_ALL}"
                    f"{Fore.YELLOW + Style.BRIGHT}{str(e)}{Style.RESET_ALL}"
                )

                proxy = self.rotate_proxy_for_account(account) if use_proxy else None
                await asyncio.sleep(5)

            except asyncio.CancelledError:
                self.print_message(account, proxy, Fore.WHITE, 
                    f"Worker ID {self.mask_account(identity)}"
                    f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                    f"{Fore.YELLOW + Style.BRIGHT}Websocket Closed{Style.RESET_ALL}"
                )
                break
            finally:
                await session.close()
        
    async def get_access_token(self, account: str, use_proxy: bool):
        proxy = self.get_next_proxy_for_account(account) if use_proxy else None
        token = None
        while token is None:
            token = await self.generate_token(account, proxy)
            if not token:
                proxy = self.rotate_proxy_for_account(account) if use_proxy else None
                continue

            self.print_message(account, proxy, Fore.GREEN, "GET Access Token Success")
            return token
        
    async def process_accounts(self, account: str, use_proxy: bool):
        token = await self.get_access_token(account, use_proxy)
        if token:
            tasks = []
            tasks.append(self.process_user_earning(account, token, use_proxy))
            tasks.append(self.process_claim_checkin_reward(account, token, use_proxy))
            tasks.append(self.process_claim_tier_reward(account, token, use_proxy))
            tasks.append(self.connect_websocket(account, token, use_proxy))
            await asyncio.gather(*tasks)

    async def main(self):
        try:
            with open('accounts.txt', 'r') as file:
                accounts = [line.strip() for line in file if line.strip()]
            
            use_proxy_choice = self.print_question()

            use_proxy = False
            if use_proxy_choice in [1, 2]:
                use_proxy = True

            self.clear_terminal()
            self.welcome()
            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(accounts)}{Style.RESET_ALL}"
            )

            if use_proxy:
                await self.load_proxies(use_proxy_choice)

            self.log(f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}"*75)

            while True:
                tasks = []
                for account in accounts:
                    if account:
                        tasks.append(self.process_accounts(account, use_proxy))

                await asyncio.gather(*tasks)
                await asyncio.sleep(10)

        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")
            raise e

if __name__ == "__main__":
    try:
        bot = OepnLedger()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] Open Ledger - BOT{Style.RESET_ALL}                                       "                              
        )