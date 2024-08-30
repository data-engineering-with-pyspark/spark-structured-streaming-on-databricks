# Databricks notebook source
# MAGIC %run ./test-utils

# COMMAND ----------

stream_test_suite = streamWCTestSuite()
stream_test_suite.runTests()
