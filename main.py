import datetime
import time
import requests
from bs4 import BeautifulSoup


def return_text_if_not_none(element):
    if element:
        return element.text.strip()
    else:
        return ''


class LogFile:

    def __init__(self, filename):
        cur_time = datetime.datetime.now()
        self.filename_full = filename + "_" + cur_time.strftime(
            '%Y-%m-%d_%H-%M-%S') + ".log"
        self.fd = open(self.filename_full, 'w', encoding='utf-8')
        self.fd.write(
            f"{cur_time.strftime('%Y-%m-%d %H:%M:%S')}: Script started\n")
        self.fd.close()

    def open_to_add_records(self):
        self.fd = open(self.filename_full, 'a', encoding='utf-8')

    def write_shutdown(self):
        self.open_to_add_records()
        cur_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.fd.write(f"{cur_time}: Script shutdown\n")
        self.fd.close()

    def write_message(self, mess):
        self.open_to_add_records()
        cur_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.fd.write(cur_time + ": " + mess + "\n")
        self.fd.close()

    def write_article(self, news_mass):
        self.open_to_add_records()
        for title, author, summary, url, keywords in news_mass:
            self.fd.write(
                '=============================================================\n'
            )
            self.fd.write(f"Article title: {title}\n")
            self.fd.write(f"Author of article: {author}\n")
            self.fd.write(f"Article summary: {summary}\n")
            self.fd.write(f"Article URL: {url}\n")
            self.fd.write(
                f"Found Keywords in article: {', '.join(keywords)}\n")
            self.fd.write(
                '=============================================================\n'
            )
        self.fd.close()


class Scrapper:

    def __init__(self):
        self.processed_mass = set()
        self.site = "https://edition.cnn.com"
        self.keywords = ["Republican", "Democratic", "Democrats",
                         "GOP"]  # Ключевые слова для поиска

    def set_all_processed(self):
        response = requests.get(self.site)  # Запрос к главной странице
        response.raise_for_status()  # Проверка на успешный ответ от сервера
        soup = BeautifulSoup(
            response.text,
            'html.parser')  # Создание объекта BeautifulSoup для парсинга HTML

        articles = soup.find_all('a',
                                 attrs={'data-link-type': ['article']
                                        })  # Поиск всех статей на странице
        for article in articles:
            #print(article.get_text(strip=True))
            link = article.attrs['href']
            if link not in self.processed_mass:  # Проверка, не обрабатывалась ли статья ранее
                self.processed_mass.add(
                    link)  # Добавление URL в список обработанных

    def fetch_news(self):
        try:
            response = requests.get(self.site)  # Запрос к главной странице
            response.raise_for_status(
            )  # Проверка на успешный ответ от сервера
            soup = BeautifulSoup(
                response.text, 'html.parser'
            )  # Создание объекта BeautifulSoup для парсинга HTML
            news_list = []  # Список для хранения информации о новостях
            articles = soup.find_all('a',
                                     attrs={'data-link-type': ['article']
                                            })  # Поиск всех статей на странице
            for article in articles:
                #print(article.get_text(strip=True))
                link = article.attrs['href']

                if link not in self.processed_mass:  # Проверка, не обрабатывалась ли статья ранее
                    self.processed_mass.add(
                        link)  # Добавление URL в список обработанных

                    print(link)
                    headline, author, article_text, found_keywords, description = self.process_a_link(
                        link)
                    print("----")
                    print(headline)  # title
                    print(author)  # author
                    #print(article_text)  # article text
                    print(found_keywords)  #keywords
                    print(description)  #descr
                    print("----")

                    if found_keywords:  # Проверка на наличие ключевых слов
                        news_list.append(
                            (headline, author, description, link,
                             found_keywords))  # Добавление новости в список
                    print("===========================================")

            return news_list

        except Exception as e:
            print(f"Error fetching news: {e}")
            return []

    def process_a_link(self, link):
        try:
            response = requests.get(self.site +
                                    link)  # Запрос к главной странице
            response.raise_for_status(
            )  # Проверка на успешный ответ от сервера
            soup = BeautifulSoup(
                response.text, 'html.parser'
            )  # Создание объекта BeautifulSoup для парсинга HTML
            headline = soup.find('h1',
                                 class_='headline__text').get_text(strip=True)
            author = soup.find('div',
                               class_='byline__names').get_text(strip=True)
            article_text = soup.find(
                'div', class_='article__content').get_text(strip=True)
            description = soup.find('meta', attrs={
                'name': ['description']
            }).get('content')

            found_keywords = [
                keyword for keyword in self.keywords if keyword in article_text
            ]  # Поиск ключевых слов в тексте

            return headline, author, article_text, found_keywords, description
        except Exception as e:
            print(f"Error fetching article details: {e}")
            return "Unknown headline", "Unknown author", "", []


def main(duration_hours):
    print("CNN SCRAP STARTED")
    l_file = LogFile("CNN_news_util")
    scr = Scrapper()
    pause = 600  # Пауза между запусками в секундах

    i = 0
    end_time = datetime.datetime.now() + datetime.timedelta(
        hours=duration_hours)
    # Рассчитываем время окончания работы скрипта
    l_file.write_message("Writing ALL existing articles in processed_mass")
    scr.set_all_processed()

    while datetime.datetime.now() < end_time:
        l_file.write_message("starting cycle: " + str(i))
        print("starting cycle: " + str(i))
        news_mass = scr.fetch_news()  # Получаем список новостей
        l_file.write_article(news_mass)  # Записываем новости в лог-файл
        i += 1
        time.sleep(pause)  # Пауза перед следующим запросом

    l_file.write_shutdown()
    print("CNN SCRAP ENDED")


if __name__ == "__main__":
    main(4)
