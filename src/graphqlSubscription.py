from PyQt5.QtCore import QThread
from gql import Client, gql
from gql.transport.websockets import WebsocketsTransport


class GraphQLSubscription:
    def __init__(self, url, main_window):
        self.url = f'ws://{url}:8000'
        self.transport = WebsocketsTransport(url=self.url)
        self.main_window = main_window

    async def start_subscription(self):
        try:
            async with Client(
                transport=self.transport,
                fetch_schema_from_transport=True,
            ) as session:
                # Определите запрос на подписку
                query = gql("""
                subscription {
                    activeSlideSubscription {
                         id
                        content
                        location
                        searchContent
                    }
                }
                """)

                async for result in session.subscribe(query):
                    slide = result.get("activeSlideSubscription")
                    if slide:
                        self.main_window.setup_text(slide['content'], 'title')
                    else:
                        self.main_window.setup_text('', '')
        except BaseException as e:
            print(e)

    def stop_subscription(self):
        pass


class SubscriptionThread(QThread):
    def __init__(self, url, main_window):
        super().__init__()
        self.work = True
        self.subscriber = GraphQLSubscription(url, main_window)

    def run(self):
        import asyncio
        while self.work:
            asyncio.run(self.subscriber.start_subscription())

    def stop(self):
        self.work = False
        self.subscriber.stop_subscription()
