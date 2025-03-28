import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.io as pio
import io
import base64


# Fraud categories and keywords
fraud_keywords = {
    # Financial Fraud
    "Crypto Fraud": ["crypto scam", "cryptocurrency fraud", "bitcoin scam", "blockchain fraud", "fake ICO", "crypto mining scam"],
    "SMS Scam": ["sms scam", "sms fraud", "fraud via SMS", "text scam", "smishing"],
    "Phishing": ["phishing email", "email phishing", "spear phishing", "phishing scam", "phishing website"],
    "OTP Fraud": ["otp scam", "otp fraud", "one-time password fraud", "sms otp fraud"],
    "Call Scam": ["call fraud", "phone scam", "vishing", "voice phishing", "fraudulent phone call"],
    "Bank Fraud": ["bank fraud", "account takeover", "wire transfer fraud", "banking phishing"],
    
    # Cybersecurity Threats
    "Malware": ["malware attack", "ransomware", "virus infection", "trojan horse", "cryptojacking", "spyware"],
    "Spyware": ["spyware attack", "keylogger", "data theft", "surveillance malware"],
    "DDoS Attack": ["ddos attack", "distributed denial of service", "service outage", "traffic amplification attack"],
    "Brute Force Attack": ["brute force attack", "password cracking", "credential stuffing"],
    "SQL Injection": ["sql injection", "database exploit", "unauthorized database access"],
    "Zero-Day Exploit": ["zero-day exploit", "unknown vulnerability", "zero-day attack"],
    "Man-in-the-Middle": ["man-in-the-middle attack", "MITM attack", "eavesdropping attack"],
    "DNS Spoofing": ["dns spoofing", "dns attack", "domain hijack"],
    
    # AI and Automation Failures
    "AI System Failure": ["ai system failure", "machine learning glitch", "ai malfunction"],
    "Automation Error": ["automation failure", "robotic process automation error", "script failure"],
    "Chatbot Failure": ["chatbot failure", "chatbot error", "ai conversation issue"],
    
    # System Failures
    "System Outage": ["system outage", "system failure", "server crash", "downtime"],
    "Network Failure": ["network failure", "network outage", "connectivity issue"],
    "Cloud Service Failure": ["cloud service failure", "cloud outage", "cloud platform crash"],
    "Power Outage": ["power outage", "electricity failure", "energy disruption"],
    
    # Social Engineering Attacks
    "Social Engineering": ["social engineering attack", "impersonation", "psychological manipulation"],
    "Baiting": ["baiting attack", "usb drop attack", "physical media scam"],
    "Tailgating": ["tailgating attack", "physical intrusion", "unauthorized access"],
    
    # Insider Threats
    "Insider Threat": ["insider threat", "employee misconduct", "internal fraud"],
    "Privilege Misuse": ["privilege misuse", "unauthorized access", "data leakage"],
    
    # Data Breaches and Leaks
    "Data Breach": ["data breach", "data leak", "personal information exposure", "data scraping"],
    "Ransomware": ["ransomware attack", "data encryption", "ransom demand"],
    "Data Theft": ["data theft", "data exfiltration", "information stealing"],
    
    # Software Vulnerabilities
    "Software Bug": ["software bug", "application error", "code vulnerability"],
    "Patch Management Issue": ["patch management issue", "unpatched system", "outdated software"],
    
    # Physical Security Breaches
    "Physical Security Breach": ["physical security breach", "unauthorized building access", "badge cloning"],
    "Device Theft": ["device theft", "laptop theft", "smartphone theft"],
    
    # AI-Powered Attacks
    "Deepfake Fraud": ["deepfake fraud", "ai-generated video", "synthetic identity fraud"],
    "Voice Cloning Attack": ["voice cloning attack", "synthetic voice fraud", "ai voice manipulation"],
    
    # Internet of Things (IoT) Vulnerabilities
    "IoT Vulnerability": ["iot vulnerability", "smart device hack", "connected device exploit"],
    "IoT Botnet": ["iot botnet", "mirai botnet", "internet of things attack"],
    
    # Supply Chain Attacks
    "Supply Chain Attack": ["supply chain attack", "third-party compromise", "vendor attack"],
    
    # Cloud Security Incidents
    "Cloud Misconfiguration": ["cloud misconfiguration", "insecure cloud storage", "cloud data exposure"],
    
    # Emerging Threats
    "Quantum Computing Threat": ["quantum computing threat", "post-quantum cryptography", "quantum attack"],
    "IoT Malware": ["iot malware", "smart device virus", "connected device malware"],
    
    # New Fraud Categories
    "Prank Calls": ["prank call", "joke call", "fake bomb threat", "hoax call"],
    "Gambling Fraud": ["fake online casino", "online gambling scam", "sports betting fraud", "lottery fraud", "fake lottery win"],
    "Social Media Scams": ["fake social media accounts", "romance scams", "social media phishing", "fake influencer scam", "scam dating profile"],
    "Job Scams": ["fake job offers", "employment phishing scams", "work-from-home scams", "fake interview scam", "fake recruiter scam"],
    "E-commerce Fraud": ["fake e-commerce site", "non-delivery fraud", "payment fraud", "fake product listings", "fake customer service scam"],
    "Cyberbullying": ["cyberbullying", "online harassment", "doxxing", "trolling", "cyberstalking", "sextortion"],
    "Cryptocurrency Scams": ["crypto fraud", "bitcoin scam", "cryptocurrency theft", "ponzi scheme", "pump and dump", "fake ICO"],
    "Hacking": ["hacked account", "data breach", "server compromise", "security breach", "unauthorized access"]
}

# Example scraping websites
websites = [
    {"name": "TechCrunch", "url": "https://techcrunch.com/"},
    {"name": "Hacker News", "url": "https://news.ycombinator.com/"},
    {"name": "krebsonsecurity", "url": "https://krebsonsecurity.com/"},
]

# Function to scrape articles
def scrape_articles(websites):
    articles = []
    for site in websites:
        response = requests.get(site["url"])
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            for a in soup.find_all('a', href=True):
                title = a.text.strip()
                if len(title) > 30:
                    articles.append({"Article": title})
    return articles

# Function to tag articles
def tag_articles(articles, keywords):
    tagged_articles = []
    for item in articles:
        article = item["Article"]
        tags = []
        for fraud_type, keyword_list in keywords.items():
            for keyword in keyword_list:
                if re.search(rf'\b{keyword}\b', article, re.IGNORECASE):
                    tags.append(fraud_type)
        tagged_articles.append({
            "Article": article,
            "Tags": ", ".join(set(tags)) if tags else "Threat Not Found"
        })
    return tagged_articles

# Scrape and tag
scraped_articles = scrape_articles(websites)
tagged_articles = tag_articles(scraped_articles, fraud_keywords)

# Create DataFrame
df = pd.DataFrame(tagged_articles)

# Prepare tag counts for the dashboard
tag_counts = df['Tags'].value_counts().reset_index()
tag_counts.columns = ['Fraud Type', 'Count']

# Create the dashboard using Dash
app = dash.Dash(__name__)

# Layout
app.layout = html.Div(
    style={'backgroundColor': '#f4f4f4', 'padding': '20px'},
    children=[
        html.H1("Cybersecurity Threats Dashboard", style={'textAlign': 'center', 'color': '#2c3e50'}),
        
        html.Div([
            html.Label("Select Chart Type:", style={'color': '#2c3e50'}),
            dcc.Dropdown(
                id='chart-type-dropdown',
                options=[
                    {'label': 'Bar Chart', 'value': 'bar'},
                    {'label': 'Pie Chart', 'value': 'pie'},
                ],
                value='bar',
                clearable=False,
                style={'width': '50%'}
            ),
        ], style={'marginBottom': '30px'}),

        dcc.Graph(id='fraud-chart'),

        html.H2("Detailed Tagged Articles", style={'color': '#2c3e50'}),
        html.Table(
            # Add a header row
            [html.Tr([html.Th(col, style={'border': '1px solid black', 'padding': '8px', 'backgroundColor': '#ccc'}) for col in df.columns])] +
            # Add data rows
            [html.Tr([
                html.Td(df.iloc[i][col], style={'border': '1px solid black', 'padding': '8px'}) for col in df.columns
            ]) for i in range(len(df))],
            style={
                'width': '100%',
                'borderCollapse': 'collapse',
                'marginTop': '20px'
            }
        ),
        
        html.Button("Download CSV Report", id="download-csv", n_clicks=0),
        dcc.Download(id="download-dataframe-csv"),

        html.Button("Download Chart Image", id="download-chart", n_clicks=0),
        dcc.Download(id="download-chart-image"),
    ]
)

# Callback to update the chart based on the selected chart type
@app.callback(
    Output('fraud-chart', 'figure'),
    Input('chart-type-dropdown', 'value')
)
def update_chart(chart_type):
    if chart_type == 'bar':
        fig = px.bar(
            tag_counts,
            x='Fraud Type',
            y='Count',
            title="Fraud Type Distribution",
            color='Fraud Type',
            text_auto=True,
            template='plotly_white'
        )
    elif chart_type == 'pie':
        fig = px.pie(
            tag_counts,
            names='Fraud Type',
            values='Count',
            title="Fraud Type Distribution",
            template='plotly_white'
        )
    
    return fig

# Callback to download CSV file
@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("download-csv", "n_clicks"),
    prevent_initial_call=True,
)
def download_csv(n_clicks):
    return dcc.send_data_frame(df.to_csv, "fraud_report.csv")

# Callback to download chart image
@app.callback(
    Output("download-chart-image", "data"),
    Input("download-chart", "n_clicks"),
    Input('chart-type-dropdown', 'value'),
    prevent_initial_call=True,
)
def download_chart(n_clicks, chart_type):
    if chart_type == 'bar':
        fig = px.bar(
            tag_counts,
            x='Fraud Type',
            y='Count',
            title="Fraud Type Distribution",
            color='Fraud Type',
            text_auto=True,
            template='plotly_white'
        )
    else:
        fig = px.pie(
            tag_counts,
            names='Fraud Type',
            values='Count',
            title="Fraud Type Distribution",
            template='plotly_white'
        )
    
    img_bytes = pio.to_image(fig, format='png')
    return dict(content=base64.b64encode(img_bytes).decode(), filename="fraud_chart.png")

# Run the dashboard
if __name__ == '__main__':
    app.run_server(debug=True)
