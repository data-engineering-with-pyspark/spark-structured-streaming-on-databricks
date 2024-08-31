# Databricks notebook source
# MAGIC %run ./test-utils

# COMMAND ----------

invoice_stream = invoiceStreamTestSuite()
invoice_stream.runTests()	
