import csv
from faker import Faker
import random
from transliterate import translit, get_available_language_codes

# Create a Faker instance
fake = Faker('el_GR')


# Generate relevant username based on first name and last name
def generate_username(first_name, last_name):
    rand = random.randint(1, 999)
    name1 = translit(first_name.lower(), 'el', reversed=True)
    name2 = translit(last_name.lower(), 'el', reversed=True)
    username = f"{name1}.{name2}{rand}"
    return username


# Generate random data for the table
def generate_user_data(num_records):
    data = []
    for _ in range(num_records):
        first_name = fake.first_name_male() if random.choice([True, False]) else fake.first_name_female()
        last_name = fake.last_name()
        username = generate_username(first_name, last_name)
        pwd = fake.password()
        data.append((username, pwd, first_name, last_name))
    return data


# Save data to CSV file
def save_to_csv(data, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['username', 'pwd', 'first_name', 'last_name'])  # Write header row
        writer.writerows(data)  # Write data rows


# Example usage
if __name__ == "__main__":
    num_records = 1000
    user_data = generate_user_data(num_records)
    filename = 'user_data.csv'
    save_to_csv(user_data, filename)
    print(f"Data saved to {filename}.")
