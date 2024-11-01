import sys
import pika
import json
import uuid

def main():
    username = input("Enter your username: ")

    # Generate a unique user ID
    user_id = str(uuid.uuid4())

    middleware_endpoint = 'localhost'

    while True:
        side = input("Do you want to BUY or SELL? ").strip().upper()

        if side not in ['BUY', 'SELL']:
            print("Invalid side. Please enter either 'BUY' or 'SELL'.")
            continue

        price = float(input("Enter the price for your order: "))
        quantity = 100

        order = {
            "user_id": user_id,  # Include unique user ID
            "username": username,
            "side": side,
            "price": price,
            "quantity": quantity
        }

        # Send order to RabbitMQ
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
        channel.exchange_declare(exchange='orders', exchange_type='fanout')

        channel.basic_publish(exchange='orders', routing_key='', body=json.dumps(order))
        print(f"Order sent: {order}")

        connection.close()

        # Ask if the user wants to make another order
        if input("Do you want to place another order? (yes/no) ").strip().lower() != "yes":
            break

if __name__ == "__main__":
    main()
