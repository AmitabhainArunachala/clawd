def log_transaction(transaction):
    # Log transaction anomalies for auditing purposes
    with open("transaction_log.txt", "a") as log_file:
        log_file.write(f"Transaction ID: {transaction[id]} - Status: {transaction[status]}
")

