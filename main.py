from flask import Flask, render_template_string, request
import requests
import os
import time

app = Flask(__name__)

API_KEY = os.getenv("API_KEY")
PRODUCT_ID = 177  # আপনার Hotmail product ID

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Hotmail Buyer</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body style="font-family:Arial;text-align:center;padding:50px;">

<h2>Hotmail Buyer</h2>

<form method="POST">
    <button type="submit" style="padding:12px 20px;">
        Buy Hotmail
    </button>
</form>

{% if email %}
<div style="margin-top:30px;">
    <input
        type="text"
        id="hotmail"
        value="{{ email }}"
        readonly
        style="width:350px;padding:10px;"
    >

    <button onclick="copyEmail()">
        Copy
    </button>
</div>
{% endif %}

{% if error %}
<p style="color:red;">
    {{ error }}
</p>
{% endif %}

<script>
function copyEmail() {
    const text = document.getElementById("hotmail").value;
    navigator.clipboard.writeText(text);
    alert("Copied!");
}
</script>

</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def home():

    email = None
    error = None

    if request.method == "POST": 

        try:

            # BUY ORDER
            buy_response = requests.post(
                "https://bulkmail.shop/api/v2/orders",
                headers={
                    "X-API-Key": API_KEY,
                    "Content-Type": "application/json"
                },
                json={
                    "product_id": PRODUCT_ID,
                    "quantity": 1
                },
                timeout=30
            )

            buy_data = buy_response.json()

            if not buy_data.get("success"):
                error = str(buy_data)

            else:

                order_id = buy_data["data"]["id"]

                # wait for stock delivery
                time.sleep(1)

                # GET ORDER DETAILS
                details_response = requests.get(
                    f"https://bulkmail.shop/api/v2/orders/{order_id}",
                    headers={
                        "X-API-Key": API_KEY
                    },
                    timeout=30
                )

                details_data = details_response.json()

                print(details_data)

                stock_items = details_data["data"].get(
                    "stock_items",
                    []
                )

                if stock_items:

                    stock = stock_items[0]

                    # email|pass|token -> only email
                    email = stock.split("|")[0]

                else:

                    error = "No stock received"

        except Exception as e:

            error = str(e)

    return render_template_string(
        HTML,
        email=email,
        error=error
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
