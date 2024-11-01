import pika

# Connect to RabbitMQ
def connect_to_rabbitmq():
    
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    return channel

def callback(ch, method, properties, body):
    message = body.decode('utf-8')
    print(message)

def main():
    # Get the room name to subscribe to from the user
    room_name = input("Enter chat room name to join: ")
    channel = connect_to_rabbitmq()

    # Declare the exchange for the specific room
    channel.exchange_declare(exchange=room_name, exchange_type='fanout')

    # Create a random queue for this subscriber and bind it to the room's exchange
    result = channel.queue_declare('', exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange=room_name, queue=queue_name)

    print(f'Waiting for messages in room: {room_name}')

    try:
        channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
        channel.start_consuming()
    except KeyboardInterrupt:
        print("\nExiting chat...")
    finally:
        channel.close()

if __name__ == '__main__':
    main()
