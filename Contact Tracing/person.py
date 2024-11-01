import pika
import time
import random
import sys

# Define movement directions
DIRECTIONS = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]

def move_person(person_id, x, y, move_speed, board_size=10, channel=None):
    while True:
        # Randomly pick a movement direction
        dx, dy = random.choice(DIRECTIONS)
        new_x, new_y = x + dx, y + dy

        # Ensure the person stays within the board boundaries
        if 0 <= new_x < board_size and 0 <= new_y < board_size:
            x, y = new_x, new_y

        # Publish the new position to the 'position' topic
        position_message = f"{person_id},{x},{y}"
        channel.basic_publish(exchange='position', routing_key='', body=position_message)
        print(f"{person_id} moved to ({x}, {y})")

        # Movement speed pause
        time.sleep(move_speed)

def main():
    # Ask for the user's unique identifier/name
    person_id = input("Enter your unique identifier (name): ")

    # Ask for the starting position
    try:
        x = int(input("Enter your starting X coordinate (0-9): "))
        y = int(input("Enter your starting Y coordinate (0-9): "))
    except ValueError:
        print("Invalid input. Coordinates must be integers.")
        sys.exit(1)

    # Ask for the movement speed
    try:
        move_speed = float(input("Enter the movement speed (in seconds): "))
    except ValueError:
        print("Invalid input. Speed must be a number.")
        sys.exit(1)

    # Set up the connection to RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    # Ensure the 'position' exchange exists
    channel.exchange_declare(exchange='position', exchange_type='fanout')

    # Publish the initial position
    position_message = f"{person_id},{x},{y}"
    channel.basic_publish(exchange='position', routing_key='', body=position_message)
    print(f"{person_id} started at ({x}, {y})")

    # Move the person around the board
    move_person(person_id, x, y, move_speed, board_size=10, channel=channel)

if __name__ == "__main__":
    main()
