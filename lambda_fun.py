import boto3
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import requests
from bs4 import BeautifulSoup

def get_sbi_ebr():
    url = "https://sbi.co.in/web/interest-rates/interest-rates"
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")

    # Find all tables
    tables = soup.find_all("table")

    for table in tables:
        rows = table.find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            if len(cols) == 3:
                # Try to parse the third column as EBR
                ebr_text = cols[2].get_text().strip().replace("%","")
                try:
                    ebr = float(ebr_text)
                    return ebr
                except:
                    continue

    raise Exception("Could not find EBR in any table!")

# print("SBI EBR:", get_sbi_ebr())


def lambda_handler(event=None, context=None):
    # Google Sheets setup
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets.readonly",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_file("service_account.json", scopes=scopes)
    client = gspread.authorize(creds)
    sheet = client.open("EducationLoanDisbursement").sheet1

    records = sheet.get_all_records()
    total_disbursed = sum([row['Disbursed Amount'] for row in records])

    # Use the first disbursement date
    disbursed_date = records[0]['Date']
    disbursed_date_obj = datetime.strptime(disbursed_date, "%Y/%m/%d").date()
    today_date_obj = datetime.today().date()

    days_elapsed = (today_date_obj - disbursed_date_obj).days + 1

    # external_benchmark_rate = 8.15 # %
    # credit_risk_premium = 1 # %
    annual_rate = get_sbi_ebr() # %

    daily_interest = total_disbursed * (annual_rate / 100) / 365
    total_interest = daily_interest * days_elapsed

    usd_daily_save = 3
    inr_daily_save = usd_daily_save * 85  # Approx conversion
    saving_days = int(2.5 * 365)  # 2.5 years ≈ 912 days
    usd_future_save = usd_daily_save * saving_days
    inr_future_save = inr_daily_save * saving_days

    message = f"""
📅 Disbursement Date: {disbursed_date}
📅 Alert Date: {today_date_obj}

💰 Total disbursed: ₹{total_disbursed:,.2f}
🔹 Today's interest: ₹{daily_interest:,.2f}
🔹 Total interest so far: ₹{total_interest:,.2f}

💡 Daily saving goal: ${usd_daily_save:.2f} (~₹{inr_daily_save:.0f})
💡 If you save this daily for 2.5 years, you’ll have ~${usd_future_save:.2f} (~₹{inr_future_save:,.0f}) ready to repay your loan faster!

🌟 Keep saving a little every single day — you WILL get placed in a MAANG company soon,
repay your loan proudly, and build the life you dream of. 🚀✨

Stay strong — your future self will thank you! 💪💙
"""

    # SNS
    sns_client = boto3.client('sns')
    topic_arn = 'arn:aws:sns:us-east-2:489335433975:daily-education-loan-alert'
    sns_client.publish(
        TopicArn=topic_arn,
        Subject='🌟 Daily Education Loan Alert',
        Message=message
    )

    # Your bot token
    bot_token = '8457299044:AAEskcvCzDmSKlpnycmcn9uMd5shC16oGIM'
    # Your chat ID
    chat_id = '1881510446'

    # Your message (reuse the same `message` you send via SNS)
    telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    telegram_payload = {
        "chat_id": chat_id,
        "text": message
    }

    response = requests.post(telegram_url, data=telegram_payload)
    print("Telegram response:", response.text)


    return {
        'statusCode': 200,
        'body': 'SNS notification sent!'
    }
