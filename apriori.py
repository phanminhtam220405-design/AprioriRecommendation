import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules


def get_recommendations(category_name):

    try:

        df = pd.read_csv("data/du_lieu_apriori.csv")

        # Tạo ma trận giao dịch
        basket = df.groupby(
            ['InvoiceID', 'Category']
        )['Quantity'].sum().unstack().fillna(0)

        # Convert về 0/1
        basket = basket.astype(bool).astype(int)

        # Apriori
        frequent_itemsets = apriori(
            basket,
            min_support=0.001,
            use_colnames=True
        )

        if frequent_itemsets.empty:
            return []

        # Association Rules
        rules = association_rules(
            frequent_itemsets,
            metric="confidence",
            min_threshold=0.01
        )

        print("\n========== RULES ==========")
        print(rules[['antecedents', 'consequents', 'confidence']])
        print("===========================\n")

        recommendations = []

        for _, row in rules.iterrows():

            antecedents = list(row['antecedents'])
            consequents = list(row['consequents'])

            if category_name in antecedents:

                recommendations.extend(consequents)

        return list(set(recommendations))

    except Exception as e:

        print("APRIORI ERROR:", e)

        return []