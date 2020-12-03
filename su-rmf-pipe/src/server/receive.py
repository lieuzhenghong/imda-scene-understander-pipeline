#!/usr/bin/env python
import pika, sys, os

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    
    channel.queue_declare(queue='object_detection')
    channel.queue_declare(queue='lift_safe_entry')
    channel.queue_declare(queue='lift_tailgate')

    def callback_object_detection(ch, method, properties, body):
        print("Object detection queue called")
        print(f" [x] Received {body} from {method.routing_key}")

    channel.basic_consume(queue='object_detection',
            on_message_callback=callback_object_detection,
            auto_ack=True)

    print(' [*] Waiting for message. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
