import pandas as pd
import unicodedata
from mlxtend.frequent_patterns import apriori, association_rules


def normalize_text(text):
    if not text:
        return ''

    text = str(text).lower()
    text = unicodedata.normalize('NFD', text)
    text = ''.join(
        c for c in text
        if unicodedata.category(c) != 'Mn'
    )

    return text


def detect_gender_from_text(text):
    text = normalize_text(text)

    female_keywords = [
        'nu', 'vay', 'dam', 'chan vay', 'croptop',
        'ao body', 'giay cao got', 'cardigan', 'legging'
    ]

    male_keywords = [
        'vest nam', 'ao polo nam', 'ao ba lo nam',
        'quan jean nam', 'quan short nam',
        'quan kaki nam', 'ca vat'
    ]

    if any(keyword in text for keyword in female_keywords):
        return 'female'

    if any(keyword in text for keyword in male_keywords):
        return 'male'

    return 'unisex'


def get_recommendations(category_name, product_gender=None):
    try:
        df = pd.read_csv("data/du_lieu_apriori.csv")

        df['ProductName'] = df['ProductName'].fillna('')
        df['ProductGender'] = df['ProductName'].apply(detect_gender_from_text)

        if product_gender == 'female':
            df_filtered = df[
                df['ProductGender'].isin(['female', 'unisex'])
            ]

            if not df_filtered.empty:
                df = df_filtered

        elif product_gender == 'male':
            df_filtered = df[
                df['ProductGender'].isin(['male', 'unisex'])
            ]

            if not df_filtered.empty:
                df = df_filtered

        # product_gender == 'all' thì không lọc, dùng toàn bộ dữ liệu

        basket = df.groupby(['InvoiceID', 'Category'])['Quantity']\
            .sum()\
            .unstack()\
            .fillna(0)

        basket = basket.astype(bool)

        frequent_itemsets = apriori(
            basket,
            min_support=0.01,
            use_colnames=True
        )

        if frequent_itemsets.empty:
            return []

        rules = association_rules(
            frequent_itemsets,
            metric="confidence",
            min_threshold=0.1
        )

        category_mapping = {
            # Database web -> CSV Apriori (now exactly matching database category names)
            'Áo sơ mi': 'Áo sơ mi',
            'Sơ mi': 'Áo sơ mi',

            'Áo khoác Hoodie': 'Áo khoác',
            'Hoodie': 'Áo khoác',
            'Sweater': 'Áo khoác',
            'Áo khoác': 'Áo khoác',

            'Quần Jeans Nam': 'Quần',
            'Quần jean': 'Quần',
            'Quần jogger': 'Quần',
            'Jogger': 'Quần',
            'Quần short': 'Quần',
            'Quần kaki': 'Quần',
            'Quần cargo': 'Quần',
            'Quần tây': 'Quần',
            'Quần baggy': 'Quần',
            'Legging': 'Quần',
            'Quần': 'Quần',

            'Đầm': 'Váy',
            'Váy': 'Váy',
            'Chân váy': 'Váy',

            'Áo tank top': 'Áo thun',
            'Áo tanktop': 'Áo thun',

            'Áo thun': 'Áo thun',
            'Áo polo': 'Áo thun',
            'Croptop': 'Áo thun',
            'Áo body': 'Áo body',
            'Áo len': 'Áo len',
            'Cardigan': 'Cardigan',
            'Blazer': 'Blazer',
            'Vest': 'Blazer',
            'Áo giữ nhiệt': 'Áo body',

            'Nón': 'Nón',
            'Giày': 'Giày',
            'Phụ kiện': 'Nón'
        }

        category_name = category_mapping.get(category_name, category_name)
        recommendations = []

        for _, row in rules.iterrows():
            antecedents = list(row['antecedents'])
            consequents = list(row['consequents'])

            if category_name in antecedents:
                for item in consequents:
                    recommendations.append({
                        "category": item,
                        "confidence": float(row["confidence"])
                    })

        recommendations.sort(
            key=lambda x: x["confidence"],
            reverse=True
        )

        return recommendations

    except Exception as e:
        print("APRIORI ERROR:", e)
        return []