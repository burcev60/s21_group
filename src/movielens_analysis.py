from bs4 import BeautifulSoup
import requests
import time
import re
import pytest

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
                movies_list.append(line.split(",")[1].strip())
        return movies_list

    def get_imdb(self, list_of_movies=None, list_of_fields=None):
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
        for movie_id in (
            list_of_movies if list_of_movies is not None else self.list_of_movies
        ):
            time.sleep(0.5)

            url = f"https://www.imdb.com/title/tt{movie_id}"

            try:
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")
            except:
                continue

            try:
                director = (
                    soup.find("li", {"data-testid": "title-pc-principal-credit"})
                    .find("a")
                    .text
                )
            except:
                director = "Unknown"

            try:
                budget = (
                    soup.find("li", {"data-testid": "title-boxoffice-budget"})
                    .find("li")
                    .text
                )
                budget = int("".join(ch for ch in budget if ch.isdigit()))
            except:
                budget = 0

            try:
                worldwide_gross = (
                    soup.find(
                        "li",
                        {"data-testid": "title-boxoffice-cumulativeworldwidegross"},
                    )
                    .find("li")
                    .text
                )
                worldwide_gross = int(
                    "".join(ch for ch in worldwide_gross if ch.isdigit())
                )
            except:
                worldwide_gross = 0

            try:
                runtime = (
                    soup.find("li", {"data-testid": "title-techspec_runtime"})
                    .find("div")
                    .text.split()
                )
                runtime = int(runtime[0]) * 60 + int(runtime[2])
            except:
                runtime = 0

            try:
                title = soup.find("h1", {"data-testid": "hero__pageTitle"}).text
            except:
                title = "Unknown"

            film_info = [movie_id]
            for field in list_of_fields:
                if field == "Director":
                    film_info.append(director)
                elif field == "Budget":
                    film_info.append(budget)
                elif field == "Cumulative Worldwide Gross":
                    film_info.append(worldwide_gross)
                elif field == "Runtime":
                    film_info.append(runtime)
                elif field == "Title":
                    film_info.append(title)

            imdb_info.append(film_info)

        imdb_info = sorted(imdb_info, key=lambda film: film[0], reverse=True)
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
            sorted(budgets.items(), key=lambda item: item[1], reverse=True)[:n]
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
            sorted(profits.items(), key=lambda item: item[1], reverse=True)[:n]
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
            sorted(runtimes.items(), key=lambda item: item[1], reverse=True)[:n]
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
        costs = dict(sorted(costs.items(), key=lambda item: item[1], reverse=True)[:n])
        return costs


class Movies:
    """
    Analyzing data from movies.csv
    """

    def __init__(self, path_to_the_file):
        """
        Put here any fields that you think you will need.
        """
        self.path = path_to_the_file
        self.data = self._get_data()

    def _get_data(self):
        data = []
        with open(self.path, "r") as file:
            for line in file:
                data.append(line.strip())
        return data

    def dist_by_release(self):
        """
        Метод возвращает словарь или OrderedDict, где ключи — это годы, а значения — это количества.
        Вам нужно извлечь годы из названий. Отсортируйте их по количеству в порядке убывания.
        """
        release_years = {}
        for line in self.data:
            match = re.search(r"\((\d{4})\)", line)
            if match:
                year = match.group(1)
                release_years[year] = release_years.get(year, 0) + 1

        release_years = dict(
            sorted(release_years.items(), key=lambda item: item[1], reverse=True)
        )

        return release_years

    def dist_by_genres(self):
        """
        Метод возвращает словарь, где ключи — жанры, а значения — количества.
        Сортируйте его по количеству в порядке убывания.
        """
        genres = {}
        if_first_line = True
        for line in self.data:
            if if_first_line:
                if_first_line = False
            else:
                raw_genres = line[line.rfind(",") + 1 :].strip().split("|")

                for gen in raw_genres:
                    genres[gen] = genres.get(gen, 0) + 1

        genres = dict(sorted(genres.items(), key=lambda item: item[1], reverse=True))
        return genres

    def most_genres(self, n):
        """
        Метод возвращает словарь с top-n фильмами, где ключи — названия фильмов,
        а значения — количество жанров фильма. Сортируйте его по номерам в порядке убывания.
        """
        untop_movies = {}

        for line in self.data:
            mov = line[line.find(",") + 1 : line.rfind(",")]
            gen = line[line.rfind(",") + 1 :].strip().split("|")
            untop_movies[mov] = len(gen)

        movies = dict(
            sorted(untop_movies.items(), key=lambda item: item[1], reverse=True)[:n]
        )
        return movies


class Tags:
    """
    Analyzing data from tags.csv
    """

    def __init__(self, path_to_the_file):
        """
        Put here any fields that you think you will need.
        """
        self.path = path_to_the_file
        self.data = self._get_data()

    def _get_data(self):
        data = []
        is_first_line = True
        with open(self.path, "r") as file:
            for line in file:
                if is_first_line:
                    is_first_line = False
                else:
                    data.append(line.strip())
        return data

    def most_words(self, n):
        """
        Метод возвращает top-n тегов с наибольшим количеством слов внутри.
        Это словарь, где ключи — теги, а значения — количество слов внутри тега.
        Удалить дубликаты. Сортировать по номерам по убыванию.
        """

        big_tags = {}
        tags = []
        for line in self.data:
            tags.append(line.split(",")[2])

        uniq_tags = list(set(tags))
        for tag in uniq_tags:
            big_tags[tag] = len(tag.split(" "))
        big_tags = dict(
            sorted(big_tags.items(), key=lambda item: item[1], reverse=True)[:n]
        )
        return big_tags

    def longest(self, n):
        """
        Метод возвращает top-n самых длинных тегов по количеству символов.
        Это список тегов. Удалите дубликаты. Отсортируйте его по номерам в порядке убывания.
        """
        big_tags = {}
        tags = []
        for line in self.data:
            tags.append(line.split(",")[2])

        uniq_tags = list(set(tags))
        for tag in uniq_tags:
            big_tags[tag] = len(tag)
        big_tags = dict(
            sorted(big_tags.items(), key=lambda item: item[1], reverse=True)[:n]
        )
        return big_tags

    def most_words_and_longest(self, n):
        """
        Метод возвращает пересечение между верхними n тегами с наибольшим количеством слов внутри
        и верхними n самыми длинными тегами по количеству символов.
        Удаляем дубликаты. Это список тегов.
        """
        big_words = self.most_words(n)
        big_symbols = self.longest(n)
        big_tags = list(set(big_words.keys()) & set(big_symbols.keys()))
        return big_tags

    def most_popular(self, n):
        """
        Метод возвращает самые популярные теги.
        Это словарь, где ключи — теги, а значения — счетчики.
        Удалите дубликаты. Отсортируйте его по счетчикам по убыванию.
        """
        popular_tags = {}
        for line in self.data:
            tag = line.split(",")[
                2
            ]  # нужен ли lower() ??? есть теги с разным регистром
            popular_tags[tag] = popular_tags.get(tag, 0) + 1

        popular_tags = dict(
            sorted(popular_tags.items(), key=lambda item: item[1], reverse=True)[:n]
        )

        return popular_tags

    def tags_with(self, word):
        """
        Метод возвращает все уникальные теги, которые включают слово, указанное в качестве аргумента.
        Удалить дубликаты. Это список тегов. Отсортировать его по именам тегов в алфавитном порядке.
        """
        tags = []
        for line in self.data:
            tag = line.split(",")[2]
            if word in tag:  # lower??
                tags.append(tag)

        tags_with_word = sorted(list(set(tags)))

        return tags_with_word

class TestMethods:
    def setup_method(self):
        self.n = 3
        self.word = "great"
        self.list_of_movies = ["0317198", "0308644", "0368891"]
        self.list_of_fields = ['Title', 'Director', 'Budget', 'Cumulative Worldwide Gross', 'Runtime']
        self.links = Links("../data/links.csv")
        self.movies = Movies("../data/movies.csv")
        self.tags = Tags("../data/tags.csv")

    def test_links_get_imdb(self):
        result = self.links.get_imdb(list_of_movies=self.list_of_movies, list_of_fields=self.list_of_fields)
        assert isinstance(result, list)

    def test_links_get_imdb_list(self):
        result = self.links.get_imdb(list_of_movies=self.list_of_movies, list_of_fields=self.list_of_fields)
        for res in result:
            assert isinstance(res[0], str)
            assert isinstance(res[1], str)
            assert isinstance(res[2], str)
            assert isinstance(res[3], int)
            assert isinstance(res[4], int)
            assert isinstance(res[5], int)

    def test_links_top_directors(self):
        result = self.links.top_directors(self.n)
        assert isinstance(result, dict)

    def test_links_most_expensive(self):
        result = self.links.most_expensive(self.n)
        assert isinstance(result, dict)

    def test_links_most_profitable(self):
        result = self.links.most_profitable(self.n)
        assert isinstance(result, dict)

    def test_links_longest(self):
        result = self.links.longest(self.n)
        assert isinstance(result, dict)

    def test_links_top_cost_per_minute(self):
        result = self.links.top_cost_per_minute(self.n)
        assert isinstance(result, dict)

    def test_movies_dist_by_release(self):
        result = self.movies.dist_by_release()
        assert isinstance(result, dict)

    def test_movies_dist_by_genres(self):
        result = self.movies.dist_by_genres()
        assert isinstance(result, dict)

    def test_movies_most_genres(self):
        result = self.movies.most_genres(self.n)
        assert isinstance(result, dict)
        assert result == {'Rubber (2010)': 10, 
                          'Patlabor: The Movie (Kidô keisatsu patorebâ: The Movie) (1989)': 8, 
                          'Mulan (1998)': 7}
        
    def test_tags_most_words(self):
        result = self.tags.most_words(self.n)
        assert isinstance(result, dict)

    def test_tags_longest(self):
        result = self.tags.longest(self.n)
        assert isinstance(result, dict)

    def test_tags_most_words_and_longest(self):
        result = self.tags.most_words_and_longest(self.n)
        assert isinstance(result, list)

    def test_tags_most_words_and_longest_list(self):
        result = self.tags.most_words_and_longest(self.n)
        for res in result:
            assert isinstance(res, str)

    def test_tags_most_popular(self):
        result = self.tags.most_popular(self.n)
        assert isinstance(result, dict)

    def test_tags_tags_with(self):
        result = self.tags.tags_with(self.word)
        assert isinstance(result, list)
    
    def test_tags_tags_with_list(self):
        result = self.tags.tags_with(self.word)
        for res in result:
            assert isinstance(res, str)

if __name__ == "__main__":
    links = Links("../data/links.csv")

    list_of_movies = ["0317198", "0308644", "0368891"]
    list_of_fields = ['Title', 'Director', 'Budget', 'Cumulative Worldwide Gross', 'Runtime']

    # get_imdb = links.get_imdb(list_of_movies=list_of_movies, list_of_fields=list_of_fields)
    # top_directors = links.top_directors(10)
    # most_expensive = links.most_expensive(10)
    # most_profitable = links.most_profitable(10)
    # longest = links.longest(10)
    # top_cost_per_minute = links.top_cost_per_minute(10)

    # print(get_imdb)


    # for result in [get_imdb, top_directors, most_expensive, most_profitable, longest, top_cost_per_minute]:
    #     print(result, "\n")

    movies = Movies("../data/movies.csv")
    # dist_by_release = movies.dist_by_release()
    # dist_by_genres = movies.dist_by_genres()
    # most_genres = movies.most_genres(3)

    # for result in [dist_by_release, dist_by_genres, most_genres]:
    #     print(result, "\n")

    tags = Tags("../data/tags.csv")
    # most_words = tags.most_words(3)
    # longest = tags.longest(3)
    # most_words_and_longest = tags.most_words_and_longest(3)
    # most_popular = tags.most_popular(10)
    tags_with = tags.tags_with("great")

    print(tags_with)

    # for result in [most_words, longest, most_words_and_longest, most_popular, tags_with]:
    #     print(result, "\n")