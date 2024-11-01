import pika
import sys


positions = {}
contacts = {}   # Dictionary to keep track of the positions & contacts of each person

def on_position_message(ch, method, properties, body):
    global positions, contacts

    # Display the message (person_id, x, y)
    message = body.decode('utf-8')
    person_id, x, y = message.split(',')
    x, y = int(x), int(y)

    # Log the person's current position
    if person_id in positions:
        previous_position = positions[person_id]
        print(f"{person_id} moved from {previous_position} to ({x}, {y})")
    else:
        print(f"{person_id} started at ({x}, {y})")
    
    positions[person_id] = (x, y)

    # Check if anyone else is at the same position
    for other_person, position in positions.items():
        if other_person != person_id and position == (x, y):
            print(f"Contact: {person_id} met {other_person} at position ({x}, {y})")

            if person_id not in contacts:
                contacts[person_id] = []
            contacts[person_id].insert(0, (other_person, position))

            if other_person not in contacts:
                contacts[other_person] = []
            contacts[other_person].insert(0, (person_id, position))

def on_query_message(ch, method, properties, body):
    global contacts

    # Display the query message (person_id)
    person_id = body.decode('utf-8')

    # Prepare the response
    if person_id in contacts:
        contact_list = contacts[person_id]
        contact_info = ', '.join([f"{name} at {position}" for name, position in contact_list])
        response = f"{person_id} came into contact with: {contact_info}"
    else:
        response = f"{person_id} has not come into contact with anyone."

    # Publish the response to the 'query-response' topic
    ch.basic_publish(exchange='', routing_key='query-response', body=response)
    print(f"Responded to query for {person_id}: {response}")

# Set up the connection to RabbitMQ
def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    # Declare the 'position' exchange
    channel.exchange_declare(exchange='position', exchange_type='fanout')

    # Declare the 'query' queue and bind it to the default exchange
    channel.queue_declare(queue='query')

    # Subscribe to the 'position' topic (exchange)
    position_queue = channel.queue_declare(queue='', exclusive=True).method.queue
    channel.queue_bind(exchange='position', queue=position_queue)
    channel.basic_consume(queue=position_queue, on_message_callback=on_position_message, auto_ack=True)

    # Subscribe to the 'query' topic (queue)
    channel.basic_consume(queue='query', on_message_callback=on_query_message, auto_ack=True)

    print("Tracker started. Listening for position and query updates...")
    channel.start_consuming()

if __name__ == "__main__":
    main()
