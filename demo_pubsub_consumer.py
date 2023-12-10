import os
import json

from concurrent.futures import TimeoutError
from google.cloud import pubsub_v1

PROJECT_ID = os.environ.get('PROJECT_ID')
SUBSCRIPTION_ID = os.environ.get('SUBSCRIPTION_ID')

subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(PROJECT_ID, SUBSCRIPTION_ID)


def callback(message) -> None:
    message.ack()
    print(f'Received message: {json.loads(message.data.decode("utf-8"))}')  # Remove this from production code


# Limit the subscriber to only have ten outstanding messages at a time.
flow_control = pubsub_v1.types.FlowControl(max_messages=50)

streaming_pull_future = subscriber.subscribe(
    subscription_path, callback=callback, flow_control=flow_control
)

# Wrap subscriber in a 'with' block to automatically call close() when done.
with subscriber:
    try:
        # set timeout
        streaming_pull_future.result(timeout=300 * 2)
    except TimeoutError:
        streaming_pull_future.cancel()  # Trigger the shutdown.
