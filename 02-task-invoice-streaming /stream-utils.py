# Databricks notebook source
class invoiceStream():
    def __init__(self):
        self.base_data_dir = "/FileStore/streaming"

    def getInvoiceSchema(self):
        return """
                    InvoiceNumber string, 
                    CreatedTime bigint, 
                    StoreID string, 
                    PosID string, 
                    CashierID string,
                    CustomerType string, 
                    CustomerCardNo string, 
                    TotalAmount double, 
                    NumberOfItems bigint, 
                    PaymentMethod string, 
                    TaxableAmount double, 
                    CGST double, 
                    SGST double, 
                    CESS double, 
                    DeliveryType string,
                    DeliveryAddress struct<
                                            AddressLine string, 
                                            City string, 
                                            ContactNumber string, 
                                            PinCode string, 
                                            State string
                                        >,
                    InvoiceLineItems array<
                                            struct<
                                                    ItemCode string, 
                                                    ItemDescription string, 
                                                    ItemPrice double, 
                                                    ItemQty bigint, 
                                                    TotalValue double
                                                >
                                        >
            """

    def read_process_Invoices(self):
        from pyspark.sql.functions import expr
        df = (spark.readStream
                    .format("json")
                    .schema(self.getInvoiceSchema())
                    .load(f"{self.base_data_dir}/data/invoices")
                )
        df = df.selectExpr("InvoiceNumber", "CreatedTime", "StoreID", "PosID",
                            "CustomerType", "PaymentMethod", "DeliveryType", "DeliveryAddress.City",
                            "DeliveryAddress.State","DeliveryAddress.PinCode", 
                            "explode(InvoiceLineItems) as LineItem")
        explode_cols = {
            "ItemCode" : expr("LineItem.ItemCode"),
            "ItemDescription" : expr("LineItem.ItemDescription"),
            "ItemPrice" : expr("LineItem.ItemPrice"),
            "ItemQty":  expr("LineItem.ItemQty"),
            "TotalValue": expr("LineItem.TotalValue")
        }
        df = df.withColumns(explode_cols).drop("LineItems")
        return df 

    def explodeInvoices(self, invoiceDF):
        return ( invoiceDF.selectExpr("InvoiceNumber", "CreatedTime", "StoreID", "PosID",
                                      "CustomerType", "PaymentMethod", "DeliveryType", "DeliveryAddress.City",
                                      "DeliveryAddress.State","DeliveryAddress.PinCode", 
                                      "explode(InvoiceLineItems) as LineItem")
                                    )  
           
    def flattenInvoices(self, explodedDF):
        from pyspark.sql.functions import expr
        return( explodedDF.withColumn("ItemCode", expr("LineItem.ItemCode"))
                        .withColumn("ItemDescription", expr("LineItem.ItemDescription"))
                        .withColumn("ItemPrice", expr("LineItem.ItemPrice"))
                        .withColumn("ItemQty", expr("LineItem.ItemQty"))
                        .withColumn("TotalValue", expr("LineItem.TotalValue"))
                        .drop("LineItem")
                )
        
    def appendInvoices(self, flattenedDF):
        return (flattenedDF.writeStream
                    .format("delta")
                    .option("checkpointLocation", f"{self.base_data_dir}/chekpoint/invoices")
                    .outputMode("append")
                    .toTable("invoice_line_items")
        )

    def process(self):
           print(f"Starting Invoice Processing Stream...", end='')
           invoicesDF = self.read_process_Invoices()
           # explodedDF = self.explodeInvoices(invoicesDF)
           # resultDF = self.flattenInvoices(explodedDF)
           sQuery = self.appendInvoices(invoicesDF)
           print("Done\n")
           return sQuery     
