MORSE_DICT = {
    '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E', '..-.': 'F', '--.': 'G', 
    '....': 'H', '..': 'I', '.---': 'J', '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', 
    '---': 'O', '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T', '..-': 'U', 
    '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y', '--..': 'Z', '.----': '1', 
    '..---': '2', '...--': '3', '....-': '4', '.....': '5', '-....': '6', '--...': '7', 
    '---..': '8', '----.': '9', '-----': '0'
}

def morse_to_text(morse_str):
        message = ""

        words = morse_str.split(" / ")
        for i, word in enumerate(words):
            letters = word.split(" ")
            for letter in letters:
                if letter == "":
                    continue
                
                message += MORSE_DICT.get(letter, "?")

            if i < len(words) - 1:
                message += " "

        return message