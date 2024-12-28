titles = []
title = ""

while title.lower() != "quit":
    title = input("\nEnter a title or the word 'quit' to quit: ")
    if title.lower() != "quit" and title:
        if titles and title in titles:
            print("\nThis title is already added!")
            continue
        titles.append(title)

print("\nYou've entered the following titles:\n")

for i, title in enumerate(titles, start=1):
    print(f"Title {i}: {title}\n")