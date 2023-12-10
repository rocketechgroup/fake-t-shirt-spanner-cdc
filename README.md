# fake-t-shirt-spanner-cdc

A fake t shirt project to test out spanner's CDC

## Setup Change Stream end to end

### Enable the Spanner change stream

```
CREATE CHANGE STREAM EverythingStream
FOR ALL;
```

### Create a pubsub topic

```
gcloud pubsub topics create fake-t-shirt-change-stream
```

### Create BigQuery Table for the CDC

```
CREATE TABLE `fake_t_shirt`.ecommerce_products_db (
  `subscription_name` STRING,
  `message_id` STRING,
  `publish_time` TIMESTAMP,
  `data` JSON,
  `attributes` JSON
)
```

### Create BigQuery Subscription

```
export PROJECT_ID=rocketech-de-pgcp-sandbox
gcloud pubsub subscriptions create fake-t-shirt-change-bq-sub \
    --topic fake-t-shirt-change-stream \
    --bigquery-table ${PROJECT_ID}:fake_t_shirt.ecommerce_products_db \
    --write-metadata
```

### Create the dataflow job via flex template

> It's best to keep the spanner metadata database in a separate cloud spanner database away from the operational one, so
> it does not impact the load, nor include this metadata table in the cdc stream

```
export SPANNER_INSTANCE_ID=fake-t-shirt
export SPANNER_DATABASE=ecommerce_products_db
export SPANNER_METADATA_INSTANCE_ID=$SPANNER_INSTANCE_ID
export SPANNER_METADATA_DATABASE=cdc_change_stream_meta
export SPANNER_CHANGE_STREAM=EverythingStream
export PUBSUB_TOPIC=fake-t-shirt-change-stream

gcloud dataflow flex-template run fake-t-shirt-product-db-cdc \
        --template-file-gcs-location=gs://dataflow-templates/2023-11-07-00_RC00/flex/Spanner_Change_Streams_to_PubSub \
        --region europe-west2 \
        --network private \
        --subnetwork regions/europe-west2/subnetworks/dataflow \
        --parameters \
    spannerInstanceId=$SPANNER_INSTANCE_ID,spannerDatabase=$SPANNER_DATABASE,spannerMetadataInstanceId=$SPANNER_METADATA_INSTANCE_ID,spannerMetadataDatabase=$SPANNER_METADATA_DATABASE,spannerChangeStreamName=$SPANNER_CHANGE_STREAM,pubsubTopic=$PUBSUB_TOPIC
```