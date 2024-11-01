import pika
import json

def callback(ch, method, properties, body):
    trade = json.loads(body)
    print(f"Trade successful: {trade['buyer']} bought from {trade['seller']} at ${trade['price']} for {trade['quantity']} shares.")

def main():
    # RabbitMQ connection setup
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    
    # Declare 'trades' exchange as fanout
    channel.exchange_declare(exchange='trades', exchange_type='fanout')
    
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    
    # Bind the queue to the 'trades' exchange
    channel.queue_bind(exchange='trades', queue=queue_name)

    print('Waiting for successful trades. To exit press CTRL+C')

    # Subscribe to the 'trades' exchange and process incoming messages
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

if __name__ == "__main__":
    main()
