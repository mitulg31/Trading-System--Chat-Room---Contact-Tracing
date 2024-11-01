import pika
import json

order_book = {}  # Store orders with unique IDs
order_id_counter = 0

def callback(ch, method, properties, body):
    global order_id_counter
    order = json.loads(body)

    feedback_message = ""

    # Prevent users from buying their own shares using user_id instead of username
    if order['side'] == 'SELL':
        existing_sell_order_id = None
        for order_id, existing_order in order_book.items():
            if existing_order['user_id'] == order['user_id'] and existing_order['side'] == 'SELL':
                existing_sell_order_id = order_id
                break

        if existing_sell_order_id is not None:
            # If a sell order exists, update the price
            order_book[existing_sell_order_id]['price'] = order['price']
            print(f"SELL order updated: {order['username']} updated their sell price to {order['price']}")
        else:
            # If no existing sell order, add a new one
            order_id = order_id_counter
            order_book[order_id] = order
            order_id_counter += 1
            print(f"New SELL order added: {order}")

        # Check for matching BUY orders
        for buy_order_id, buy_order in list(order_book.items()):
            if buy_order['side'] == 'BUY' and buy_order['price'] >= order['price']:
                if buy_order['user_id'] == order['user_id']:
                    feedback_message = "You cannot buy your own shares."
                    print(feedback_message)
                else:
                    print(f"Trade successful: {order['username']} sold to {buy_order['username']} at {order['price']}")
                    publish_trade(order, buy_order['username'], order['price'])
                    del order_book[buy_order_id]  # Remove matched order from order book
                break
        else:
            print("No matching BUY order found.")
    
    elif order['side'] == 'BUY':
        order_id = order_id_counter
        order_book[order_id] = order
        order_id_counter += 1
        print(f"New BUY order added: {order}")

        # Now check for matching SELL orders
        for sell_order_id, sell_order in list(order_book.items()):
            if sell_order['side'] == 'SELL' and sell_order['price'] <= order['price']:
                if sell_order['user_id'] == order['user_id']:
                    feedback_message = "You cannot buy your own shares."
                    print(feedback_message)
                else:
                    print(f"Trade successful: {sell_order['username']} sold to {order['username']} at {sell_order['price']}")
                    publish_trade(sell_order, order['username'], sell_order['price'])
                    del order_book[sell_order_id]  # Remove matched order from order book
                break
        else:
            # Feedback for unsuccessful order
            if not feedback_message:
                print("No matching SELL order found.")

def publish_trade(sell_order, buyer_username, price):
    trade = {
        "buyer": buyer_username,
        "seller": sell_order['username'],
        "price": price,
        "quantity": sell_order['quantity']
    }
    
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange='trades', exchange_type='fanout')
    
    channel.basic_publish(exchange='trades', routing_key='', body=json.dumps(trade))
    print(f"Trade published: {trade}")
    
    connection.close()

def main():
    # RabbitMQ connection setup
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange='orders', exchange_type='fanout')
    
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange='orders', queue=queue_name)

    print('Waiting for orders. To exit press CTRL+C')

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

if __name__ == "__main__":
    main()
