import re


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


if __name__ == "__main__":
    movie = Movies("../data/movies.csv")
    # print(movie.dist_by_release())

    # print(movie.dist_by_genres())

    # for key,value in movie.most_genres(3).items():
    #     print(f"{key} : {value}")

    # print(movie.most_genres(10))
