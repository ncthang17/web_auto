import os
import json
import datetime
from flask import Flask, render_template, request, redirect, url_for, session
from bs4 import BeautifulSoup

app = Flask(__name__)
app.secret_key = '9f2c7e4d5b7a8e1f3a2b4c6d8e9f0123'  # 본인만 아는 랜덤 키로 변경하세요

# 예시 사용자 정보 (ID, 비밀번호 및 개인 정보)
USERS = {
    "john123": {
        "password": "password123",
        "age": 30,
        "education": "학사",
        "address": "서울시",
        "phone": "010-1234-5678",
        "work_experience": "5년",
        "certificate": "파이썬 개발자 자격증"
    },
    "anna456": {
        "password": "pass456",
        "age": 28,
        "education": "석사",
        "address": "부산시",
        "phone": "010-9876-5432",
        "work_experience": "3년",
        "certificate": "데이터 분석 자격증"
    }
}

def scrape_info_page_html(user_id):
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['user_id'] = user_id
        response = client.get('/info')  # fetch HTML of /info

    soup = BeautifulSoup(response.data, 'html.parser')
    scraped_info = {}
    rows = soup.select('table tbody tr')
    for row in rows:
        cols = row.find_all('td')
        if len(cols) == 2:
            scraped_info[cols[0].get_text(strip=True)] = cols[1].get_text(strip=True)

    # Save individual JSON
    if not os.path.exists('scraped'):
        os.makedirs('scraped')
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"scraped/scraped_user_{user_id}_{timestamp}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(scraped_info, f, ensure_ascii=False, indent=2)

    # Append to combined JSON
    combined_filename = "scraped/all_scraped.json"
    if os.path.exists(combined_filename):
        with open(combined_filename, 'r', encoding='utf-8') as f:
            combined_data = json.load(f)
    else:
        combined_data = []
    combined_data.append(scraped_info)
    with open(combined_filename, 'w', encoding='utf-8') as f:
        json.dump(combined_data, f, ensure_ascii=False, indent=2)

    return scraped_info

@app.route("/")
def home():
    return redirect("/login")  # or render a template

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['id']
        password = request.form['password']
        user = USERS.get(user_id)
        if user and user['password'] == password:
            session['user_id'] = user_id
            return redirect(url_for('register'))
        else:
            return render_template('login.html', error="아이디 또는 비밀번호가 틀렸습니다.")
    return render_template('login.html')

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if 'user_id' not in session:
#         return redirect(url_for('login'))

#     user_id = session['user_id']

#     if request.method == 'POST':
#         # Instead of scraping here, just go to /info with ?scrape=1
#         return redirect(url_for('info', scrape=1))

#     return render_template('register.html', user_id=user_id)

@app.route("/register")
def register():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    return render_template('register.html', user_id=user_id)

# @app.route("/apply", methods=['POST'])
# def apply():
#     if 'user_id' not in session:
#         return redirect(url_for('login'))
#     user_id = session['user_id']
#     scraped_info = scrape_info_page_html(user_id)  # scrape info page HTML
#     return render_template('info.html', info=scraped_info)

@app.route('/apply', methods=['POST'])
def apply():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    # Scrape the info page
    scraped_info = scrape_info_page_html(user_id)

    # Option 1: Show the info page briefly, then auto-logout via JS
    return render_template('info.html', info=scraped_info, auto_logout=True)

@app.route('/info')
def info():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    user = USERS.get(user_id)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    submission = {
        "ID": user_id,
        "제출시간": timestamp,
        "나이": user["age"],
        "학력": user["education"],
        "주소": user["address"],
        "전화번호": user["phone"],
        "경력": user["work_experience"],
        "자격증": user["certificate"]
    }

    return render_template('info.html', info=submission)

# @app.route('/info')
# def info():
#     if 'user_id' not in session:
#         return redirect(url_for('login'))

#     user_id = session['user_id']
#     user = USERS.get(user_id)
#     timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

#     submission = {
#         "ID": user_id,
#         "제출시간": timestamp,
#         "나이": user["age"],
#         "학력": user["education"],
#         "주소": user["address"],
#         "전화번호": user["phone"],
#         "경력": user["work_experience"],
#         "자격증": user["certificate"]
#     }

#     # If this visit is meant to scrape
#     if request.args.get('scrape') == '1':
#         # Simulate scraping this very page
#         with app.test_client() as client:
#             with client.session_transaction() as sess:
#                 sess['user_id'] = user_id
#             response = client.get('/info')  # No scrape param to avoid infinite loop

#         soup = BeautifulSoup(response.data, 'html.parser')
#         rows = soup.select('table tbody tr')
#         scraped_info = {}
#         for row in rows:
#             cols = row.find_all('td')
#             if len(cols) == 2:
#                 scraped_info[cols[0].get_text(strip=True)] = cols[1].get_text(strip=True)

#         # Save JSON files
#         if not os.path.exists('scraped'):
#             os.makedirs('scraped')
#         filename = f"scraped/scraped_user_{user_id}_{timestamp}.json"
#         with open(filename, 'w', encoding='utf-8') as f:
#             json.dump(scraped_info, f, ensure_ascii=False, indent=2)

#         combined_filename = "scraped/all_scraped.json"
#         if os.path.exists(combined_filename):
#             with open(combined_filename, 'r', encoding='utf-8') as f:
#                 combined_data = json.load(f)
#         else:
#             combined_data = []
#         combined_data.append(scraped_info)
#         with open(combined_filename, 'w', encoding='utf-8') as f:
#             json.dump(combined_data, f, ensure_ascii=False, indent=2)

    return render_template('info.html', info=submission)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)