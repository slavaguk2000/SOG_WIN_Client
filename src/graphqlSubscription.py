from PyQt5.QtCore import QThread, pyqtSignal
from gql import Client, gql
from gql.transport.websockets import WebsocketsTransport


class GraphQLSubscription:
    def __init__(self, url, main_window, parent):
        self.url = f'ws://{url}:8000'
        self.transport = WebsocketsTransport(url=self.url)
        self.main_window = main_window
        self.parent = parent

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
                        self.parent.update_signal.emit({'text': slide['content'], 'title': 'title'})
                    else:
                        self.parent.update_signal.emit({'text': '', 'title': ''})
        except BaseException as e:
            print(e)

    def stop_subscription(self):
        pass


class SubscriptionThread(QThread):
    update_signal = pyqtSignal(dict)

    def __init__(self, url, main_window):
        super().__init__()
        self.work = True
        self.subscriber = GraphQLSubscription(url, main_window, self)

    def run(self):
        import asyncio
        asyncio.run(self.subscriber.start_subscription())

    def stop(self):
        self.work = False
        self.subscriber.stop_subscription()
