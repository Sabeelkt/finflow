from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_mysqldb import MySQL
import os
from dotenv import load_dotenv

load_dotenv()  # load DB credentials from .env

app = Flask(__name__)
CORS(app)

# MySQL config
app.config['MYSQL_HOST'] = os.getenv("MYSQL_HOST")
app.config['MYSQL_USER'] = os.getenv("MYSQL_USER")
app.config['MYSQL_PASSWORD'] = os.getenv("MYSQL_PASSWORD")
app.config['MYSQL_DB'] = os.getenv("MYSQL_DB")


mysql = MySQL(app)

# Test connection route
@app.route("/test-db")
def test_db():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT 1")
        cur.close()
        return jsonify({"status": "Database connected successfully"})
    except Exception as e:
        return jsonify({"status": "Error", "message": str(e)})


@app.route("/add-expense", methods=["POST"])
def add_expense():
    data = request.get_json()

    amount = data.get("amount")
    category = data.get("category")
    transaction_date = data.get("date")
    transaction_type = data.get("type")  # Expense / Income
    payment_mode = data.get("paymentMode")

    # Basic validation
    if not all([amount, category, transaction_date, transaction_type, payment_mode]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO transactions
            (amount, category, transaction_date, transaction_type, payment_mode)
            VALUES (%s, %s, %s, %s, %s)
        """, (amount, category, transaction_date, transaction_type, payment_mode))

        mysql.connection.commit()
        cur.close()

        return jsonify({"message": "Expense added successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/delete-expense/<string:transaction_id>", methods=["DELETE"])
def delete_expense(transaction_id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM transactions WHERE transaction_id = %s", (transaction_id,))
        mysql.connection.commit()
        cur.close()
        return jsonify({"message": "Transaction deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/update-expense/<string:transaction_id>", methods=["PUT"])
def update_expense(transaction_id):
    data = request.get_json()
    
    amount = data.get("amount")
    category = data.get("category")
    transaction_date = data.get("date")
    transaction_type = data.get("type")
    payment_mode = data.get("paymentMode")

    if not all([amount, category, transaction_date, transaction_type, payment_mode]):
         return jsonify({"error": "Missing required fields"}), 400

    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE transactions
            SET amount = %s, category = %s, transaction_date = %s, transaction_type = %s, payment_mode = %s
            WHERE transaction_id = %s
        """, (amount, category, transaction_date, transaction_type, payment_mode, transaction_id))
        
        mysql.connection.commit()
        cur.close()
        return jsonify({"message": "Transaction updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/transactions", methods=["GET"])
def get_transactions():
    try:
        cur = mysql.connection.cursor()
        # Order by date desc
        cur.execute("SELECT transaction_id, transaction_date, transaction_type, category, amount, payment_mode FROM transactions ORDER BY transaction_date DESC")
        rows = cur.fetchall()
        cur.close()

        transactions = []
        for row in rows:
            transactions.append({
                "id": str(row[0]),
                "date": str(row[1]),
                "type": row[2],  # DB stores 'Income'/'Expense' (Capitalized)
                "category": row[3],
                "amount": float(row[4]),
                "paymentMode": row[5]
            })
        
        return jsonify(transactions)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
