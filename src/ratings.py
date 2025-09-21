import datetime
from collections import Counter

class Ratings:
    """
    Analyzing data from ratings.csv
    """
    def __init__(self, path_to_ratings, path_to_movies):
        """
        Put here any fields that you think you will need.
        """
        
        self.data_ratings = self._get_data(path_to_ratings)
        self.data_movies = self._get_data(path_to_movies)

        self.movies = self.Movies(self.data_ratings, self.data_movies)
        self.users = self.Users(self.data_ratings, self.data_movies)
        

    def _get_data(self, path):

        data = []
        with open(path, "r", encoding="utf-8") as file:
            for line in file:
                data.append(line.strip())
        return data            

    class Movies:    
        def __init__(self, data_ratings, data_movies):
            self.data_ratings = data_ratings
            self.data_movies = data_movies

        def _get_id_names_movies(self):
            movies_id_name = {}

            for line in self.data_movies[1:]:
                name = line[line.find(",") + 1 : line.rfind(",")]
                id = line[:line.find(",")]
                movies_id_name[id] = name

            return movies_id_name

        def dist_by_year(self):
            """
            Метод возвращает словарь, где ключами являются годы, а значениями — количества.
            Отсортируйте его по возрастанию лет. Вам нужно извлечь годы из временных меток.
            """
            years = []
            for line in self.data_ratings[1:]:
                timestamp = line.split(',')[3]
                timestamp = int(timestamp)
                date = datetime.datetime.utcfromtimestamp(timestamp)
                year = int(str(date)[:4])
                years.append(year)
            
            year_dict = dict(Counter(years))
            ratings_by_year = dict(
                sorted(year_dict.items(), key=lambda item: item[0])
            )
            return ratings_by_year
        
        def dist_by_rating(self):
            """
            Метод возвращает словарь, где ключи — это рейтинги, а значения — это счетчики.
            Сортируйте его по возрастанию рейтингов.
            """

            rates = []
            for line in self.data_ratings[1:]:
                rating = line.split(',')[2]
                rates.append(float(rating))
            
            ratings_distribution = dict(Counter(rates))
            ratings_distribution = dict(
                sorted(ratings_distribution.items(), key=lambda item: item[0])
            )

            return ratings_distribution
        
        def top_by_num_of_ratings(self, n):
            """
            Метод возвращает top-n фильмов по количеству оценок.
            Это словарь, где ключами являются названия фильмов, а значениями — числа.               !!!
            Сортируйте его по числам в порядке убывания.
            """

            moviesIDs = []
            movies_id_name = self._get_id_names_movies()
            top_movies = {}

            for line in self.data_ratings[1:]:
                movieID = line.split(',')[1]
                moviesIDs.append(movieID)

            id_top_movies = dict(Counter(moviesIDs).most_common(n))

            for key, value in id_top_movies.items():
                top_movies[movies_id_name[key]] = value 
            return top_movies
        
        def median(self, lst):
            
            sorted_lst = sorted(lst)
            n = len(sorted_lst)
            mid = n // 2

            if n % 2 == 1:
                return float(sorted_lst[mid])
            else:
                return (sorted_lst[mid - 1] + sorted_lst[mid]) / 2.0
        
        def top_by_ratings(self, n, metric="average"):
            """
            Метод возвращает топ-n фильмов по среднему или медианному значению рейтингов.
            Это словарь, где ключами являются названия фильмов, а значениями — значения метрик.
            Сортируйте его по убыванию метрик.
            Значения должны быть округлены до 2 десятичных знаков.
            """

            movies_id_name = self._get_id_names_movies()

            movies_ratings = {}

            for line in self.data_ratings[1:]:
                movieID = line.split(',')[1]
                rating = line.split(',')[2]
                rating = float(rating)
                movies_ratings[movies_id_name[movieID]] = movies_ratings.get(movies_id_name[movieID], []) + [rating]

            if metric == "median":
                movies_median = {}
                for name, ratings in movies_ratings.items():
                    movies_median[name] = round(self.median(ratings), 2)
                    top_movies = dict(Counter(movies_median).most_common(n))
            elif metric == "average":
                movies_average = {}
                for name, ratings in movies_ratings.items():
                    movies_average[name] = round(sum(ratings) / len(ratings), 2)
                    top_movies = dict(Counter(movies_average).most_common(n))

            return top_movies
        
        def variance(self, values):
            if len(values) < 2:
                return 0.0  # дисперсия из одного элемента = 0 по соглашению
            mean = sum(values) / len(values)
            squared_diffs = [(x - mean) ** 2 for x in values]
            return sum(squared_diffs) / (len(values) - 1)

        def top_controversial(self, n):
            """
            Метод возвращает top-n фильмов по дисперсии рейтингов.
            Это словарь, где ключами являются названия фильмов, а значениями — дисперсии.
            Сортируйте его по дисперсии по убыванию.
            Значения должны быть округлены до 2 десятичных знаков.
            """

            movies_id_name = self._get_id_names_movies()

            movies_ratings = {}

            for line in self.data_ratings[1:]:
                movieID = line.split(',')[1]
                rating = line.split(',')[2]
                rating = float(rating)
                movies_ratings[movies_id_name[movieID]] = movies_ratings.get(movies_id_name[movieID], []) + [rating]

            
            movies_variance = {}
            for name, ratings in movies_ratings.items():
                movies_variance[name] = round(self.median(ratings), 2)
                top_movies = dict(Counter(movies_variance).most_common(n))

            return top_movies

    class Users(Movies):
        """
        В этом классе должны работать три метода.
        Первый возвращает распределение пользователей по количеству оценок, которые они поставили.
        Второй возвращает распределение пользователей по средним или медианным оценкам, которые они поставили.
        Третий возвращает n лучших пользователей с самой большой дисперсией их оценок.
        Наследуется от класса Movies. Несколько методов похожи на методы из него.
        """
        def dist_by_num_ratings(self):
            """
            Возвращает словарь: ключ — userId, значение — количество оценок.
            Отсортировано по возрастанию userId.
            """
            user_counts = {}
            for line in self.data_ratings[1:]:
                user_id = line.split(',')[0]
                user_counts[user_id] = user_counts.get(user_id, 0) + 1

            # Сортируем по userId (числовое сравнение)
            return dict(sorted(user_counts.items(), key=lambda x: int(x[0])))

        def dist_by_ratings(self, metric="average"):
            """
            Возвращает распределение пользователей по метрике: 'average' или 'median'.
            Ключ — userId, значение — средний или медианный рейтинг пользователя.
            Округлено до 2 знаков, отсортировано по возрастанию userId.
            """
            user_ratings = {}
            for line in self.data_ratings[1:]:
                parts = line.split(',')
                user_id = parts[0]
                rating = float(parts[2])
                user_ratings.setdefault(user_id, []).append(rating)

            result = {}
            for user_id, ratings in user_ratings.items():
                if metric == "average":
                    value = sum(ratings) / len(ratings)
                elif metric == "median":
                    value = self.median(ratings)

                result[user_id] = round(value, 2)

            return dict(sorted(result.items(), key=lambda x: int(x[0])))

        def top_by_variance(self, n):
            """
            Возвращает топ-n пользователей с наибольшей дисперсией их оценок.
            Ключ — userId, значение — дисперсия (округлённая до 2 знаков).
            Сортировка по убыванию дисперсии.
            """
            user_ratings = {}
            for line in self.data_ratings[1:]:
                parts = line.split(',')
                user_id = parts[0]
                rating = float(parts[2])
                user_ratings.setdefault(user_id, []).append(rating)

            user_variances = {}
            for user_id, ratings in user_ratings.items():
                var = self.variance(ratings)
                user_variances[user_id] = round(var, 2)

            # Топ-n по убыванию дисперсии
            top_n = dict(Counter(user_variances).most_common(n))
            return top_n


ratings = Ratings("../data/ratings.csv", "../data/movies.csv")
# movies = ratings.Movies()

print(ratings.users.top_by_variance(5))

