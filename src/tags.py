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
            tags.append(line.split(',')[2])

        uniq_tags = list(set(tags))
        for tag in uniq_tags:
            big_tags[tag] = len(tag.split(' '))
        big_tags = dict(sorted(big_tags.items(), key = lambda item: item[1], reverse = True)[:n])
        return big_tags

    def longest(self, n):
        """
        Метод возвращает top-n самых длинных тегов по количеству символов. 
        Это список тегов. Удалите дубликаты. Отсортируйте его по номерам в порядке убывания.
        """
        big_tags = {}
        tags = []
        for line in self.data:
            tags.append(line.split(',')[2])

        uniq_tags = list(set(tags))
        for tag in uniq_tags:
            big_tags[tag] = len(tag)
        big_tags = dict(sorted(big_tags.items(), key = lambda item: item[1], reverse = True)[:n])
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
            tag = line.split(',')[2] # нужен ли lower() ??? есть теги с разным регистром
            popular_tags[tag] = popular_tags.get(tag, 0) + 1

        popular_tags = dict(sorted(popular_tags.items(), key = lambda item: item[1], reverse=True)[:n])

        return popular_tags
        
    def tags_with(self, word):
        """
        Метод возвращает все уникальные теги, которые включают слово, указанное в качестве аргумента.
        Удалить дубликаты. Это список тегов. Отсортировать его по именам тегов в алфавитном порядке.
        """
        tags = []
        for line in self.data:
            tag = line.split(',')[2] 
            if word in tag:             # lower??
                tags.append(tag)

        tags_with_word = sorted(list(set(tags)))

        return tags_with_word


if __name__ == "__main__":
    tags = Tags("../data/tags.csv")
    print(tags.tags_with("top"))