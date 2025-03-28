from flask import Flask, render_template
import requests
from bs4 import BeautifulSoup
from datetime import datetime

app = Flask(__name__)

# Groq API details
groq_api_key = "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"
groq_api_url = "https://api.groq.com/openai/v1/chat/completions"  # Correct API endpoint
groq_model = "llama3-8b-8192"


def summarize_text(text):
    """
    Send text to the Groq API and return the summarized response.
    """
    headers = {
        "Authorization": f"Bearer {groq_api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": groq_model,
        "messages": [
            {"role": "system", "content": "Summarize this information in 6 lines."},
            {"role": "user", "content": text}
        ]
    }

    response = requests.post(groq_api_url, json=data, headers=headers)

    if response.status_code == 200:
        groq_response = response.json()
        return groq_response['choices'][0]['message']['content'].strip()
    else:
        return "Summary unavailable"


def scrape_krebs_latest_news():
    url = 'https://krebsonsecurity.com/'
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        latest_news = []
        for article in soup.find_all('article'):
            title_tag = article.find('h2', class_='entry-title')
            date_tag = article.find('span', class_='date updated')
            desc_tag = article.find('div', class_='entry-content')
            if title_tag and title_tag.find('a'):
                description = desc_tag.get_text(strip=True).split('.')[0] if desc_tag else 'No description available'
                summary = summarize_text(description)
                latest_news.append({
                    'title': title_tag.get_text(strip=True),
                    'link': title_tag.find('a')['href'],
                    'date': date_tag.get_text(strip=True) if date_tag else 'No date available',
                    'description': summary  # Replace with summarized text
                })
        return latest_news
    except Exception as e:
        return [{'title': 'Error fetching Krebs on Security', 'link': '', 'date': '', 'description': str(e)}]


def scrape_cyberscoop_news_with_date():
    url = 'https://cyberscoop.com/'
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        for article in soup.find_all('article', class_='post-item'):
            title_tag = article.find('h3', class_='post-item__title')
            link_tag = title_tag.find('a', class_='post-item__title-link') if title_tag else None
            date_tag = article.find('time', class_='post-item__date')
            description = title_tag.get_text(strip=True) if title_tag else 'No description available'
            summary = summarize_text(description)
            articles.append({
                'title': title_tag.get_text(strip=True) if title_tag else 'No title available',
                'link': link_tag['href'] if link_tag else 'No link available',
                'date': date_tag.get_text(strip=True) if date_tag else 'No date available',
                'description': summary
            })
        return articles
    except Exception as e:
        return [{'title': 'Error fetching CyberScoop', 'link': '', 'date': '', 'description': str(e)}]


def scrape_hacker_news():
    url = 'https://thehackernews.com/'
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        for article in soup.find_all('div', class_='body-post clear'):
            title_tag = article.find('h2', class_='home-title')
            link_tag = article.find('a', class_='story-link')
            date_tag = article.find('span', class_='h-datetime')
            description = title_tag.get_text(strip=True) if title_tag else 'No description available'
            summary = summarize_text(description)
            articles.append({
                'title': title_tag.get_text(strip=True) if title_tag else 'No title',
                'link': link_tag['href'] if link_tag else 'No link',
                'date': date_tag.get_text(strip=True) if date_tag else 'No date info',
                'description': summary
            })
        return articles
    except Exception as e:
        return [{'title': 'Error fetching The Hacker News', 'link': '', 'date': '', 'description': str(e)}]


def aggregate_cyber_incident_news():
    all_news = []
    all_news.extend(scrape_krebs_latest_news())
    all_news.extend(scrape_cyberscoop_news_with_date())
    all_news.extend(scrape_hacker_news())
    return all_news


def sort_news_by_date(news_list):
    news_with_dates = []
    news_without_dates = []
    for news in news_list:
        try:
            parsed_date = datetime.strptime(news['date'], '%B %d, %Y')
            news_with_dates.append({'news': news, 'parsed_date': parsed_date})
        except:
            news_without_dates.append(news)
    news_with_dates.sort(key=lambda x: x['parsed_date'], reverse=True)
    return [item['news'] for item in news_with_dates] + news_without_dates


@app.route('/')
def index():
    news_list = aggregate_cyber_incident_news()
    sorted_news_list = sort_news_by_date(news_list)
    return render_template('index.html', news_list=sorted_news_list)


if __name__ == "__main__":
    app.run(debug=True)
