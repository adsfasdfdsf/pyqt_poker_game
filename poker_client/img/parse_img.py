from PIL import Image

input_path = "card_deck.png"
output_folder = "./deck/"
image = Image.open(input_path)


card_width = 2179 // 13 + 1
card_height = 1216 // 5

print(card_width, card_height)
card_count = 1
for row in range(4):
    for col in range(14):
        left = col * card_width
        upper = row * card_height
        right = left + card_width
        lower = upper + card_height
        op = ""

        if row == 0:
            op = output_folder + "Spades/"
        elif row == 1:
            op = output_folder + "Diamonds/"
        elif row == 2:
            op = output_folder + "Hearts/"
        elif row == 3:
            op = output_folder + "Spears/"
        card = image.crop((left, upper, right, lower))
        card = card.resize((card_width // 3, card_height // 3))
        card.save(f"{op}card_{col + 2}.png")
        card_count += 1

