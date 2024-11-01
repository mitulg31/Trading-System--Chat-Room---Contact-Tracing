import pika
import sys

def on_query_response(ch, method, properties, body):
    response = body.decode('utf-8')
    print(response)
    sys.exit(0)  # Exit after receiving the response

def main():
    person_id = input("Enter the name of the person to check contact status: ")

    # Set up the connection to RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    # Declare the 'query' queue and 'query-response' queue
    channel.queue_declare(queue='query')
    channel.queue_declare(queue='query-response')

    # Publish the query request to the 'query' queue
    channel.basic_publish(exchange='', routing_key='query', body=person_id)
    print(f"Sent query for {person_id}")

    # Listen for the response on the 'query-response' queue
    channel.basic_consume(queue='query-response', on_message_callback=on_query_response, auto_ack=True)

    print("Waiting for response...")
    channel.start_consuming()

if __name__ == "__main__":
    main()
