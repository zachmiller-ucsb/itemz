#!/usr/bin/env python3.12

import os
import stripe
from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from urllib.parse import urlparse

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("FLASK_SQLALCHEMY_DATABASE_URI")
db = SQLAlchemy(app)

stripe_keys = {
    "secret_key": os.environ.get("STRIPE_SECRET_KEY"),
    "publishable_key": os.environ.get("STRIPE_PUBLISHABLE_KEY"),
    "endpoint_secret": os.environ.get("STRIPE_ENDPOINT_SECRET")
}

stripe.api_key = stripe_keys.get("secret_key")

from models import Item

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/db_test", methods=["GET"])
def db_test():
    return render_template("db_test.html")

@app.route("/create_item", methods=["POST"])
def create_item():
    name = request.form.get("name")
    description = request.form.get("description")
    price = request.form.get("price")

    item = Item(name, description, price)
    db.session.add(item)
    db.session.commit()

    return redirect(url_for("db_test"))

@app.route("/success", methods=["GET"])
def success():
    return render_template("success.html")

@app.route("/cancel", methods=["GET"])
def cancelled():
    return render_template("cancel.html")

@app.route("/config", methods=["GET"])
def get_publishable_key():
    stripe_config = {"publicKey": stripe_keys["publishable_key"]}
    return jsonify(stripe_config)

@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    domain_url = urlparse(request.host_url)

    try:
        # Create new Checkout Session for the order
        checkout_session = stripe.checkout.Session.create(
            success_url=domain_url.geturl() + "success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=domain_url.geturl() + "cancel",
            payment_method_types=["card"],
            mode="payment",
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": "Cool Lamp",
                        },
                        "unit_amount": 10000,
                    },
                    "quantity": 1,
                }
            ]
        )
        return jsonify({"sessionId": checkout_session["id"]})
    except Exception as e:
        return jsonify(error=str(e)), 403
    
@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, stripe_keys["endpoint_secret"]
        )

    except ValueError as e:
        # Invalid payload
        return "Invalid payload", 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return "Invalid signature", 400

    # Handle the checkout.session.completed event
    if event["type"] == "checkout.session.completed":
        print("Payment was successful.")
        # TODO: run some custom code here

    return "Success", 200

if __name__ == "__main__":
    app.run(port=3000, debug=True)
