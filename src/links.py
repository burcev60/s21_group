from bs4 import BeautifulSoup
import requests
import time

class Links:
    """
    Analyzing data from links.csv
    """
    def __init__(self, path_to_the_file):
        """
        Put here any fields that you think you will need.
        """
        self.path = path_to_the_file
        self.list_of_movies = self._get_list_of_movies()

    def _get_list_of_movies(self):
        movies_list = []
        is_first_line = True
        with open(self.path, "r") as file:
            for line in file:
                if is_first_line:
                    is_first_line = False
                else:
                    movies_list.append(line.split(',')[1].strip())
        return movies_list

    
    def get_imdb(self, list_of_movies = None, list_of_fields = None):
        """
        Метод возвращает список списков [movieId, field1, field2, field3, ...] для списка фильмов, указанных в качестве аргумента (movieId).
        Например, [movieId, Director, Budget, Cumulative Worldwide Gross, Runtime].
        Значения должны быть проанализированы с веб-страниц IMDB фильмов.
        Отсортируйте их по movieId по убыванию.
        """
        print("hello")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Referer": "https://www.imdb.com/",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "DNT": "1",  # Do Not Track
        }

        imdb_info = []
        film_id = 1
        for movie_id in self.list_of_movies:
            time.sleep(0.5)
            print(film_id)
            if film_id == 1000:
                break
            url = f"https://www.imdb.com/title/tt{movie_id}"

            try:
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
            except:
                continue

            soup = BeautifulSoup(response.text, 'html.parser')

            try:
                director = soup.find('li', {'data-testid': 'title-pc-principal-credit'}).find('a').text
            except:
                director = "Unknown"

            try:    
                budget = soup.find('li', {'data-testid': "title-boxoffice-budget"}).find('li').text
                budget = int(''.join(ch for ch in budget if ch.isdigit()))
            except:
                budget = 0

            try:
                world_widegross = soup.find('li', {'data-testid': "title-boxoffice-cumulativeworldwidegross"}).find('li').text
                world_widegross = int(''.join(ch for ch in world_widegross if ch.isdigit()))
            except:
                world_widegross = 0

            try:    
                runtime = soup.find('li', {'data-testid': 'title-techspec_runtime'}).find('div').text.split()
                runtime = int(runtime[0]) * 60 + int(runtime[2])
            except:
                runtime = 0

            try:    
                title = soup.find('h1', {'data-testid':"hero__pageTitle"}).text
            except:
                title = "Unknown"

            imdb_info.append([film_id, movie_id, title, director, budget, world_widegross, runtime])
            film_id += 1
        with open("../data/parsed_from_links.csv", "w") as file:
            file.write("movieId,ImdbId,Title,Director,Budget,Cumulative Worldwide Gross,runtime\n")
            for film in imdb_info:
                file.write(','.join([str(x) for x in film]) + '\n')
        return imdb_info
        
    # def top_directors(self, n):
    #     """
    #     Метод возвращает словарь с топ-n режиссерами, где ключи — режиссеры, а значения — номера фильмов, созданных ими. 
    #     Сортируем по номерам в порядке убывания.
    #     """
    #     return directors
        
    # def most_expensive(self, n):
    #     """
    #     Метод возвращает словарь с топ-n фильмами, где ключи — названия фильмов, а значения — их бюджеты. 
    #     Сортируйте его по убыванию бюджетов.
    #     """
    #     return budgets
        
    # def most_profitable(self, n):
    #     """
    #     Метод возвращает словарь с лучшими фильмами, где ключами являются названия фильмов, 
    #     а значениями — разница между совокупным мировым валовым сбором и бюджетом.
    #     Сортируйте его по разнице по убыванию.
    #     """
    #     return profits
        
    # def longest(self, n):
    #     """
    #     Метод возвращает словарь с top-n фильмами, где ключи — названия фильмов, а
    #     значения — их время выполнения. Если версий больше одной — выберите любую.
    #     Сортируйте по времени выполнения по убыванию.
    #     """
    #     return runtimes
        
    # def top_cost_per_minute(self, n):
    #     """
    #     Метод возвращает словарь с top-n фильмами, где ключами являются названия фильмов, а значениями — бюджеты, деленные на время их выполнения. 
    #     Бюджеты могут быть в разных валютах — не обращайте на это внимания.
    #     Значения должны быть округлены до 2 десятичных знаков. Отсортируйте их по делению по убыванию.
    #     """
    #     return costs


if __name__ == "__main__":
    link = Links("../data/links.csv")
    films_info = link.get_imdb(list_of_fields=['Directory'])
    for film in films_info:
        print(film)