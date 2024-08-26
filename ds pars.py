import requests
from bs4 import BeautifulSoup
import json
import time

# Параметры для поиска
search_url = "https://hh.ru/search/vacancy"
params = {
    "text": "Python",
    "area": [1, 2],  # Москва и Санкт-Петербург
    "items_on_page": "20",
    "page": 0,  # Начальная страница
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
}

# Функция для проверки наличия ключевых слов
def contains_keywords(description, keywords):
    return all(keyword.lower() in description.lower() for keyword in keywords)

# Сбор вакансий
vacancies = []
keywords = ["Django", "Flask"]

while True:
    response = requests.get(search_url, headers=headers, params=params)
    soup = BeautifulSoup(response.text, "html.parser")
    
    vacancy_items = soup.find_all("div", class_="vacancy-serp-item")
    
    if not vacancy_items:
        break  # Если вакансий больше нет, выходим из цикла
    
    for item in vacancy_items:
        title = item.find("a", class_="serp-item__title").text
        link = item.find("a", class_="serp-item__title")["href"]
        company = item.find("a", class_="bloko-link bloko-link_kind-tertiary").text.strip()
        city = item.find("div", {"data-qa": "vacancy-serp__vacancy-address"}).text.strip()
        salary = item.find("span", {"data-qa": "vacancy-serp__vacancy-compensation"})
        
        if salary:
            salary = salary.text.strip()
        else:
            salary = "Не указана"
        
        # Открываем ссылку на вакансию для получения описания
        vacancy_response = requests.get(link, headers=headers)
        vacancy_soup = BeautifulSoup(vacancy_response.text, "html.parser")
        description = vacancy_soup.find("div", {"data-qa": "vacancy-description"}).text
        
        if contains_keywords(description, keywords):
            # Фильтрация по зарплате в долларах (если требуется)
            if "USD" in salary:
                vacancies.append({
                    "title": title,
                    "link": link,
                    "company": company,
                    "city": city,
                    "salary": salary,
                })
    
    # Переход на следующую страницу
    params["page"] += 1
    time.sleep(1)  # Даем паузу между запросами, чтобы не перегружать сервер

# Запись в JSON файл
with open("vacancies.json", "w", encoding="utf-8") as file:
    json.dump(vacancies, file, ensure_ascii=False, indent=4)

print(f"Собрано {len(vacancies)} вакансий.")
