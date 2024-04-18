import asyncio
import nodriver as uc

class BrowserManager:
    def __init__(self):
        self.browser = None
        self.main_tab = None
        self.username = None
        self.password = None

    async def launch_browser(self):
        try:
            self.browser = await uc.start()
        except Exception as e:
            print(f"Failed to launch browser: {e}")
            raise
        return self.browser

    async def launch_proxy_browser(self, ipPort, username, password):
        try:
            self.browser = await uc.start(
                browser_args=[f"--proxy-server={ipPort}"]
            )

            self.username = username
            self.password = password

            self.main_tab = await self.browser.get("draft:,")
            self.main_tab.add_handler(uc.cdp.fetch.RequestPaused, self.req_paused)
            self.main_tab.add_handler(
                uc.cdp.fetch.AuthRequired, self.auth_challenge_handler
            )
            await self.main_tab.send(uc.cdp.fetch.enable(handle_auth_requests=True))
            return self.browser
        except Exception as e:
            print(f"Failed to launch proxy browser: {e}")
            raise

    async def auth_challenge_handler(self, event: uc.cdp.fetch.AuthRequired):
        try:
            asyncio.create_task(
                self.main_tab.send(
                    uc.cdp.fetch.continue_with_auth(
                        request_id=event.request_id,
                        auth_challenge_response=uc.cdp.fetch.AuthChallengeResponse(
                            response="ProvideCredentials",
                            username=self.username,
                            password=self.password,
                        ),
                    )
                )
            )
        except Exception as e:
            print(f"Error handling authentication challenge: {e}")

    async def req_paused(self, event: uc.cdp.fetch.RequestPaused):
        try:
            asyncio.create_task(
                self.main_tab.send(
                    uc.cdp.fetch.continue_request(request_id=event.request_id)
                )
            )
        except Exception as e:
            print(f"Error while continuing paused request: {e}")
