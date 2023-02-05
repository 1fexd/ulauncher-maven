from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction

from bs4 import BeautifulSoup
import requests


class MavenRepositoryExtension(Extension):

    def __init__(self):
        super().__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())


class KeywordQueryEventListener(EventListener):
    __GOOGLE_WEB_CACHE_PREFIX = "https://webcache.googleusercontent.com/search?q=cache:"
    __MAVEN_BASE_URL = "https://mvnrepository.com"

    def on_event(self, event: KeywordQueryEvent, extension: MavenRepositoryExtension):
        open_latest = extension.preferences.get("latest") == "Yes"

        items = []
        argument = event.get_argument()
        if argument is not None and len(argument) > 0:
            resp = requests.get(f"{self.__GOOGLE_WEB_CACHE_PREFIX}{self.__MAVEN_BASE_URL}/search?q={argument}",
                                headers={"Host": "webcache.googleusercontent.com",
                                         "Sec-Fetch-Dest": "document",
                                         "Sec-Fetch-Mode": "navigate",
                                         "Sec-Fetch-Site": "none",
                                         "Sec-Fetch-User": "?1",
                                         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                                                       "(KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36"})

            soup = BeautifulSoup(resp.text, features="html5lib")
            for child in soup.find_all("div", class_="im"):
                link = child.find("a")["href"]
                title = child.find("h2", class_="im-title").find("a").text
                subtitle = child.find("p", class_="im-subtitle")

                anchors = subtitle.find_all("a")
                desc = anchors[0].text + " » " + anchors[1].text

                item_url = f"{self.__MAVEN_BASE_URL}{link}"
                if open_latest:
                    item_url += "/latest"

                items.append(ExtensionResultItem(icon="images/icon.png", name=title,
                                                 description=desc,
                                                 on_enter=OpenUrlAction(item_url)))

        return RenderResultListAction(items)


if __name__ == '__main__':
    MavenRepositoryExtension().run()
