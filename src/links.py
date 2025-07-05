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
        self.data = self._get_data()

    def _get_data(self):
        data = []
        is_first_line = True
        with open("../data/parsed_from_links.csv", "r", encoding="utf-8") as file:
            for line in file:
                if is_first_line:
                    is_first_line = False
                else:
                    line = line.strip()  
                    line_parts = []
                    string = ""
                    has_quotes = False

                    for ch in line:
                        if ch == '"':
                            has_quotes = not has_quotes
                        if ch == "," and not has_quotes:
                            line_parts.append(string)
                            string = ""
                        else:
                            string += ch

                    line_parts.append(string)

                    data.append(line_parts)
        return data

    def _get_list_of_movies(self):
        movies_list = []
        with open(self.path, "r") as file:
            for line in file:
                movies_list.append(line.split(',')[1].strip())
        return movies_list

    
    def get_imdb(self, list_of_movies= None, list_of_fields = None):
        """
        Метод возвращает список списков [movieId, field1, field2, field3, ...] для списка фильмов, указанных в качестве аргумента (movieId).
        Например, [movieId, Director, Budget, Cumulative Worldwide Gross, Runtime].
        Значения должны быть проанализированы с веб-страниц IMDB фильмов.
        Отсортируйте их по movieId по убыванию.
        """
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
        for movie_id in list_of_movies if list_of_movies is not None else self.list_of_movies:
            time.sleep(0.5)

            url = f"https://www.imdb.com/title/tt{movie_id}"

            try:
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
            except:
                continue

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
                worldwide_gross = soup.find('li', {'data-testid': "title-boxoffice-cumulativeworldwidegross"}).find('li').text
                worldwide_gross = int(''.join(ch for ch in worldwide_gross if ch.isdigit()))
            except:
                worldwide_gross = 0

            try:    
                runtime = soup.find('li', {'data-testid': 'title-techspec_runtime'}).find('div').text.split()
                runtime = int(runtime[0]) * 60 + int(runtime[2])
            except:
                runtime = 0

            try:    
                title = soup.find('h1', {'data-testid':"hero__pageTitle"}).text
            except:
                title = "Unknown"

            film_info = [movie_id]
            for field in list_of_fields:
                if field == "Director": film_info.append(director)
                elif field == "Budget": film_info.append(budget)
                elif field == "Cumulative Worldwide Gross": film_info.append(worldwide_gross)
                elif field == "Runtime": film_info.append(runtime)
                elif field == "Title": film_info.append(title)
            
            imdb_info.append(film_info)

        imdb_info = sorted(imdb_info, key = lambda film: film[0], reverse= True )
        return imdb_info
        
    def top_directors(self, n):
        """
        Метод возвращает словарь с топ-n режиссерами, где ключи — режиссеры, а значения — номера фильмов, созданных ими. 
        Сортируем по номерам в порядке убывания.
        """
        directors = {}
        for film in self.data:
            name = film[3]
            directors[name] = directors.get(name, []) + [film[1]]
        
        directors = dict(
            sorted(directors.items(), key=lambda item: len(item[1]), reverse=True)[:n]
        )
        return directors
        
    def most_expensive(self, n):
        """
        Метод возвращает словарь с топ-n фильмами, где ключи — названия фильмов, а значения — их бюджеты. 
        Сортируйте его по убыванию бюджетов.
        """
        budgets = {}
        for film in self.data:
            budget = film[4]
            title = film[2]
            budgets[title] = int(budget)

        budgets = dict(
            sorted(budgets.items(), key = lambda item: item[1], reverse=True)[:n]
        )

        return budgets
        
    def most_profitable(self, n):
        """
        Метод возвращает словарь с лучшими фильмами, где ключами являются названия фильмов, 
        а значениями — разница между совокупным мировым валовым сбором и бюджетом.
        Сортируйте его по разнице по убыванию.
        """
        profits = {}
        for film in self.data:
            budget = film[4]
            worldwide_gross = film[5]
            title = film[2]
            profits[title] = int(worldwide_gross) - int(budget)

        profits = dict(
            sorted(profits.items(), key = lambda item: item[1], reverse=True)[:n]
        )

        return profits
        
    def longest(self, n):
        """
        Метод возвращает словарь с top-n фильмами, где ключи — названия фильмов, а
        значения — их время выполнения. Если версий больше одной — выберите любую.
        Сортируйте по времени выполнения по убыванию.
        """
        runtimes = {}
        for film in self.data:
            title = film[2]
            runtime = film[6]            
            runtimes[title] = int(runtime)

        runtimes = dict(
            sorted(runtimes.items(), key = lambda item: item[1], reverse=True)[:n]
        )
        return runtimes
        
    def top_cost_per_minute(self, n):
        """
        Метод возвращает словарь с top-n фильмами, где ключами являются названия фильмов, а значениями — бюджеты, деленные на время их выполнения. 
        Бюджеты могут быть в разных валютах — не обращайте на это внимания.
        Значения должны быть округлены до 2 десятичных знаков. Отсортируйте их по делению по убыванию.
        """
        costs = {}
        for film in self.data:
            title = film[2]
            budget = film[4]
            runtime = film[6]
            try:
                per_min = float(budget) / float(runtime)
                costs[title] = round(per_min, 2)
            except:
                continue
        costs = dict(
            sorted(costs.items(), key = lambda item: item[1], reverse=True)[:n]
        )
        return costs


if __name__ == "__main__":
    link = Links("../data/links20.csv")
    
    list_of_movies = ["0317198", "0308644", "0368891"]
    list_of_fields = ['Title', 'Director', 'Budget', 'Cumulative Worldwide Gross', 'Runtime']
    
    # films_info = link.get_imdb(list_of_movies = list_of_movies, list_of_fields = list_of_fields)
    # for film in films_info:
    #     print(film)

    top_directors = link.top_directors(10)
    most_expensive = link.most_expensive(10)
    most_profitable = link.most_profitable(10)
    longest = link.longest(10)
    top_cost_per_minute = link.top_cost_per_minute(10)

    for name, films in top_cost_per_minute.items():
        print(f"{name} : {films}")

