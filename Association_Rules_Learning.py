# -*- coding: utf-8 -*-
"""Association_Rules_Learning.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ywA3cerSro2PRCZSPJg2cttBgmzIRWpW

# **ASSOCIATION RULE LEARNING (BİRLİKTELİK KURALI ÖĞRENİMİ)**

Our aim is to suggest products to users during the purchasing process by applying association analysis to the online retail II dataset. 

1. Importing Data & Data Preprocessing
2. Preparing ARL Data Structure (Invoice-Product Matrix)
3. Preparation of Association Rules
4. Suggesting a Product to Users at the Basket Stage
(Our aim is to suggest products to users in the product purchasing process by applying association analysis to the online retail II dataset.)

**1. Importing Data & Data Preprocessing**
"""

# Import Libraries

import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 500)
pd.set_option('display.expand_frame_repr', False)

# Libraries for Association Rules Learning & Apriori 
# !pip install mlxtend
from mlxtend.frequent_patterns import apriori, association_rules

# Import Data:

df_ = pd.read_excel('online_retail_II.xlsx', sheet_name='Year 2010-2011')

df = df_.copy()

df.info()

## Data Preprocessing

# Removing the null (missing) value 
df.isna().sum()
df.dropna(inplace=True)
#df.shape

# Let's remove the cancelled transactions (Invoice Id contains value "C")

df_Invoice = pd.DataFrame({"Invoice":[row for row in df["Invoice"].values if "C"  not in str(row)]})
df_Invoice.head()
df_Invoice = df_Invoice.drop_duplicates("Invoice")

# The transactions except cancelled transactions:
df = df.merge(df_Invoice, on = "Invoice")

# Removing  Outliers with Interquartile Range Method:

# Price:

Q1 = df["Price"].quantile(0.01)
Q3 = df["Price"].quantile(0.99)
IQR = Q3- Q1
low_limit = Q1 - 1.5 * IQR
up_limit = Q3 + 1.5 * IQR

df.loc[(df["Price"] < low_limit), "Price"] = low_limit
df.loc[(df["Price"] > up_limit ), "Price"] = up_limit

 # Quantity:
 
Q1 = df["Quantity"].quantile(0.01)
Q3 = df["Quantity"].quantile(0.99)
IQR = Q3- Q1

low_limit = Q1 - 1.5 * IQR
up_limit = Q3 + 1.5 * IQR

df.loc[(df["Quantity"] < low_limit), "Quantity"] = low_limit
df.loc[(df["Quantity"] > up_limit ), "Quantity"] = up_limit

# Removing values less than or equal to 0 in the variables Quantity and Price:

df = df[df["Quantity"] > 0]
df = df[df["Price"] > 0]

# Unique Number of Products (with Description)

df.Description.nunique()

# Unique Number of Products (with StockCode)

df.StockCode.nunique()

# The unique values of these 2 variables (Description & StockCode) should be equal, because each stock code represents a product.

# 1st Step
df_product = df[["Description","StockCode"]].drop_duplicates()
df_product = df_product.groupby(["Description"]).agg({"StockCode":"count"}).reset_index()

df_product.rename(columns={'StockCode':'StockCode_Count'},inplace=True)

df_product = df_product.sort_values("StockCode_Count", ascending=False)
df_product = df_product[df_product["StockCode_Count"]>1]

df_product.head()

# Let's delete products with more than one stock code:

df = df[~df["Description"].isin(df_product["Description"])]

print(df.StockCode.nunique())
print(df.Description.nunique())

# 2nd Step
df_product = df[["Description","StockCode"]].drop_duplicates()
df_product = df_product.groupby(["StockCode"]).agg({"Description":"count"}).reset_index()
df_product.rename(columns={'Description':'Description_Count'},inplace=True)
df_product = df_product.sort_values("Description_Count", ascending=False)
df_product = df_product[df_product["Description_Count"] > 1] 

df_product.head()

# Let's delete stock codes that represent multiple products:

df = df[~df["StockCode"].isin(df_product["StockCode"])]

# Now each stock code represents a single product:

print(df.StockCode.nunique())
print(df.Description.nunique())

# The post statement in the stock code shows the postage cost, let's delete it as it is not a product:

df = df[~df["StockCode"].str.contains("POST", na=False)]

# Let's work on shopping transactions with Germany as an example:  

df_germany = df[df["Country"] == "Germany"]

"""**2. Preparing ARL Data Structure (Invoice-Product Matrix)**"""

gr_inv_pro_df = create_invoice_product_df(df_germany, id=True)
gr_inv_pro_df.columns = gr_inv_pro_df.columns.droplevel(0)
gr_inv_pro_df.head(5)

# Let's define a function to find the product name corresponding to the stock code:

def check_id(dataframe, stockcode):
    product_name = dataframe[dataframe["StockCode"] == stockcode]["Description"].unique()[0]
    return stockcode, product_name
    
check_id(df_germany, 10002)

"""**3.Preparation of Association Rules**"""

# Calculate the support values for every possible configuration of items (thereshold of support has been chosen 0.01 (1%))

frequent_itemsets = apriori(gr_inv_pro_df, min_support=0.01, use_colnames=True)
frequent_itemsets.sort_values("support", ascending=False).head(100)

# Finding frequent patterns, associations

rules = association_rules(frequent_itemsets, metric="support", min_threshold=0.01)
rules.sort_values("support", ascending=False).head(5)

""" * In addition to the **antecedent (if)** and the **consequent (then)**, an association rule has two numbers that express the degree of uncertainty about the rule. In association analysis, the antecedent and consequent are sets of items (called itemsets) that are disjoint (do not have any items in common). (https://www.solver.com/xlminer/help/association-rules)

* **antecedent support:** If X is called antecendent,  'antecedent support' computes the proportion of transactions that contain the antecedent X.

* **consequent support:** If Y is called consequent,  'consequent support' computes the proportion of transactions that contain the antecedent Y.

* **support:** 'support' computes the proportion of transactions that contain the antecedent X and Y.

* **confidence:** Probability of buying Y when X is bought.

* **lift:** Represents how many times the probability of getting Y increases when X is received.
"""

rules.sort_values("lift", ascending=False).head(500)

"""**4.Suggesting a Product to Users at the Basket Stage**

We can develop different strategies at the product offer stage. For example,
When X is bought, we can sort according to the probability of buying Y (confidence) and make a product offer, or we can make an offer according to how many times the probability of sales over the lift increases. We can also make a product recommendation with a hybrid filtering where support, lift and confidence are used together. 

"""

# If user buys a product whose id is 22492, which products do you recommend?

product_id = 22492
check_id(df, product_id)

#  Let's assume that we make a product recommendation based on lift. 
sorted_rules = rules.sort_values("lift", ascending=False)
sorted_rules.head()

product_id = 22492

recommendation_list = []

for idx, product in enumerate(sorted_rules["antecedents"]):
    for j in list(product):
        if j == product_id:
            recommendation_list.append(list(sorted_rules.iloc[idx]["consequents"])[0])
            recommendation_list = list( dict.fromkeys(recommendation_list) )

# Let's bring the top 5 most preferred products together with the product with id 22492

list_top5 = recommendation_list[0:5]
list_top5

# Let's show the product names of top 5 recommended products:

for elem in list_top5:
  print(check_id(df_germany,elem))

"""**What can be done if it is integrated with the sales platform?** 


> Each product and related products can be stored at the database level and an integrated structure can be established with the purchasing processes. Thus, while a customer is purchasing product A, the first 3 products related to this product can be offered as an offer by calling the relevant product from the database. 
"""

