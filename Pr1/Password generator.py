import random

def generate_encrypted_word(length=7):
  valid_chars = list(range(33, 127))
  # Generate a random password of the specified length
  encrypted_word = "".join(chr(random.choice(valid_chars)) for _ in range(length))
  return encrypted_word


encrypted_word = generate_encrypted_word()
print(encrypted_word)
