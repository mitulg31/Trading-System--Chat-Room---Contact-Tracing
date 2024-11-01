import pika

def connect_to_rabbitmq():
    # Connect to RabbitMQ (running on localhost in this case)
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    return channel

def main():
    # Get the username and chat room name from the user
    username = input("Enter your username: ")
    room_name = input("Enter chat room name: ")
    channel = connect_to_rabbitmq()

    # Declare the exchange for the specific room
    channel.exchange_declare(exchange=room_name, exchange_type='fanout')

    print(f'You can start typing your messages. To exit press CTRL+C')

    try:
        while True:
            message = input()
            formatted_message = f"{username}: {message}"
            channel.basic_publish(exchange=room_name, routing_key='', body=formatted_message)
            print(f"{formatted_message}")
    except KeyboardInterrupt:
        print("\nExiting chat...")
    finally:
        channel.close()

if __name__ == '__main__':
    main()
