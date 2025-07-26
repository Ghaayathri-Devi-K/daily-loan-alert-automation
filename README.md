# 🎓📊 Daily Education Loan Alert Automation

This project is a fully automated daily tracker that helps me stay motivated to clear my education loan faster!  
It reads my Google Sheet disbursement data, scrapes the latest SBI EBR, calculates my daily interest, and sends me an alert every day via **email and Telegram** — fully serverless with **AWS Lambda**, **EventBridge**, **SNS**, and a custom Telegram bot.

---

### 🗂️ System Architecture  
The complete system:  
1️⃣ EventBridge → 2️⃣ Lambda → 3️⃣ Google Sheets & SBI EBR → 4️⃣ SNS → 5️⃣ Email & Telegram Bot — fully serverless and automated!

<img width="1131" height="968" alt="image" src="https://github.com/user-attachments/assets/9ff61b17-4b7b-4d7b-af60-1795a14d5ccb" />

---

## ⚙️ How It Works

1. 📅 Disbursement data → Google Sheets
2. ⏰ Scheduled trigger → EventBridge
3. 🧩 Lambda → reads data & scrapes EBR
4. 📣 SNS → Email & Telegram

---

## 🧩 System Design Details

### 1️⃣ Requirements

**Functional Requirements:**
- 🗂️ Fetch disbursement data from a Google Sheet.
- 🔍 Scrape the live External Benchmark Rate (EBR) daily.
- 🔄 Calculate daily interest based on total disbursed amount and current EBR.
- 📤 Send daily interest updates to:
  - 📧 Email (via AWS SNS)
  - 💬 Telegram Bot
- 🗓️ Run automatically every day at a fixed time.

**Non-Functional Requirements:**
- ✅ **High reliability** — Must run daily without fail.
- 💸 **Cost-effective** — Should stay within free tier/serverless.
- 🛡️ **Secure** — Google Sheets API keys and credentials must be protected.
- 📈 **Scalable** — Support multiple delivery channels (Email, Telegram, future Slack/WhatsApp).
- 🔒 **Idempotent** — Running multiple times should not create duplicate/conflicting data.

---

### 2️⃣ Capacity Estimation

- 📊 **Daily Active Users (DAU)**: 1 (Me!)
- 🚀 **Throughput**: 1 Lambda invocation/day, 1 SNS publish, 1 web scrape, 1 Google Sheets API call.
- 💾 **Storage**:  
  - Google Sheet: Tiny (~few KB).
  - No DB yet — can migrate to DynamoDB/RDS if scaling.
- 🌐 **Network/Bandwidth**:  
  - Google Sheets API + Web scrape call.
  - SNS sends 1–2 messages daily.

---

### 3️⃣ API Design

- ✅ Uses:
  - Google Sheets API (`gspread` + service account, OAuth2)
  - HTTP GET to SBI website (scraper)
  - AWS SNS Publish API
  - Telegram Bot API (HTTP POST)

---

### 4️⃣ High-Level Design

**Architecture highlights:**
- **Trigger:** AWS EventBridge cron rule.
- **Compute:** AWS Lambda.
- **Data Source:** Google Sheets.
- **Web Scraping:** SBI EBR page.
- **Message Queue:** SNS.
- **Delivery:** Email & Telegram Bot.

---

### 5️⃣ Deep Dive

**Storage Platform:**  
- Google Sheets → Lightweight pseudo-database for disbursement tracking.
(Could migrate to DynamoDB/RDS for scaling, query history, analytics)

**Message Queue:**  
- SNS → decouples compute(lambda) from notifications.
- Multiple subscribers (Email & Telegram) → classic fan-out.

**Caching:**  
By default, this project does not use a caching layer, because the EBR (External Benchmark Rate) rarely changes — most banks revise it only once a month when the RBI repo rate changes. For personal or small-scale usage, scraping SBI’s EBR daily works fine and costs nothing extra. However, if you want to make your system more robust and efficient, you can add a cache using DynamoDB with a Time To Live (TTL).
```bash
✅ Lambda checks DynamoDB for the latest EBR	
⚡ If found and not expired → use cached EBR	
🔄 If not found/expired → scrape SBI → store new EBR with TTL (~30 days)
```

**Monitoring & Logging:**  
- AWS CloudWatch logs for Lambda.

**Cloud:**  
- 100% serverless → EventBridge + Lambda + SNS.
- Scales automatically, no servers to manage.

---

### ✅ Key Design Goals

- **Scalability:** Serverless + pub/sub → easily add more channels.
- **Availability:** Lambda + EventBridge = highly reliable.
- **Consistency:** Live EBR + current disbursement → daily accurate snapshot.
- **Fault Tolerance:** Lambda retries, CloudWatch logs errors, SNS guarantees at least-once delivery.

---

### 🌐 Key Networking Concepts

- **IP Address & DNS:** Lambda makes outbound HTTPS calls to Google Sheets API & SBI website.
- **Client & Server:**  
  - Lambda = client to Google Sheets API, SBI website, Telegram Bot API.
- **Protocols:**  
  - HTTPS for all external calls.
  - AWS internal APIs for SNS publish.

---

### 📨 Key Communication Concepts

- **API:**  
  - RESTful → Google Sheets, Telegram Bot.
- **Message Queue:**  
  - SNS → fan-out → Email + Telegram Bot subscribers.

---

### 🗄️ Key Storage Concepts
 Google Sheets is the “DB”.
.

---

### 🛡️ Logging & Monitoring

- **Logs:** AWS CloudWatch for Lambda execution.
- **Monitoring:** Add CloudWatch Alarms for failures.
- **Audit:** Use CloudTrail if expanded.

---

### ⚖️ CAP Theorem

- ✅ **Consistency:** Uses fresh EBR + latest disbursement.
- ✅ **Availability:** Runs daily, serverless.
- (Partition Tolerance not directly relevant here.)

---
## 📸 **Demo — Visual Flow**

Below is a simple step-by-step walkthrough of how it works:

---

### 📊 Step 1 — Google Sheet  
My Google Sheet records every loan disbursement — with the date and amount for each installment.

<img width="1280" height="737" alt="google-sheet" src="https://github.com/user-attachments/assets/5dcd105d-ce22-45e3-9a81-aa474ae2ccd0" />


---

### ⏰ Step 2 — EventBridge Trigger  
AWS EventBridge runs a scheduled cron job daily to trigger my Lambda function 

<img width="1278" height="734" alt="eventbridge" src="https://github.com/user-attachments/assets/b2ef2e60-a526-4262-839d-238057d2c6e2" />


---

### ⚙️ Step 3 — Lambda Function  
The Lambda function reads my Google Sheet, scrapes the SBI website for the latest EBR, and calculates my daily interest.

<img width="1280" height="731" alt="lambda" src="https://github.com/user-attachments/assets/2655abba-d357-48cc-af10-80cde65cb97f" />


---

### 🔍 Step 4 — SBI EBR Scraper  
Using `requests` and `BeautifulSoup`, my Lambda fetches the current EBR rate directly from SBI’s website.

<img width="2559" height="1466" alt="image" src="https://github.com/user-attachments/assets/16aeba88-a74e-48b9-b769-33671c1cd41b" />
<br>
<img width="1280" height="734" alt="lambda2" src="https://github.com/user-attachments/assets/70a0aff8-c98a-4e90-a4fc-0fcd7725855e" />


---

### 📣 Step 5 — SNS Notification  
After calculating the daily update, Lambda publishes the alert to an SNS topic, which fans it out to my email and Telegram bot.

<img width="1280" height="736" alt="sns" src="https://github.com/user-attachments/assets/8e7ce67a-2a42-4e45-9b4d-077b54514890" />


---

### 📬 Step 6 — Email Alert  
I get a clean daily email with today’s interest, total interest so far, and my savings target — a daily push to repay faster.

<img width="1280" height="734" alt="email" src="https://github.com/user-attachments/assets/ef178295-8d2e-4f3e-af59-c2061da5b51b" />


---

### 💬 Step 7 — Telegram Bot  
The same daily update lands instantly on my Telegram via a custom bot — so I never miss it.

<img width="868" height="746" alt="telegram-message" src="https://github.com/user-attachments/assets/df4f851b-deba-4ea7-9571-c0734b36b4a6" />


---


## 📦 **Requirements**

- Python 3.8+
- `boto3` — AWS SDK for Python
- `gspread` — Google Sheets API wrapper
- `google-auth` — OAuth 2.0 for Google API
- `requests` — For HTTP scraping
- `beautifulsoup4` — For parsing SBI EBR HTML

(To install the dependencies - needed if run on cloud(AWS lambda))
pip install -t . boto3 gspread google-auth requests beautifulsoup4

---

## ⚙️ **Setup**

### 🔑 1️⃣ Google Sheets Service Account  
- Create a Google Cloud project → enable **Sheets API** & **Drive API**.  
- Create a **service account**, download `service_account.json`.  
- Share your Google Sheet with the service account email.

### ☁️ 2️⃣ AWS Resources  
- **SNS:** Create an SNS Topic. Subscribe your email & Telegram webhook.
- **Lambda:** Upload your zipped function with `service_account.json` + all Python libs.
- **EventBridge:** Create a **scheduled rule** to trigger your Lambda daily (cron).

### 🧩 3️⃣ Environment Variables  
- Store any secrets like your `TELEGRAM_BOT_TOKEN` securely.
- Reference them in your Lambda if needed.

---

## 🚀 **Run Locally**

Test your function before deploying:
```bash

# Create virtual env
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run
python lambda_fun.py
``` 
---

## 📜 License

This project is licensed under the **MIT License** — feel free to fork, adapt, or improve it for your own daily loan tracking automation!

---


---

### 🚀 Why This Matters

This small project shows how **serverless + event-driven design + external data APIs** can automate a real-life financial task — while being easy to maintain, cheap to run, and ready to scale or extend.  

---

**💙 Built to motivate myself (and anyone!) to pay off student loans wisely — one day at a time.**
Let’s connect on [LinkedIn](https://www.linkedin.com/in/ghaayathri-devi-k-21089b231/) if you liked this! 🚀✨

