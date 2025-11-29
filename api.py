from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
import pandas as pd
from joblib import load

# NEW:
import mysql.connector
from datetime import datetime

# ---------- Load model + threshold ----------
bundle = load("fraud_rf_pipeline.joblib")
model = bundle["model"]
threshold = bundle["threshold"]

app = FastAPI(title="Fraud Detection API", version="1.0.0")


# ---------- MySQL logging helpers ----------

def get_db_connection():
    """Create and return a new MySQL connection."""
    return mysql.connector.connect(
        host="host name ",
        user="root",                 # change if your user is different
        password="your_password",    # <-- PUT YOUR REAL PASSWORD HERE
        database="banking_fraud_detection"
    )

def init_db():
    """Create fraud_predictions table if it does not exist."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS fraud_predictions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            created_at DATETIME,
            amount DOUBLE,
            balance DOUBLE,
            hour INT,
            day_of_week INT,
            is_weekend TINYINT,
            is_international_flag TINYINT,
            age INT,
            txns_per_account INT,
            avg_amount_account DOUBLE,
            txn_type VARCHAR(20),
            channel VARCHAR(20),
            account_type VARCHAR(20),
            gender VARCHAR(5),
            city VARCHAR(50),
            state VARCHAR(50),
            fraud_probability DOUBLE,
            fraud_prediction TINYINT,
            reason_text VARCHAR(255)
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

def log_prediction_to_db(
    amount, balance, hour, day_of_week,
    is_weekend, is_international_flag, age,
    txns_per_account, avg_amount_account,
    txn_type, channel, account_type, gender,
    city, state,
    fraud_probability, fraud_prediction,
    reason_text
):
    """Insert one prediction into fraud_predictions table."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO fraud_predictions (
            created_at,
            amount, balance, hour, day_of_week,
            is_weekend, is_international_flag, age,
            txns_per_account, avg_amount_account,
            txn_type, channel, account_type, gender,
            city, state,
            fraud_probability, fraud_prediction, reason_text
        )
        VALUES (
            %s,
            %s, %s, %s, %s,
            %s, %s, %s,
            %s, %s,
            %s, %s, %s, %s,
            %s, %s,
            %s, %s, %s
        )
    """, (
        datetime.now(),
        amount, balance, hour, day_of_week,
        is_weekend, is_international_flag, age,
        txns_per_account, avg_amount_account,
        txn_type, channel, account_type, gender,
        city, state,
        fraud_probability, fraud_prediction,
        reason_text[:250]  # limit text length for safety
    ))
    conn.commit()
    cur.close()
    conn.close()

# call once when app starts
init_db()


# ---------- JSON API (what you already had) ----------
@app.get("/")
def home():
    return {"message": "Fraud Detection API is running!"}


@app.post("/predict")
def predict(data: dict):
    """JSON endpoint – keep for programmatic use"""
    X_new = pd.DataFrame([data])
    fraud_probs = model.predict_proba(X_new)[:, 1]
    decision = int(fraud_probs[0] >= threshold)

    return {
        "fraud_probability": float(fraud_probs[0]),
        "fraud_prediction": decision
    }

    # Save this prediction into MySQL
    try:
        log_prediction_to_db(
            amount=amount,
            balance=balance,
            hour=hour,
            day_of_week=day_of_week,
            is_weekend=is_weekend,
            is_international_flag=is_international_flag,
            age=age,
            txns_per_account=txns_per_account,
            avg_amount_account=avg_amount_account,
            txn_type=txn_type,
            channel=channel,
            account_type=account_type,
            gender=gender,
            city=city,
            state=state,
            fraud_probability=fraud_prob,
            fraud_prediction=decision,
            reason_text=reason_text
        )
    except Exception as e:
        # Optional: print error in server logs but don't break UI
        print("Error logging prediction to DB:", e)

# ---------- Simple HTML Frontend ----------
@app.get("/ui", response_class=HTMLResponse)
def ui_form():
    """Render HTML form for manual testing with nicer UI + tooltips"""
    html = """
    <html>
    <head>
        <title>SecureTrust Bank – Banking Fraud Detection</title>
        <style>
            * { box-sizing: border-box; }
            body {
                margin: 0;
                padding: 0;
                font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
                background: radial-gradient(circle at top left, #1f2937, #020617);
                color: #0f172a;
            }
            .page {
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 24px;
            }
            .card {
                width: 100%;
                max-width: 720px;
                background: #ffffff;
                border-radius: 16px;
                box-shadow: 0 20px 40px rgba(15,23,42,0.35);
                padding: 24px 28px 28px;
                position: relative;
                overflow: hidden;
            }
            .card::before {
                content: "";
                position: absolute;
                inset: -80px auto auto -80px;
                width: 180px;
                height: 180px;
                background: radial-gradient(circle, #38bdf8, transparent 60%);
                opacity: 0.3;
            }
            .card::after {
                content: "";
                position: absolute;
                inset: auto -60px -60px auto;
                width: 160px;
                height: 160px;
                background: radial-gradient(circle, #22c55e, transparent 60%);
                opacity: 0.25;
            }
            .card-content {
                position: relative;
                z-index: 1;
            }
            .header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 10px;
            }
            .logo-wrap {
                display: flex;
                align-items: center;
                gap: 10px;
            }
            .logo-circle {
                width: 38px;
                height: 38px;
                border-radius: 999px;
                background: linear-gradient(135deg, #0ea5e9, #22c55e);
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: 700;
                font-size: 18px;
                box-shadow: 0 6px 16px rgba(34,197,94,0.35);
            }
            .title {
                font-size: 20px;
                font-weight: 700;
                color: #0f172a;
            }
            .subtitle {
                font-size: 12px;
                color: #64748b;
            }
            .badge {
                font-size: 11px;
                padding: 4px 10px;
                border-radius: 999px;
                background: #ecfdf5;
                color: #16a34a;
                border: 1px solid #bbf7d0;
                font-weight: 600;
            }
            .demo-buttons {
                display: flex;
                gap: 10px;
                margin-bottom: 10px;
                flex-wrap: wrap;
            }
            .btn {
                border-radius: 999px;
                border: none;
                padding: 8px 14px;
                font-size: 13px;
                font-weight: 600;
                cursor: pointer;
                display: inline-flex;
                align-items: center;
                gap: 6px;
                box-shadow: 0 4px 10px rgba(15,23,42,0.15);
            }
            .btn-safe {
                background: linear-gradient(135deg, #22c55e, #16a34a);
                color: white;
            }
            .btn-fraud {
                background: linear-gradient(135deg, #ef4444, #b91c1c);
                color: white;
            }
            .btn span.icon {
                font-size: 16px;
            }
            form {
                margin-top: 4px;
            }
            .grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
                gap: 12px 16px;
            }
            label {
                display: block;
                font-size: 12px;
                font-weight: 600;
                color: #0f172a;
                margin-bottom: 3px;
            }
            input, select {
                width: 100%;
                padding: 7px 9px;
                border-radius: 8px;
                border: 1px solid #cbd5f5;
                font-size: 13px;
                outline: none;
                transition: border-color 0.15s, box-shadow 0.15s, background 0.15s;
                background: #f8fafc;
            }
            input:focus, select:focus {
                border-color: #0ea5e9;
                box-shadow: 0 0 0 1px rgba(14,165,233,0.3);
                background: #ffffff;
            }
            .footer-actions {
                margin-top: 16px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                gap: 10px;
                flex-wrap: wrap;
            }
            .primary-submit {
                background: linear-gradient(135deg, #0ea5e9, #2563eb);
                color: white;
                border-radius: 999px;
                border: none;
                padding: 9px 18px;
                font-size: 14px;
                font-weight: 600;
                cursor: pointer;
                box-shadow: 0 6px 16px rgba(37,99,235,0.45);
                display: inline-flex;
                align-items: center;
                gap: 6px;
            }
            .primary-submit:hover {
                filter: brightness(1.05);
            }
            .hint {
                font-size: 11px;
                color: #6b7280;
            }
            @media (max-width: 640px) {
                .card {
                    padding: 18px 16px 20px;
                }
            }
        </style>
    </head>
    <body>
        <div class="page">
            <div class="card">
                <div class="card-content">
                    <div class="header">
                        <div class="logo-wrap">
                            <div class="logo-circle">ST</div>
                            <div>
                                <div class="title">SecureTrust Bank</div>
                                <!-- subtitle removed as requested -->
                                <div class="subtitle">Banking Fraud Detection</div>
                            </div>
                        </div>
                        <div class="badge">ML Model · v1.0</div>
                    </div>

                    <!-- Tooltip / helper box -->
                    <div id="helpBox"
                        style="
                            background:#1f2937;
                            border:1px solid #374151;
                            padding:8px 14px;
                            border-radius:8px;
                            font-size:13px;
                            color:white;
                            margin-bottom:12px;
                            opacity:0;
                            transition:opacity 0.25s;
                        ">
                    </div>

                    <div class="demo-buttons">
                        <button type="button" class="btn btn-safe" onclick="runSafeDemo()">
                            <span class="icon">✅</span> Demo Safe Transaction
                        </button>
                        <button type="button" class="btn btn-fraud" onclick="runFraudDemo()">
                            <span class="icon">⚠️</span> Demo Fraud Transaction
                        </button>
                    </div>

                    <form id="fraudForm" action="/ui/predict" method="post">
                        <div class="grid">
                            <div>
                                <label>Amount (₹)</label>
                                <input type="number" step="0.01" name="amount" required
                                       onfocus="showHelp('amount')" onblur="hideHelp()">
                            </div>

                            <div>
                                <label>Balance (₹)</label>
                                <input type="number" step="0.01" name="balance" required
                                       onfocus="showHelp('balance')" onblur="hideHelp()">
                            </div>

                            <div>
                                <label>Hour (0–23)</label>
                                <input type="number" name="hour" min="0" max="23" required
                                       onfocus="showHelp('hour')" onblur="hideHelp()">
                            </div>

                            <div>
                                <label>Day of Week</label>
                                <select name="day_of_week"
                                        onfocus="showHelp('day_of_week')" onblur="hideHelp()">
                                    <option value="0">0 – Monday</option>
                                    <option value="1">1 – Tuesday</option>
                                    <option value="2">2 – Wednesday</option>
                                    <option value="3">3 – Thursday</option>
                                    <option value="4">4 – Friday</option>
                                    <option value="5">5 – Saturday</option>
                                    <option value="6">6 – Sunday</option>
                                </select>
                            </div>

                            <div>
                                <label>Is Weekend?</label>
                                <select name="is_weekend"
                                        onfocus="showHelp('is_weekend')" onblur="hideHelp()">
                                    <option value="0">0 – No</option>
                                    <option value="1">1 – Yes</option>
                                </select>
                            </div>

                            <div>
                                <label>Is International?</label>
                                <select name="is_international_flag"
                                        onfocus="showHelp('is_international_flag')" onblur="hideHelp()">
                                    <option value="0">0 – No</option>
                                    <option value="1">1 – Yes</option>
                                </select>
                            </div>

                            <div>
                                <label>Transactions per Account</label>
                                <input type="number" name="txns_per_account" min="0" required
                                       onfocus="showHelp('txns_per_account')" onblur="hideHelp()">
                            </div>

                            <div>
                                <label>Transaction Type</label>
                                <select name="txn_type"
                                        onfocus="showHelp('txn_type')" onblur="hideHelp()">
                                    <option>ATM</option>
                                    <option>POS</option>
                                    <option>Online</option>
                                    <option>Transfer</option>
                                </select>
                            </div>

                            <div>
                                <label>Channel</label>
                                <select name="channel"
                                        onfocus="showHelp('channel')" onblur="hideHelp()">
                                    <option>Branch</option>
                                    <option>ATM</option>
                                    <option>Online</option>
                                    <option>Mobile</option>
                                </select>
                            </div>

                            <div>
                                <label>Account Type</label>
                                <select name="account_type"
                                        onfocus="showHelp('account_type')" onblur="hideHelp()">
                                    <option>savings</option>
                                    <option>current</option>
                                    <option>credit_card</option>
                                </select>
                            </div>

                            <div>
                                <label>City</label>
                                <input type="text" name="city" value="Hyderabad"
                                       onfocus="showHelp('city')" onblur="hideHelp()">
                            </div>

                            <div>
                                <label>State</label>
                                <input type="text" name="state" value="Telangana"
                                       onfocus="showHelp('state')" onblur="hideHelp()">
                            </div>

                            <div>
                                <label>Country</label>
                                <input type="text" name="country" value="India"
                                       onfocus="showHelp('country')" onblur="hideHelp()">
                            </div>
                        </div>

                        <!-- hidden defaults for model-only fields: age, avg_amount_account, gender -->
                        <input type="hidden" name="age" value="35">
                        <input type="hidden" name="avg_amount_account" value="2000">
                        <input type="hidden" name="gender" value="M">

                        <div class="footer-actions">
                            <button type="submit" class="primary-submit">
                                <span>Predict Fraud</span> <span class="icon">➜</span>
                            </button>
                            <div class="hint">
                                Tip: hover / focus on any field to see what it means.  
                                Use the demo buttons above for instant examples.
                            </div>
                        </div>
                    </form>
                </div>
            </div>
        </div>

        <script>
            // Help-text dictionary
            const helpText = {
                amount: "Total transaction amount in rupees.",
                balance: "Customer's account balance before the transaction.",
                hour: "Time of the transaction (0 = midnight, 23 = 11PM).",
                day_of_week: "Day of the transaction (0=Mon … 6=Sun).",
                is_weekend: "Whether the transaction happened on a weekend (Sat/Sun).",
                is_international_flag: "Indicates if the transaction is international.",
                txns_per_account: "Total number of previous transactions for this account.",
                txn_type: "Type of transaction: ATM, POS, Online, Transfer, etc.",
                channel: "Channel used for the transaction (Branch/ATM/Online/Mobile).",
                account_type: "Account category: savings, current, or credit card.",
                city: "City where the customer lives or account is registered.",
                state: "State where the customer lives or account is registered.",
                country: "Country of the customer (not used directly by the model, for display only)."
            };

            function showHelp(name) {
                const helpBox = document.getElementById("helpBox");
                helpBox.innerText = helpText[name] || "";
                helpBox.style.opacity = "1";
            }

            function hideHelp() {
                document.getElementById("helpBox").style.opacity = "0";
            }

            function setValue(name, value) {
                const el = document.querySelector('[name="' + name + '"]');
                if (el) el.value = value;
            }

            function runSafeDemo() {
                setValue("amount", 1500);
                setValue("balance", 25000);
                setValue("hour", 14);
                setValue("day_of_week", 2);
                setValue("is_weekend", 0);
                setValue("is_international_flag", 0);
                setValue("txns_per_account", 120);
                setValue("txn_type", "ATM");
                setValue("channel", "Branch");
                setValue("account_type", "savings");
                setValue("city", "Hyderabad");
                setValue("state", "Telangana");
                setValue("country", "India");
                // hidden model fields:
                setValue("age", 35);
                setValue("avg_amount_account", 1800);
                setValue("gender", "M");

                document.getElementById("fraudForm").submit();
            }

            function runFraudDemo() {
                setValue("amount", 95000);
                setValue("balance", 12000);
                setValue("hour", 2);
                setValue("day_of_week", 6);
                setValue("is_weekend", 1);
                setValue("is_international_flag", 1);
                setValue("txns_per_account", 8);
                setValue("txn_type", "Online");
                setValue("channel", "Mobile");
                setValue("account_type", "savings");
                setValue("city", "Mumbai");
                setValue("state", "Maharashtra");
                setValue("country", "India");
                // hidden model fields:
                setValue("age", 22);
                setValue("avg_amount_account", 1500);
                setValue("gender", "M");

                document.getElementById("fraudForm").submit();
            }
        </script>
    </body>
    </html>
    """
    return html




@app.post("/ui/predict", response_class=HTMLResponse)
def ui_predict(
    amount: float = Form(...),
    balance: float = Form(...),
    hour: int = Form(...),
    day_of_week: int = Form(...),
    is_weekend: int = Form(...),
    is_international_flag: int = Form(...),
    age: int = Form(...),
    txns_per_account: int = Form(...),
    avg_amount_account: float = Form(...),
    txn_type: str = Form(...),
    channel: str = Form(...),
    account_type: str = Form(...),
    gender: str = Form(...),
    city: str = Form(...),
    state: str = Form(...)
):
    # Build DataFrame
    data = {
        "amount": [amount],
        "balance": [balance],
        "hour": [hour],
        "day_of_week": [day_of_week],
        "is_weekend": [is_weekend],
        "is_international_flag": [is_international_flag],
        "age": [age],
        "txns_per_account": [txns_per_account],
        "avg_amount_account": [avg_amount_account],
        "txn_type": [txn_type],
        "channel": [channel],
        "account_type": [account_type],
        "gender": [gender],
        "city": [city],
        "state": [state],
    }

    X_new = pd.DataFrame(data)
    fraud_prob = float(model.predict_proba(X_new)[:, 1][0])
    decision = int(fraud_prob >= threshold)

    is_fraud = (decision == 1)
    label = "FRAUD" if is_fraud else "NOT FRAUD"
    badge_text = "High Risk" if is_fraud else "Low Risk"
    card_class = "fraud" if is_fraud else "safe"

    # reason generator
    reasons = []
    if amount > max(balance * 0.6, 50000):
        reasons.append("high transaction amount compared to balance")
    if is_international_flag == 1:
        reasons.append("international transaction")
    if is_weekend == 1 or hour < 7 or hour > 22:
        reasons.append("unusual transaction time")
    if txns_per_account < 10:
        reasons.append("low account activity")

    if is_fraud:
        reason_text = (
            "This transaction is flagged as FRAUD because of "
            + ", ".join(reasons)
            + "."
            if reasons
            else "This transaction pattern looks unusual compared to typical customer behaviour."
        )
    else:
        safe_reasons = []
        if amount <= max(balance * 0.6, 50000):
            safe_reasons.append("amount is within a normal range")
        if is_international_flag == 0:
            safe_reasons.append("transaction is domestic")
        if not (is_weekend == 1 or hour < 7 or hour > 22):
            safe_reasons.append("time of transaction is within normal hours")
        if txns_per_account >= 10:
            safe_reasons.append("account has sufficient past activity")

        reason_text = (
            "This transaction is considered SAFE because "
            + ", ".join(safe_reasons)
            + "."
            if safe_reasons
            else "This transaction is consistent with typical customer behaviour."
        )

    # Save to MySQL
    try:
        log_prediction_to_db(
            amount, balance, hour, day_of_week,
            is_weekend, is_international_flag, age,
            txns_per_account, avg_amount_account,
            txn_type, channel, account_type, gender,
            city, state,
            fraud_prob, decision, reason_text
        )
    except Exception as e:
        print("DB Logging Error:", e)

    # ----------- HTML response START -----------
    html = f"""
    <html>
    <head>
        <title>Banking Fraud Detection Result</title>
        <style>
            body {{
                margin: 0;
                padding: 0;
                font-family: system-ui, sans-serif;
                background: radial-gradient(circle at top left, #0f172a, #020617);
                color: #e5e7eb;
            }}
            .page {{
                padding: 30px;
                display: flex;
                justify-content: center;
            }}
            .card {{
                width: 720px;
                background: #020617;
                border-radius: 18px;
                padding: 28px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.6);
            }}
            .bank {{
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            .logo {{
                display: flex;
                align-items: center;
                gap: 12px;
            }}
            .circle {{
                width: 38px;
                height: 38px;
                border-radius: 100px;
                background: linear-gradient(135deg, #0ea5e9, #22c55e);
                color: white;
                font-weight: 700;
                display: flex;
                justify-content: center;
                align-items: center;
            }}
            .badge {{
                padding: 5px 12px;
                border-radius: 12px;
                border: 1px solid #4ade80;
                background: #052e16;
                color: #bbf7d0;
                font-size: 12px;
            }}
            .title {{
                font-size: 24px;
                font-weight: 700;
                margin-top: 20px;
            }}
            .result-box {{
                margin-top: 20px;
                border-radius: 12px;
                padding: 18px;
                background: {"#450a0a" if is_fraud else "#022c22"};
                border: 1px solid {"#f87171" if is_fraud else "#34d399"};
            }}
            a {{
                color: #38bdf8;
                text-decoration: none;
                font-size: 14px;
            }}
        </style>
    </head>

    <body>
        <div class="page">
            <div class="card">

                <div class="bank">
                    <div class="logo">
                        <div class="circle">ST</div>
                        <div>
                            <b>SecureTrust Bank</b><br>
                            <span style="font-size:11px;color:#9ca3af;">Transaction Fraud Engine</span>
                        </div>
                    </div>
                    <div class="badge">{badge_text}</div>
                </div>

                <div class="title">Banking Fraud Detection Result</div>

                <div class="result-box">
                    <h3>PREDICTION: {label}</h3>
                    <p><b>Fraud probability:</b> {fraud_prob:.4f}</p>
                    <p><b>Reason:</b> {reason_text}</p>
                </div>

                <div style="margin-top:20px;">
                    <a href="/ui">⟵ Test another transaction</a>
                </div>

            </div>
        </div>
    </body>
    </html>
    """
    # ----------- HTML response END -----------

    return html
