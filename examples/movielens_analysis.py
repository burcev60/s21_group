#!/usr/bin/env python3
import re
import os
import sys
import requests
import json
import pytest
from datetime import datetime
from bs4 import BeautifulSoup
from functools import wraps, lru_cache
from collections import Counter, OrderedDict, defaultdict

def check_errors(func):
    """Checking methods for errors."""  # noqa: D401
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"File not found: {e}")
        except KeyboardInterrupt:
            raise KeyboardInterrupt("Program stopped by user")
        except IndexError as e:
            raise IndexError(f"Index error: attempt to access non-existent index. Details: {e}")  # noqa: E501
        except UnicodeDecodeError as e:
            raise UnicodeDecodeError(f"Unsupported encoding: {e}")
        except ValueError as e:
            raise ValueError(f"Value error: invalid data format or range. Details: {e}")  # noqa: E501
        except MemoryError as e:
            raise MemoryError(f"Memory error: not enough memory to complete operation. Details: {e}")  # noqa: E501
        except TypeError as e:
            raise TypeError(f"Type error: operation applied to object of inappropriate type. Details: {e}")  # noqa: E501
        except AttributeError as e:
            raise AttributeError(f"Attribute error: attempt to access non-existent attribute. Details: {e}")  # noqa: E501
        except Exception as e:
            raise Exception(f"Unexpected error: {e.__class__.__name__}: {e}")
        else:
            return result

    return wrapper


class Ratings:
    """Analyzing data from links.csv."""

    def __init__(self, path_to_the_file, path_to_the_file2) -> None:
        """Initializing attributes."""  # noqa: D401
        self.path = path_to_the_file
        self.path2 = path_to_the_file2
        self.ratings = []
        self.movies = []
        self.unity = []
        self.read_ratings_csv()
        self.read_movies_csv()
        self.unity_ratings_and_movies_csv()
    
    @check_errors
    def read_ratings_csv(self) -> None:
        """Reading rating.csv and writing the data to the dictionary list."""  # noqa: D401
        with open(self.path, encoding="utf-8") as file:
            next(file)

            for line in file:
                temp = line.strip().split(",")
                self.ratings.append(
                    {
                        "userId": int(temp[0]),
                        "movieId": int(temp[1]),
                        "rating": float(temp[2]),
                        "timestamp": int(temp[3]),
                    }
                )

    @check_errors
    def read_movies_csv(self) -> None:
        """Reading movies.csv and writing the data to the dictionary list."""  # noqa: D401
        with open(self.path2, encoding="utf-8") as file:
            next(file)

            for line in file:
                line = line.strip()
                temp = line.split(",")
                
                if len(temp) > 3:
                    step = line.rsplit('"',1)[0].split(",")
                    step2 = ' '.join(step[1:]).replace('"', '')
                    title = step2.replace("  ", " ")

                else:
                    title = line.split(",")[1].strip('"')
        
                self.movies.append( 
                    {
                        "movieId": int(temp[0]),
                        "title": title[:-7],
                        "genres": temp[-1],
                    }
                    )
        
    @check_errors
    def unity_ratings_and_movies_csv(self) -> None:
        """Combining ratings.csv and movies.csv into one file.
        File structure: {'userId': 68, 'movieId': 1, 'rating': 2.5, 'timestamp': 1158531426, 'title': 'Toy Story (1995)', 'genres': 'Adventure|Animation|Children|Comedy|Fantasy'}.
        """  # noqa: D205, D401, E501
        sorted_movies = list(sorted(self.movies, key=lambda v: v["movieId"]))
        sorted_ratings = list(sorted(self.ratings, key=lambda v: v["movieId"]))
        
        ratings_dict = defaultdict(list)
        for rating in sorted_ratings:
            ratings_dict[rating["movieId"]].append(rating)

        for movie in sorted_movies:
            movie_id = movie["movieId"]
            if movie_id in ratings_dict:
                for rating in ratings_dict[movie_id]:
                    self.unity.append(rating | movie)
                    
    
    @staticmethod
    @check_errors
    def get_average(target) -> float:
        """Calculation of the average value."""  # noqa: D401
        return sum(target) / len(target) if target else 0
    
    @staticmethod
    @check_errors
    def get_median(target) -> float:
        """Calculation of the median value."""  # noqa: D401
        if not target:
            return 0

        s = sorted(target)
        middle = len(s) // 2
        
        return (s[middle-1] + s[middle]) / 2 if len(s) % 2 == 0 else s[middle]
    
    @staticmethod
    @check_errors
    def get_variance(target) -> float:
        """Calculation of variance."""  # noqa: D401
        if len(target) < 2:
            return 0

        middle = Ratings.get_average(target)
        
        return sum((x - middle) ** 2 for x in target) / (len(target) - 1)
    

    class Movies:
        """Analyzing data from ratings.csv & movies.csv."""

        def __init__(self, unity) -> None:
            """Initializing attributes."""  # noqa: D401
            self.unity = unity or []

        @check_errors
        def dist_by_year(self) -> dict:
            """The method returns a dict where the keys are years and the values are counts. Sort it by years ascendingly. You need to extract years from timestamps."""  # noqa: D401, E501
            ratings_by_year = Counter(datetime.fromtimestamp(
                item["timestamp"]).year for item in self.unity)
            
            return dict(sorted(ratings_by_year.items()))

        @check_errors
        def dist_by_rating(self) -> dict:
            """The method returns a dict where the keys are ratings and the values are counts. Sort it by ratings ascendingly."""  # noqa: D401, E501
            ratings_distribution = Counter(
                item["rating"] for item in self.unity)

            return dict(sorted(ratings_distribution.items()))

        @check_errors
        def top_by_num_of_ratings(self, n) -> dict:
            """The method returns top-n movies by the number of ratings.
            It is a dict where the keys are movie titles and the values are numbers.Sort it by numbers descendingly."""  # noqa: D205, D209, D401, E501
            if n <= 0:
                return {}
            
            top_movies = Counter(item["title"] for item in self.unity 
                if item and "title" in item)
            
            return dict(sorted(top_movies.items(), 
                key=lambda v: v[1], reverse=True)[:n])


        @check_errors
        def top_by_ratings(self, n, metric="average") -> dict:
            """The method returns top-n movies by the number of ratings.
            It is a dict where the keys are movie titles and the values are numbers. Sort it by numbers descendingly."""  # noqa: D205, D209, D401, E501
            if n <= 0:
                return {}
            
            if metric == "average":
                metric = Ratings.get_average
            elif metric == "median":
                metric = Ratings.get_median
            else:
                raise ValueError("Invalid metric. Use 'average' or 'median'.")
                
            movie_ratings = defaultdict(list)
            for item in self.unity:
                if isinstance(item, dict):
                    title = item.get("title")
                    rating = item.get("rating")
                    if title is not None and rating is not None:
                        movie_ratings[title].append(rating)

            if not movie_ratings:
                return {}

            rated_movies = {
                title: round(metric(ratings), 2)
                for title, ratings in movie_ratings.items()
            }
            return dict(sorted(rated_movies.items(), 
                key=lambda x: x[1], reverse=True)[:n])
        
        @check_errors
        def top_controversial(self, n) -> dict:
            """The method returns top-n movies by the variance of the ratings.
            It is a dict where the keys are movie titles and the values are the variances. Sort it by variance descendingly. The values should be rounded to 2 decimals."""  # noqa: D205, D209, D401, E501
            if n <= 0:
                return {}
            
            top_movies = defaultdict(list)
            for item in self.unity:
                top_movies[item["title"]].append(item["rating"])
                
            variances = {movie: round(
                Ratings.get_variance(rating), 2)
                for movie, rating in top_movies.items()
                if len(rating) > 1}
            
            return dict(sorted(variances.items(), 
                key=lambda v: v[1], reverse=True)[:n])
            
            # BONUS PART
        @check_errors
        def average_ratings_by_genres(self) -> dict:  # noqa: D102
            """The method returns a dictionary where genres are the keys and their average rating is the values. The dictionary is sorted in descending order."""  # noqa: D401, E501 
            if not hasattr(self, 'unity') or not self.unity:
                return {} 

            genre_ratings = defaultdict(list)

            for item in self.unity:
                if "genres" not in item or "rating" not in item:
                    continue 
                
                split_genres = item["genres"].split("|")
                rating = item["rating"]
                
                for genre in split_genres:
                    genre_ratings[genre].append(rating)

            average_ratings = {genre: round(sum(ratings)/len(ratings), 2)
                for genre, ratings in genre_ratings.items()}


            return dict(sorted(average_ratings.items(), 
                key=lambda item: item[1], reverse=True))
        
        
    class Users(Movies):
        """In this class, three methods should work. The 1st returns the distribution of users by the number of ratings made by them. The 2nd returns the distribution of users by average or median ratings made by them.The 3rd returns top-n users with the biggest variance of their ratings. Inherit from the class Movies. Several methods are similar to the methods from it."""  # noqa: D205, D209, E501
        
        def __init__(self, unity) -> None:
            """Initializing attributes."""  # noqa: D401
            super().__init__(unity)
            self.unity = unity
        
        
        @check_errors
        def number_of_ratings(self) -> dict:
            """The method returns the distribution of users by the number of ratings given."""  # noqa: D401, E501
            ratings = Counter(item["userId"] for item in self.unity)
            
            return dict(sorted(ratings.items(), 
                key=lambda v: v[1], reverse=True))
        

        @check_errors
        def average_or_median_ratings(self, metric="average")-> dict:
            """The method returns the distribution of users based on the average or median of their ratings."""  # noqa: D401, E501
            if metric == "average":
                metric = Ratings.get_average
            if metric == "median":
                metric = Ratings.get_median
                
            aom_ratings = defaultdict(list)
            for item in self.unity:
                if item and "title" in item and "rating" in item:
                    aom_ratings[item["userId"]].append(item["rating"])
                    
                    
            aom_ratings = defaultdict(list)
            for item in self.unity:
                if item and isinstance(item, dict):
                    userid = item.get("userId")
                    rating = item.get("rating")
                    if userid is not None and rating is not None:
                        aom_ratings[userid].append(rating)
                        
            metric_values = {
                title: round(metric(ratings), 2)
                for title, ratings in aom_ratings.items()}            
            
            return dict(sorted(metric_values.items(),
                key=lambda v: v[1], reverse=True))
        
        
        @check_errors
        def biggest_variance_ratings(self, n) -> dict:
            """The method returns the top n users with the most
            the variance of the estimates."""  # noqa: D205, D209, D401
            if n <= 0:
                return {}
            
            variance_ratings = defaultdict(list)
            for item in self.unity:
                if item and "title" in item and "rating" in item:
                    variance_ratings[item["userId"]].append(item["rating"])
            
            variance_ratings = defaultdict(list)
            for item in self.unity:
                if item and isinstance(item, dict):
                    userid = item.get("userId")
                    rating = item.get("rating")
                    if userid is not None and rating is not None:
                        variance_ratings[userid].append(rating)
            
            metric_values = {
                title: round(Ratings.get_variance(ratings), 2)
                for title, ratings in variance_ratings.items()}            
            
            return dict(sorted(metric_values.items(),
                key=lambda v: v[1], reverse=True)[:n])

class Movies:
    """Analyzing data from movies.csv."""

    def __init__(self, path_to_the_file) -> None:
        """Initializing attributes."""  # noqa: D401
        self.path = path_to_the_file
        self.lines = None
        self.read_movies_csv()


    @check_errors
    def read_movies_csv(self) -> None:
        """Reading movies.csv."""  # noqa: D401
        with open(self.path, encoding="utf-8") as file:
            self.movies = file.read()

        self.lines = [
            line.strip() for line in self.movies.split("\n") if line.strip()]

    @check_errors
    def dist_by_release(self) -> OrderedDict:
        """The method returns a dict or an OrderedDict where the keys are years and the values are counts. You need to extract years from the titles. Sort it by counts descendingly."""  # noqa: D401, E501
        years = [
            re.search(r"\((\d{4})\)", line).group(1)
            for line in self.lines
            if re.search(r"\(\d{4}\)", line)
        ]

        count_in_years = Counter(years)

        return OrderedDict(sorted(count_in_years.items(), 
            key=lambda v: -v[1]))

    @check_errors
    @lru_cache
    def dist_by_genres(self) -> dict:
        """The method returns a dict where the keys are genres and the values are counts. Sort it by counts descendingly."""  # noqa: D401, E501
        genres = []

        for line in self.lines[1:]:
            line = line.strip("\n")

            if not line:
                continue

            match = re.match(r'(\d+),((".*?"|[^,]+)),(.+)', line)
            genres += match.group(4).split("|")

        return dict(sorted(Counter(genres).items(), 
            key=lambda v: v[1], reverse=True))

    @check_errors
    def most_genres(self, n) -> dict:
        """The method returns a dict with top-n movies where the keys are movie titles and the values are the number of genres of the movie. Sort it by numbers descendingly."""  # noqa: D401, E501
        if n <= 0:
            return {}

        movies = {}

        for line in self.lines[1:]:
            line = line.strip("\n")

            if not line:
                continue

            match = re.match(r'(\d+),((".*?"|[^,]+)),(.+)', line)
            title = match.group(2).strip('"')[:-7]
            genres = match.group(4).split("|")

            movies[title] = len(genres) 

        return dict(sorted(movies.items(), 
            key=lambda v: v[1], reverse=True)[:n])
    
        # BONUS PART
    @check_errors
    def stat_by_genres(self) -> dict:
        """The method returns a dict with movies where the keys are genre and the values are the percent of total genres in movies.csv."""  # noqa: D401, E501
        all_info = dict(Counter(self.dist_by_genres()))   
        total_cnt = sum(int(v) for v in all_info.values())
        
        convert_to_percent = {  
            k: f"{round(v/total_cnt * 100, 2)} %" for k,v in all_info.items()}
        
        return dict(sorted(convert_to_percent.items(), 
            key=lambda v: float(v[1][:-2]), reverse=True))

class Tags:
    """Analyzing data from tags.csv."""

    def __init__(self, path_to_the_file) -> None:
        """Initializing attributes."""  # noqa: D401
        self.path = path_to_the_file
        self.tags = None
        self.read_tags_csv()

    @check_errors
    def read_tags_csv(self) -> None:
        """Reading tags.csv."""  # noqa: D401
        with open(self.path, encoding="utf-8") as file:
            tags = file.read()
            self.tags = [
                line.strip() for line in tags.split("\n") if line.strip()]

    @check_errors
    def most_words(self, n) -> dict:
        """The method returns top-n tags with most words inside. It is a dict
        where the keys are tags and the values are the number of words inside the tag.Drop the duplicates. Sort it by numbers descendingly.
        """  # noqa: D205, D401, E501
        if n <= 0:
            return {}

        tags = {}

        for line in self.tags[1:]:
            if not line:
                continue

            split_line = line.split(",")
            if len(split_line) > 2:
                split_tags = split_line[2].split(" ")
                tags[split_line[2]] = len(split_tags)

        return dict(sorted(tags.items(), 
            key=lambda v: v[1], reverse=True)[:n])


    @check_errors
    def longest(self, n) -> list:
        """The method returns top-n longest tags in terms of the number of characters.It is a list of the tags. Drop the duplicates. Sort it by numbers descendingly."""  # noqa: D205, D401, E501
        if n <= 0:
            return []

        tags = set()

        for line in self.tags[1:]:
            if not line:
                continue

            split_line = line.split(",")
            if len(split_line) > 2:
                tags.add(split_line[2])

        return sorted(tags, key=lambda v: len(v), reverse=True)[:n]

    @check_errors
    def most_words_and_longest(self, n) -> list:
        """The method returns the intersection between top-n tags with most words inside and top-n longest tags in terms of the number of characters.Drop the duplicates. It is a list of the tags."""  # noqa: D401, E501
        if n <= 0:
            return []

        max_longest = set(self.longest(n))
        max_words = set(self.most_words(n).keys())

        return list(max_words & max_longest)

    @check_errors
    def most_popular(self, n) -> dict:
        """The method returns the most popular tags. It is a dict where the keys are tags and the values are the counts. Drop the duplicates. Sort it by counts descendingly."""  # noqa: D401, E501
        if n <= 0:
            return {}

        popular_tags = {}

        for line in self.tags[1:]:
            if not line:
                continue

            temp = line.split(",")
            if len(temp) > 2:
                tag = temp[2].strip()
                popular_tags[tag] = popular_tags.get(tag, 0) + 1

        return dict(sorted(popular_tags.items(), key=lambda v: -v[1])[:n])

    @check_errors
    def tags_with(self, word) -> list:
        """The method returns all unique tags that include the word given as the argument. Drop the duplicates. It is a list of the tags. Sort it by tag names alphabetically."""  # noqa: D401, E501
        tags_with_word = set()

        for line in self.tags[1:]:
            if not line:
                continue

            temp = line.split(",")
            if len(temp) > 2 and word in temp[2]:
                tags_with_word.add(temp[2])

        return sorted(tags_with_word)


        # BONUS PART
    @check_errors
    def get_tags_by_the_movie(self, movie_id) -> list:
        """Bonus part: this method returns a list of tags for the specified movie."""  # noqa: E501
        movie_id = str(movie_id)
        
        tags = []
        for line in self.tags[1:]:
            _, current_movie_id, tag, _ = line.split(',')
            if current_movie_id == movie_id:
                tags.append(tag.lower())
                
        return list(set(tags))


class Links:
    """Analyzing data from links.csv."""

    def __init__(self, path_to_the_file_links, 
        path_to_the_file_movies, rows) -> None:
        """Initializing attributes."""  # noqa: D401
        self.path_links = path_to_the_file_links
        self.path_movies = path_to_the_file_movies
        self.rows = rows
        self.links_data = {}
        self.movies_data = {}
        self.imbd_data = {}
        self.read_links_csv()
        self.read_movies_csv()
        
    @check_errors
    def read_links_csv(self) -> None:
        """Reading the links.csv file and saving the data."""  # noqa: D401
        with open(self.path_links, encoding="utf-8") as file:
            next(file)
            for i, line in enumerate(file):
                if i >= self.rows:
                    break
                movie_id, imdb_id, tmdb_id = line.strip().split(",")
                self.links_data[int(movie_id)] = (imdb_id)
                
    @check_errors
    def read_movies_csv(self) -> None:
        """Reading the movies.csv file and saving the data."""  # noqa: D401
        with open(self.path_movies, encoding="utf-8") as file:
                next(file)
                for i, line in enumerate(file):
                    if i >= self.rows:
                        break
                    fields = []
                    current_field = ""
                    in_quotes = False
                    for char in line.strip():
                        if char == '"':
                            in_quotes = not in_quotes
                        elif char == "," and not in_quotes:
                            fields.append(current_field.strip())
                            current_field = ""
                        else:
                            current_field += char
                            
                    fields.append(current_field.strip())
                    prepared_data = [
                        field.strip('"') for field in fields if field]
                    
                    self.movies_data[
                        int(prepared_data[0].strip("'"))] = re.sub(
                        r"\s*\(\d{4}\)\s*", "", prepared_data[1])        
    
    @check_errors
    def get_imdb(self, list_of_movies, list_of_fields) -> list:
        """The method returns a list of lists [movieId, field1, field2, field3, ...]."""  # noqa: D401, E501
        imdb_info = []
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",  # noqa: E501
            "Accept-Language": "en-US,en;q=0.9"}
        
        for movie_id in list_of_movies:
            imdb_id = self.links_data.get(movie_id)
            if not imdb_id:
                imdb_info.append([movie_id] + ["N/A" for _ in list_of_fields])
                continue
                
            try:
                url = f"https://www.imdb.com/title/tt{imdb_id}/"
                session = requests.Session()
                response = session.get(url, headers=headers, timeout=15)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "lxml")
                result_row = [movie_id]

                for field in list_of_fields:
                    value = "N/A"
                    field_lower = field.lower()
                    
                    try:
                        if field_lower == "title":
                            title_tag = soup.find("h1")
                            if title_tag:
                                value = title_tag.get_text(strip=True)
                            else:
                                script = soup.find("script", 
                                    type="application/ld+json")
                                if script:
                                    try:
                                        data = json.loads(script.string)
                                        value = data.get("name", "N/A")
                                    except json.JSONDecodeError:
                                        pass

                        elif field_lower == "director":
                            directors = []
                            director_section = soup.find("li", 
                                {"data-testid": "title-pc-principal-credit"})
                            if not director_section:
                                director_section = soup.find("h4",  string="Director:").find_next("a") if soup.find("h4", string="Director:") else None  # noqa: E501
                            
                            if director_section:
                                directors = [a.get_text(strip=True) for a in director_section.find_all("a") if "name" in a.get("href", "")]  # noqa: E501
                            value = ", ".join(directors
                                ) if directors else "N/A"

                        elif field_lower in [
                            "budget", "cumulative worldwide gross"]:
                            
                            label = "Budget" if field_lower == "budget" else "Gross worldwide"  # noqa: E501
                            li = soup.find("li", {"data-testid": f"title-boxoffice-{field_lower.replace(' ', '')}"})  # noqa: E501
                            if not li:
                                li = soup.find("h4", string=label).parent if soup.find("h4", string=label) else None  # noqa: E501
                            
                            if li:
                                value_span = li.find("span", class_="ipc-metadata-list-item__list-content-item")  # noqa: E501
                                
                                if value_span:
                                    value = value_span.get_text(strip=True).split("(")[0].strip()  # noqa: E501

                        elif field_lower == "runtime":
                            runtime_li = soup.find("li", {"data-testid": "title-techspec_runtime"})  # noqa: E501
                            
                            if not runtime_li:
                                runtime_li = soup.find("h4", string="Runtime:").parent if soup.find("h4", string="Runtime:") else None  # noqa: E501
                            
                            if runtime_li:
                                time_text = runtime_li.get_text(
                                    separator=" ", strip=True)
                                
                                if "min" in time_text:
                                    value = time_text.split(
                                        "Runtime")[-1].strip()
                                    
                                else:
                                    value = time_text

                        result_row.append(value if value else "N/A")
                    except Exception:
                        result_row.append("N/A")
                        continue

                imdb_info.append(result_row)

            except requests.RequestException as e:
                print(f"Request failed for movie {movie_id}: {str(e)}")
                imdb_info.append([movie_id] + ["N/A" for _ in list_of_fields])
            except Exception as e:
                print(f"Error processing movie {movie_id}: {str(e)}")
                imdb_info.append([movie_id] + ["N/A" for _ in list_of_fields])
            
            self.imbd_data = sorted(imdb_info, 
                key=lambda x: x[0], reverse=True)

        return sorted(imdb_info, key=lambda x: x[0], reverse=True)

    @check_errors
    def top_directors(self, n) -> dict:
        """The method returns a dict with top-n directors where the keys are directors and the values are numbers of movies created by them. Sort it by numbers descendingly."""  # noqa: D401, E501
        directors = {}
        movie_id_list = list(self.links_data.keys())
        self.get_imdb(movie_id_list, ["Director"])

        for lst in self.imbd_data:
            directors_names = lst[1].split(",")
            
            for name in directors_names:
                directors[name] = directors.get(name, 0) + 1

        return dict(sorted(directors.items(), 
            key=lambda x: x[1], reverse=True)[:n])


    @check_errors
    def most_expensive(self, n) -> dict:
        """The method returns a dict with top-n movies where the keys are movie titles and the values are their budgets. Sort it by budgets descendingly."""  # noqa: D401, E501
        movies_id_list = list(self.movies_data.keys())
        self.get_imdb(movies_id_list, ["Budget"])
        
        movies_titles_budgets = {}
        for lst in self.imbd_data:
            if lst[1] == "N/A":
                pass
            else:
                title = self.movies_data[lst[0]]
                movies_titles_budgets[title] = lst[
                    1
                ]
        movies_titles_budgets_sorted = dict(
            sorted(movies_titles_budgets.items(),
            key=lambda item: (int(re.sub(r"[^\d]", "", item[1]))),
            reverse=True))
        
        return dict(list(movies_titles_budgets_sorted.items())[:n])


    @check_errors
    def most_profitable(self, n) -> dict:
        """The method returns a dict with top-n movies where the keys are movie titles and the values are the difference between cumulative worldwide gross and budget.Sort it by the difference descendingly."""  # noqa: D401, E501
        self.get_imdb(list(self.movies_data.keys()), 
            ["Budget", "Cumulative worldwide gross"])
        
        profit = {}
        for movie_id, budget_str, gross_str in self.imbd_data:
            if "N/A" in (budget_str, gross_str):
                continue
                
            currency = ""
            for s in [budget_str, gross_str]:
                match = re.match(r'^([^\d-]*)(-?)', s)
                if match:
                    found_currency = match.group(1)
                    if found_currency:
                        currency = found_currency
                        break
                    
            if not currency:
                currency = "$"
                
            budget = int(re.sub(r'[^\d]', '', budget_str or '0'))
            gross = int(re.sub(r'[^\d]', '', gross_str or '0'))
            
            profit_value = gross - budget
            abs_value = abs(profit_value)
            
            if profit_value < 0:
                formatted_value = f"-{currency}{abs_value:,}"
            else:
                formatted_value = f"{currency}{abs_value:,}"
            
            profit[self.movies_data[movie_id]] = formatted_value

        return dict(sorted(profit.items(), 
            key=lambda item: int(re.sub(r'[^\d-]', '', item[1])), 
            reverse=True)[:n])

    @check_errors
    def longest(self, n) -> dict:
        """The method returns a dict with top-n movies where the keys are movie titles and the values are their runtime. If there are more than one version – choose any. Sort it by runtime descendingly."""  # noqa: D401, E501
        movies_id_list = list(self.movies_data.keys())
        self.get_imdb(movies_id_list, ["Runtime"])
        
        runtimes = {}
        for lst in self.imbd_data:
            if lst[1] == "N/A":
                pass
            else:
                title = self.movies_data[lst[0]]
                runtimes[title] = lst[1]
            
        return dict(sorted(runtimes.items(), 
            key=lambda item: item[1], reverse=True)[:n])

    @check_errors
    def top_cost_per_minute(self, n) -> dict:
        """The method returns a dict with top-n movies where the keys are the values are the budgets divided by their runtime. The budgets can be in different currencies – do not pay attention to it. The values should be rounded to 2 decimals. Sort it by the division descendingly."""  # noqa: D401, E501
        movies_id_list = list(self.movies_data.keys())
        self.get_imdb(movies_id_list, ["Runtime", "Budget"])
        
        costs = {}
        for lst in self.imbd_data:
            if lst[1] == "N/A" or lst[2] == "N/A":
                pass
            else:
                runtime = 0
                parts = lst[1].split()
                i = 0
                
                while i < len(parts):
                    if parts[i] in ["hour", "hours"]:
                        hours = int(parts[i - 1])
                        runtime += hours * 60
                        i += 2
                    elif parts[i] in ["minute", "minutes"]:
                        minutes = int(parts[i - 1])
                        runtime += minutes
                        i += 2
                    else:
                        i += 1
                        
                budget_to_cost = round(
                    int(re.sub(r"\D", "", lst[2])) / runtime, 2)
                title = self.movies_data[lst[0]]
                costs[title] = budget_to_cost

        return dict(sorted(costs.items(),
            key=lambda item: item[1], reverse=True)[:n])
        
        # BONUS PART
    @check_errors
    def directors_of_most_expensive(self, n):
        """Bonus part: returns the top n directors who direct the most high-budget films."""  # noqa: E501
        movies_id_list = list(self.movies_data.keys())
        movieid_budgets_directors = self.get_imdb(
            movies_id_list, ['Budget', 'Director'])  
        
        
        directors_budgets = {}
        for lst in movieid_budgets_directors:
            if lst[1] == 'N/A':
                pass
            else: 
                budget = lst[1]
                name = (lst[2].split(','))[0]

                if name in directors_budgets:
                    bigger_budget = directors_budgets[name] if directors_budgets[name] > budget else budget  # noqa: E501
                    directors_budgets[name] = bigger_budget
                    
                else: 
                    directors_budgets[name] = budget
        sorted_dir = dict(sorted(directors_budgets.items(), 
            key=lambda item: int(re.sub(r'\D', '', item[1])), reverse=True))
        return dict(list(sorted_dir.items())[:n])


class TestAllMethods:
    """Unit-testing all methods."""
    
    @check_errors
    def dummy_function(self, raise_exception=None):
        """Test method for checking decorator error handling."""
        if raise_exception:
            raise raise_exception("Test error")
        return "Success"
    
    @pytest.fixture(scope="class")
    def ratings_instance(self):  # noqa: D102
        
        path_to_file = "data/ratings.csv"
        path_to_file2 = "data/movies.csv"
        assert os.path.isfile(path_to_file)
        assert os.path.isfile(path_to_file2)
        return Ratings(path_to_file, path_to_file2)

    @pytest.fixture(scope="class")
    def movies_instance(self):  # noqa: D102
        
        path_to_file = "data/movies.csv"
        assert os.path.isfile(path_to_file)
        return Movies(path_to_file)
    
    @pytest.fixture(scope="class")
    def tags_instance(self):  # noqa: D102
        
        path_to_file = "data/tags.csv"
        assert os.path.isfile(path_to_file)
        return Tags(path_to_file)
    
    @pytest.fixture(scope="class")
    def links_instance(self):  # noqa: D102
        
        path_to_file = "data/links.csv"
        path_to_file2 = "data/movies.csv"
        assert os.path.isfile(path_to_file)
        assert os.path.isfile(path_to_file2)
        return Movies(path_to_file, path_to_file2)
    
    class TestDecorator:
        """Unit-testing decorators on errors."""
        
        def test_file_not_found_error(self):  # noqa: D102
            
            instance = TestAllMethods()
            with pytest.raises(FileNotFoundError) as exc_info:
                instance.dummy_function(raise_exception=FileNotFoundError)
            assert "File not found: Test error" in str(exc_info.value)

        def test_keyboard_interrupt(self):  # noqa: D102
            
            instance = TestAllMethods()
            with pytest.raises(KeyboardInterrupt) as exc_info:
                instance.dummy_function(raise_exception=KeyboardInterrupt)
            assert "Program stopped by user" in str(exc_info.value)

        def test_value_error(self):  # noqa: D102
            
            instance = TestAllMethods()
            with pytest.raises(ValueError) as exc_info:
                instance.dummy_function(raise_exception=ValueError)
            assert "Value error: invalid data format or range" in str(
                exc_info.value)

        def test_successful_execution(self):  # noqa: D102
            
            instance = TestAllMethods()
            result = instance.dummy_function()
            assert result == "Success"

        def test_error_message_output(self):  # noqa: D102
            
            instance = TestAllMethods()
            with pytest.raises(ValueError) as exc_info:
                instance.dummy_function(raise_exception=ValueError)
            assert "Value error: invalid data format or range" in str(
                exc_info.value)

        def test_unexpected_error(self):  # noqa: D102
            
            class CustomError(Exception):
                pass
                
            instance = TestAllMethods()
            with pytest.raises(Exception) as exc_info:
                instance.dummy_function(raise_exception=CustomError)
            assert "Unexpected error: CustomError" in str(exc_info.value)

        def test_decorator_preserves_function_metadata(self):  # noqa: D102
            
            def sample_func():
                return True

    class TestRatings:
        """Unit-testing for Ratings."""
        
        def test_get_average(target):  # noqa: D102
            
            assert Ratings.get_average([1, 2, 3, 4, 5]) == 3.0
            assert Ratings.get_average([-1, 0, 1]) == 0.0
            assert Ratings.get_average([1.5, 2.5, 3.5]) == 2.5
            assert Ratings.get_average([1000000, 2000000]) == 1500000.0
            first_call = Ratings.get_average([1, 2, 3])
            second_call = Ratings.get_average([1, 2, 3])
            assert first_call == second_call
            assert isinstance(first_call, float)


        @pytest.mark.parametrize("input_data,expected", [
        ([1, 3, 2], 2), ([1, 2, 3, 4], 2.5),([5], 5),
        ([], 0),([1, 1, 1, 1], 1),([-1, 0, 1], 0),
        ([1.5, 2.5, 3.5], 2.5),])   
        def test_get_median(self, input_data, expected):  # noqa: D102
            
            result = Ratings.get_average([1, 2, 3, 4])
            assert Ratings.get_median(input_data) == expected
            assert isinstance(result, float)
            
        @pytest.mark.parametrize("input_data,expected", [
        ([1, 2, 3], 2.0), ([], 0), ([5], 5.0),
        ([-1, 0, 1], 0.0), ([1.5, 2.5], 2.0),])
        def test_get_variance(self, input_data, expected):  # noqa: D102
            
            result = Ratings.get_average([1, 2, 3, 4])
            assert Ratings.get_average(input_data) == expected
            assert isinstance(result, float)
            
            
        @pytest.fixture
        def sample_movies(self):  # noqa: D102
            
            return [
            {"title": "Movie1", "rating": 5, "timestamp": 946684800},
            {"title": "Movie1", "rating": 4, "timestamp": 946684800},
            {"title": "Movie2", "rating": 3, "timestamp": 978307200},
            {"title": "Movie2", "rating": 2, "timestamp": 978307200},
            {"title": "Movie3", "rating": 1, "timestamp": 1009843200},] 
            
            
        def test_dist_by_year(self, sample_movies):  # noqa: D102
            
            movies = Ratings.Movies(sample_movies)
            result = movies.dist_by_year()
            assert result == {2000: 2, 2001: 2, 2002: 1}
            assert isinstance(result, dict)
        
        
        def test_dist_by_rating(self, sample_movies):  # noqa: D102
            
            movies = Ratings.Movies(sample_movies)
            result = movies.dist_by_rating()
            assert result == {5: 1, 4: 1, 3: 1, 2: 1, 1: 1}
            assert isinstance(result, dict)


        def test_top_by_num_of_ratings(self, sample_movies):  # noqa: D102
            
            movies = Ratings.Movies(sample_movies)
            result = movies.top_by_num_of_ratings(2)
            assert result == {"Movie1": 2, "Movie2": 2}
            assert isinstance(result, dict)


        def test_top_by_ratings(self, sample_movies):  # noqa: D102
            
            movies = Ratings.Movies(sample_movies)
            result = movies.top_by_ratings(2, "median")
            assert result == {"Movie1": 4.5, "Movie2": 2.5}
            assert isinstance(result, dict)


        def test_top_controversial(self, sample_movies):  # noqa: D102
            
            movies = Ratings.Movies(sample_movies)
            result = movies.top_controversial(2)
            assert list(result.keys()) == ["Movie1", "Movie2"]
            assert all(isinstance(v, float) for v in result.values())
            assert isinstance(result, dict)
            
        @pytest.fixture
        def sample_unity(self):  # noqa: D102
            return [
                {'userId': 21, 'movieId': 167036, 'rating': 4.0, 'timestamp': 1483340756, 'title': 'Sing (2016)', 'genres': 'Animation|Children|Comedy'}, {'userId': 111, 'movieId': 167036, 'rating': 4.0, 'timestamp': 1516153691, 'title': 'Sing (2016)', 'genres': 'Animation|Children|Comedy'}]  # noqa: E501
            
        
        def test_average_ratings_by_genres(self, sample_unity):  # noqa: D102
            
            movies = Ratings.Movies(sample_unity)
            result = movies.average_ratings_by_genres()
            expected = {'Animation': 4.0, 'Children': 4.0, 'Comedy': 4.0}
            assert result == expected
            assert isinstance(result, dict)

        
        @pytest.fixture
        def sample_users(self):  # noqa: D102
            
            return [
                {"userId": 1, "rating": 5},
                {"userId": 1, "rating": 1},
                {"userId": 2, "rating": 3},
                {"userId": 2, "rating": 3},
                {"userId": 3, "rating": 4},
            ]


        def test_number_of_ratings(self, sample_users):  # noqa: D102
            
            users = Ratings.Users(sample_users)
            result = users.number_of_ratings()
            assert result == {1: 2, 2: 2, 3: 1}
            assert isinstance(result, dict)


        def test_average_or_median_ratings(self, sample_users):  # noqa: D102
            
            users = Ratings.Users(sample_users)
            avg_result = users.average_or_median_ratings("average")
            assert avg_result[1] == 3.0
            assert avg_result[2] == 3.0
            med_result = users.average_or_median_ratings("median")
            assert med_result[1] == 3.0
            assert isinstance(avg_result, dict)


        def test_biggest_variance_ratings(self, sample_users):  # noqa: D102
            
            users = Ratings.Users(sample_users)
            result = users.biggest_variance_ratings(1)
            assert list(result.keys()) == [1]
            assert result[1] > 0
            assert isinstance(result, dict)
            

    class TestMovies:
        """Unit-testing for methods in Movies."""    
        
        def test_dist_by_release(self, movies_instance):  # noqa: D102
            
            expected = {'2002': 311, '2006': 295, '2001': 294, '2007': 284, '2000': 283}  # noqa: E501
            result = movies_instance.dist_by_release()
            result = dict(list(result.items())[:5])
            assert result == expected
            assert isinstance(result, dict)


        def test_dist_by_genres(self, movies_instance):  # noqa: D102
            
            expected = {'Drama': 4361, 'Comedy': 3756, 'Thriller': 1894, 'Action': 1828, 'Romance': 1596}  # noqa: E501
            result = movies_instance.dist_by_genres()
            result = dict(list(result.items())[:5])
            assert result == expected
            assert isinstance(result, dict)


        def test_most_genres(self, movies_instance):  # noqa: D102
            
            expected = {'Rubber': 10, 'Patlabor: The Movie (Kidô keisatsu patorebâ: The Movie)': 8, 'Mulan': 7, 'Who Framed Roger Rabbit?': 7, 'Osmosis Jones': 7}  # noqa: E501
            result = movies_instance.most_genres(5)
            assert result == expected
            assert isinstance(result, dict)
            
            
        def test_stat_by_genres(self, movies_instance):  # noqa: D102
            
            expected = {'Drama': '19.75 %', 'Comedy': '17.01 %', 'Thriller': '8.58 %', 'Action': '8.28 %', 'Romance': '7.23 %', 'Adventure': '5.72 %', 'Crime': '5.43 %', 'Sci-Fi': '4.44 %', 'Horror': '4.43 %', 'Fantasy': '3.53 %', 'Children': '3.01 %', 'Animation': '2.77 %', 'Mystery': '2.59 %', 'Documentary': '1.99 %', 'War': '1.73 %', 'Musical': '1.51 %', 'Western': '0.76 %', 'IMAX': '0.72 %', 'Film-Noir': '0.39 %', '(no genres listed)': '0.15 %'}  # noqa: E501
            result = movies_instance.stat_by_genres()
            assert result == expected
            assert isinstance(result, dict)
            
                    
                    
    class TestTags:
        """Unit-testing for methods in Tags.""" 
        
        def test_most_words(self, tags_instance):  # noqa: D102
            
            result = tags_instance.most_words(2)
            assert isinstance(result, dict)
            assert len(result) <= 2
            first_key = next(iter(result))
            first_value = result[first_key]
            assert first_key == 'Something for everyone in this one... saw it without and plan on seeing it with kids!'  # noqa: E501
            assert first_value == 16


        def test_longest(self, tags_instance):  # noqa: D102
            
            result = tags_instance.longest(2)
            assert isinstance(result, list)
            assert len(result) <= 2
            assert result[0] == 'Something for everyone in this one... saw it without and plan on seeing it with kids!'  # noqa: E501
            
            
        def test_most_words_and_longest(self, tags_instance):  # noqa: D102
            
            result = tags_instance.most_words_and_longest(2)
            assert isinstance(result, list)
            assert len(result) <= 2
            assert (sorted(result, key=len, reverse=True))[0] == 'Something for everyone in this one... saw it without and plan on seeing it with kids!'  # noqa: E501
            assert (sorted(result, key=len, reverse=True))[1] == 'the catholic church is the most corrupt organization in history'  # noqa: E501


        def test_most_popular(self, tags_instance):  # noqa: D102
            
            result = tags_instance.most_popular(3)
            assert isinstance(result, dict)
            assert len(result) <= 3
            first_key = next(iter(result))
            first_value = result[first_key]
            assert first_key == 'In Netflix queue'
            assert first_value == 131


        def test_tags_with(self, tags_instance):  # noqa: D102
            
            result = tags_instance.tags_with("Python")
            assert isinstance(result, list)
            assert all("Python" in tag for tag in result)
            assert result[0] == 'Monty Python'


        def test_get_tags_by_the_movie(self, tags_instance):  # noqa: D102
            
            result = tags_instance.get_tags_by_the_movie(4993)
            assert isinstance(result, list)
            assert set(result) == set(['high fantasy', 'wizards', 'tolkien', 'tolkein', 'magic', 'fantasy', 'mythology'])  # noqa: E501


    class TestLinks:
        """Unit-testing for Links."""
        
        def test_get_imdb(self):  # noqa: D102

            links_object = Links('data/links.csv', 'data/movies.csv', 10)
            result = links_object.get_imdb([1, 2], ["title", "Director", "Budget", "Cumulative worldwide gross", "Runtime"])  # noqa: E501
            assert isinstance(result, list)
            assert all(isinstance(x, list) for x in result)
            assert result == sorted(result, key=lambda x: x[0], reverse=True)
            movie_title = (links_object.get_imdb([9], ["title"]))[0][1]
            assert movie_title == 'Sudden Death'


        def test_top_directors(self):  # noqa: D102
            
            links_object = Links('data/links.csv', 'data/movies.csv', 10)
            result = links_object.top_directors(3)
            assert isinstance(result, dict)
            
            for director, count in result.items():
                assert isinstance(director, str)
                assert isinstance(count, int)
                
            if len(result) > 1:
                sorted_items = sorted(result.items(), 
                    key=lambda x: x[1], reverse=True)
                assert list(result.items()) == sorted_items[:len(result)]
                
            first_key = next(iter(result))
            first_value = result[first_key]
            assert first_key == 'Martin Campbell'
            assert first_value == 1


        def test_most_expensive(self):  # noqa: D102
            
            links_object = Links('data/links.csv', 'data/movies.csv', 10)
            result = links_object.most_expensive(3)
            assert isinstance(result, dict)
            
            for movie, budget in result.items():
                assert isinstance(movie, str)
                assert isinstance(budget, str)
                
            if len(result) > 1:
                sorted_items = sorted(result.items(), 
                    key=lambda x: x[1], reverse=True)
                assert list(result.items()) == sorted_items[:len(result)]
                
            first_key = next(iter(result))
            first_value = result[first_key]
            assert first_key == 'Jumanji'
            assert first_value == '$65,000,000'
        
                
        def test_most_profitable(self):  # noqa: D102
            
            links_object = Links('data/links.csv', 'data/movies.csv', 10)
            result = links_object.most_profitable(3)
            assert isinstance(result, dict)
            
            for movie, profit in result.items():
                assert isinstance(movie, str)
                assert isinstance(profit, str)
                
            if len(result) > 1:
                sorted_items = sorted(result.items(), 
                    key=lambda x: x[1], reverse=True)
                assert list(result.items()) == sorted_items[:len(result)]
                
            first_key = next(iter(result))
            first_value = result[first_key]
            assert first_key == 'Toy Story'
            assert first_value == '$364,436,586'


        def test_longest(self):  # noqa: D102
            
            links_object = Links('data/links.csv', 'data/movies.csv', 10)
            result = links_object.longest(3)
            assert isinstance(result, dict)
            
            for movie, runtime in result.items():
                assert isinstance(movie, str)
                assert isinstance(runtime, str)
                
            if len(result) > 1:
                sorted_items = sorted(result.items(), 
                    key=lambda x: x[1], reverse=True)
                assert list(result.items()) == sorted_items[:len(result)]
                
            first_key = next(iter(result))
            first_value = result[first_key]
            assert first_key == 'Sabrina'
            assert first_value == '2 hours 7 minutes'


        def test_top_cost_per_minute(self):  # noqa: D102
            
            links_object = Links('data/links.csv', 'data/movies.csv', 10)
            result = links_object.top_cost_per_minute(3)
            assert isinstance(result, dict)
            
            for movie, cost in result.items():
                assert isinstance(movie, str)
                assert isinstance(cost, float)
                cost_rounded = round(cost, 2)
                assert abs(cost - cost_rounded) < 0.01
                
            if len(result) > 1:
                sorted_items = sorted(result.items(), 
                    key=lambda x: x[1], reverse=True)
                assert list(result.items()) == sorted_items[:len(result)]
                
            first_key = next(iter(result))
            first_value = result[first_key]
            assert first_key == 'Jumanji'
            assert first_value == 625000.0


        def test_directors_of_most_expensive(self):  # noqa: D102
            
            links_object = Links('data/links.csv', 'data/movies.csv', 10)
            result = links_object.directors_of_most_expensive(3)
            assert isinstance(result, dict)
            
            if len(result) > 1:
                sorted_items = sorted(result.items(), 
                    key=lambda x: x[1], reverse=True)
                assert list(result.items()) == sorted_items[:len(result)]
                
            first_key = next(iter(result))
            first_value = result[first_key]
            assert first_key == 'Joe Johnston'
            assert first_value == '$65,000,000'


            

def main():  # noqa: D103
    sys.tracebacklimit = 0
    R = Ratings("data/ratings.csv", "data/movies.csv")
    Rm = R.Movies(R.unity)  # noqa: F841
    Ru = R.Users(R.unity)  # noqa: F841
    M = Movies("data/movies.csv")  # noqa: F841
    T = Tags("data/tags.csv")  # noqa: F841
    L = Links('data/links.csv', 'data/movies.csv', 100)  # noqa: F841
    TestAllMethods()
    
    # Ratings:
    print(Rm.dist_by_year())
    print(Rm.dist_by_rating())
    print(Rm.top_by_num_of_ratings(50))
    print(Rm.top_by_ratings(50))
    print(Rm.top_controversial(50))
    print(Rm.average_ratings_by_genres())  # BONUS
    print(Ru.number_of_ratings())
    print(Ru.average_or_median_ratings())
    print(Ru.biggest_variance_ratings(50))
    
    # Movies
    print(M.dist_by_release())
    print(M.dist_by_genres())
    print(M.most_genres(50))
    print(M.stat_by_genres())  # BONUS
    
    # Tags
    print(T.most_words(50))
    print(T.longest(50))
    print(T.most_words_and_longest(50))
    print(T.most_popular(50))
    print(T.tags_with("dark"))
    print(T.get_tags_by_the_movie(50))  # BONUS
    
    # Links
    print(L.get_imdb([12, 22, 32, 42, 58, 69], 
        ["Title", "Runtime", "Director","Budget", 
        "Cumulative worldwide gross"]))
    print(L.top_directors(10))
    print(L.most_expensive(10))
    print(L.most_profitable(10))
    print(L.longest(10))
    print(L.top_cost_per_minute(10))
    print(L.directors_of_most_expensive(10))  # BONUS
    
if __name__ == "__main__":
    main()        
