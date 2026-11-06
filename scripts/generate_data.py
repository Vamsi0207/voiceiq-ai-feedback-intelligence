"""Generate synthetic English data; evaluation uses independent base phrasing."""

from pathlib import Path
import csv
import random
from datetime import datetime, timedelta, timezone

ROOT = Path(__file__).resolve().parents[1]
CATEGORIES = [
    "UPI & Payments",
    "Credit Cards",
    "Account Access",
    "Mobile Banking",
    "Loans",
    "Customer Support",
    "Fraud & Security",
    "Other",
]
TRAIN = [
    [
        "UPI payment failed but money deducted",
        "bank transfer pending and amount debited",
        "merchant payment unsuccessful balance reduced",
        "payment refund not received",
        "UPI transfer stuck processing",
        "payment completed instantly",
    ],
    [
        "credit card charged twice",
        "card bill shows duplicate charge",
        "credit card dispute still unresolved",
        "card statement fee is incorrect",
        "card limit increase request",
        "credit card cashback arrived",
    ],
    [
        "cannot login to my account",
        "password reset link does not work",
        "OTP for login never arrives",
        "account locked after password attempt",
        "unable to access my account",
        "password reset worked quickly",
    ],
    [
        "mobile banking app keeps crashing",
        "app freezes on dashboard",
        "banking application is very slow",
        "mobile app update broke screen",
        "app does not load on phone",
        "mobile banking interface is smooth",
    ],
    [
        "loan EMI deducted incorrectly",
        "loan application pending approval",
        "loan interest rate changed unexpectedly",
        "loan repayment schedule missing",
        "home loan documents not updated",
        "loan approval was quick",
    ],
    [
        "customer support has not replied for four days",
        "support agent ended chat without help",
        "helpline call waiting forever",
        "service ticket closed without resolution",
        "customer care callback never happened",
        "support team resolved my query",
    ],
    [
        "unauthorized transaction on my account",
        "suspected fraud money stolen",
        "someone compromised my banking account",
        "phishing message asked for OTP",
        "suspicious debit I did not approve",
        "security team blocked the scam",
    ],
    [
        "please add a branch in my town",
        "ATM receipt paper is missing",
        "bank office timings need updating",
        "feedback about parking at branch",
        "please offer statements in more languages",
        "branch staff gave clear directions",
    ],
]
EVAL = [
    [
        "The recipient got nothing although my wallet was debited after scanning a QR code",
        "A transfer through UPI vanished before reaching the shopkeeper",
        "Reversing the failed remittance has taken a week",
        "Paying the vendor through UPI was effortless",
    ],
    [
        "Two identical purchases appeared on my credit statement",
        "The revolving credit facility added an unexplained annual fee",
        "I need to contest an entry on my Visa bill",
        "My card rewards were credited exactly as promised",
    ],
    [
        "Signing in asks for a verification code that never comes",
        "The reset password email leads to an expired page",
        "I have been shut out of the account despite valid credentials",
        "Regaining access to my profile was straightforward",
    ],
    [
        "Every launch of the banking application ends with a blank display",
        "The Android banking screen becomes unresponsive after opening",
        "Since the release my phone banking interface stops responding",
        "The latest mobile interface runs beautifully",
    ],
    [
        "My mortgage installment exceeded the agreed repayment amount",
        "The borrowing application has sat with underwriting for weeks",
        "Interest on the personal loan differs from the signed contract",
        "The lender sanctioned my mortgage ahead of schedule",
    ],
    [
        "Nobody at the contact centre answers my follow up messages",
        "An adviser marked my case solved before investigating",
        "I waited on the customer helpline and was disconnected",
        "The helpdesk adviser explained everything patiently",
    ],
    [
        "A stranger used my credentials to withdraw my savings",
        "I spotted a debit from an unknown location and fear identity theft",
        "A caller impersonating the bank persuaded me to share a code",
        "The scam alert prevented an unauthorized withdrawal",
    ],
    [
        "The cash machine outside the branch has no printed slips",
        "Wheelchair access at the local office could be improved",
        "I would like a branch closer to our village",
        "The branch receptionist made my visit easy",
    ],
]
TRAIN_SENTIMENT = {
    "Negative": [
        "This is frustrating and terrible service.",
        "I am unhappy and disappointed.",
        "Really bad experience, please fix this.",
    ],
    "Neutral": [
        "Please provide an update.",
        "I am asking for information.",
        "Could you check the current status?",
    ],
    "Positive": [
        "Thank you, excellent service!",
        "I am happy with the great experience.",
        "Very helpful and easy, I appreciate it.",
    ],
}
EVAL_SENTIMENT = {
    "Negative": [
        "This has been awful; I regret trusting this service.",
        "Such a miserable experience, I am furious.",
    ],
    "Neutral": [
        "I would like to know what happens next.",
        "This is a request for clarification.",
    ],
    "Positive": [
        "Delighted with how well everything went.",
        "Wonderful assistance; you made my day.",
    ],
}


def write(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def generate():
    rng = random.Random(42)
    rows = []
    start = datetime(2026, 7, 1, tzinfo=timezone.utc)
    for i in range(2400):
        c = rng.choices(range(8), weights=[25, 16, 14, 14, 9, 12, 7, 3])[0]
        s = rng.choices(list(TRAIN_SENTIMENT), weights=[65, 22, 13])[0]
        text = (
            rng.choice(TRAIN[c][:5] if s != "Positive" else TRAIN[c][5:])
            + ". "
            + rng.choice(TRAIN_SENTIMENT[s])
        )
        text += f" This concerns my {rng.choice(['personal', 'family', 'salary', 'everyday'])} banking, reference SYN-{i:04d}."
        if i % 17 == 0:
            text = text.replace("please", "pls").replace("received", "recieved")
        rows.append(
            dict(
                complaint_id=f"VIQ-{i + 1:05d}",
                customer_id=f"SYN-{rng.randrange(10000):05d}",
                complaint_text=text,
                created_at=(
                    start + timedelta(days=rng.randrange(120), hours=rng.randrange(24))
                ).isoformat(),
                source=rng.choice(["App review", "Support ticket", "Survey", "Email"]),
                category=CATEGORIES[c],
                sentiment=s,
            )
        )
    write(ROOT / "data/sample_complaints.csv", rows)
    evaluation = []
    for c, phrases in enumerate(EVAL):
        for j, phrase in enumerate(phrases):
            sentiments = ["Positive"] if j == 3 else ["Negative", "Neutral"]
            for s in sentiments:
                for k, clause in enumerate(EVAL_SENTIMENT[s]):
                    evaluation.append(
                        dict(
                            complaint_id=f"EVAL-{c}-{j}-{s}-{k}",
                            complaint_text=phrase + ". " + clause,
                            category=CATEGORIES[c],
                            sentiment=s,
                        )
                    )
    write(ROOT / "data/evaluation/heldout.csv", evaluation)
    print(
        f"Generated {len(rows)} training/demo records and {len(evaluation)} independent-phrase evaluation records"
    )


if __name__ == "__main__":
    generate()
