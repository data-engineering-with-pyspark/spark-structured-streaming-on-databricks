# Databricks notebook source
# MAGIC %run ./test-utils

# COMMAND ----------

trigger_stream = streamingBatchTestSuite()

# COMMAND ----------

trigger_stream.runStreamTests()

# COMMAND ----------

trigger_stream.runBatchTests()
