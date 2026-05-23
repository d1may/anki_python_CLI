import csv, random
with open('top_1000_german_words.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    random_ = random.randint(0, 1000)
    for row in reader:
        random_ -= 1
        word = row['word']
        if random_ == 0:
            print(word)
            continue

