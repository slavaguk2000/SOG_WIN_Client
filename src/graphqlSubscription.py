from PyQt5.QtCore import QThread, pyqtSignal
from gql import Client, gql
from gql.transport.websockets import WebsocketsTransport

bible_books_query = gql("""
   query bibleBooks($bibleId: ID!) {
       bibleBooks(bibleId: $bibleId) {
         id
         name
         chapterCount
       }
   }
   """)

subscription_query = gql("""
subscription {
    activeSlideSubscription {
         id
        content
        location
        searchContent
    }
}
""")


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
                try:
                    bible_books_data = (await session.execute(bible_books_query,
                                                              variable_values={"bibleId": "0"}))['bibleBooks']
                except BaseException as e:
                    print(e)
                    bible_books_data = None

                print(bible_books_data)

                async for result in session.subscribe(subscription_query):
                    slide = result.get("activeSlideSubscription")
                    if slide:
                        try:
                            location = slide["location"]
                            self.parent.update_signal.emit({
                                'text': f"{location[-1]}. {slide['content']}",
                                'title': f'{bible_books_data[int(location[-3])]["name"] if bible_books_data else ""} {location[-2]}'
                            })
                        except BaseException as e:
                            print(e)

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
