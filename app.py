from flask import Flask, request, jsonify, render_template
import pandas as pd
from openai import OpenAI
import sqlite3

# Initialize OpenAI client with your API key
client = OpenAI(
    api_key="your api key here"  # replace with your actual key
)
#this is the app
app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('fda_codes.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fda_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            industry_code TEXT,
            industry_description TEXT,
            class_code TEXT,
            class_description TEXT,
            subclass_code TEXT,
            subclass_description TEXT,
            pic_code TEXT,
            pic_description TEXT,
            product_code TEXT,
            product_description TEXT,
            fda_code TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def insert_fda_code(data):
    conn = sqlite3.connect('fda_codes.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO fda_codes (
            industry_code, industry_description,
            class_code, class_description,
            subclass_code, subclass_description,
            pic_code, pic_description,
            product_code, product_description,
            fda_code
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['industry'], data['industry_description'],
        data['class'], data['class_description'],
        data['subclass'], data['subclass_description'],
        data['PIC'], data['PIC_description'],
        data['product'], data['product_description'],
        data['fda_code']
    ))
    conn.commit()
    conn.close()

init_db()
@app.route('/')
def home():
    return render_template('index6.html')

@app.route('/get_fda_code', methods=['POST'])
def get_fda_code():
    data = request.get_json()
    images_base64 = data['images_base64']  # Array of base64-encoded images
    include_subclass = data.get('include_subclass', True)  # Include subclass by default
    show_descriptions = data.get('show_descriptions', False)  # Checkbox for descriptions
    show_explanations = data.get('show_explanations', False)  # Checkbox for explanations

    # Process images and get detailed FDA codes and explanations
    fda_code = get_FDA_code_from_images_base64(images_base64, include_subclass, show_descriptions, show_explanations)
    insert_fda_code(fda_code)
    return jsonify(fda_code)

def get_FDA_code_from_images_base64(images_base64, include_subclass=True, show_descriptions=False, show_explanations=False):
    # Combine all images into one request and analyze them as a group
    image_data_list = [f"data:image/jpeg;base64,{image_base64}" for image_base64 in images_base64]

    # Load FDA data from CSVs
    industry_csv_file_path = "industry_api_result_data.csv"
    subclass_csv_file_path = "subclassforfood.csv"
    pic_csv_file_path = "picmodified.csv"

    # Read CSV files into dataframes
    industry_csv = pd.read_csv(industry_csv_file_path)
    subclass_csv = pd.read_csv(subclass_csv_file_path)
    pic_csv = pd.read_csv(pic_csv_file_path)

    # Convert CSVs to JSON for use in prompts
    industry_data = industry_csv.to_json(orient='records')
    subclass_data = subclass_csv.to_json(orient='records')
    pic_data = pic_csv.to_json(orient='records')

    # Step 1: Get the Industry Code
    response_industry = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Can you provide the industry code of this product based on these images? Use the following FDA industry data: {industry_data}. Output only the industry code."
                    },
                    *[{"type": "image_url", "image_url": {"url": img_data}} for img_data in image_data_list]
                ],
            }
        ],
        max_tokens=100
    )
    industry_code = response_industry.choices[0].message.content.strip()

    # Get Industry Description and Explanation (if needed)
    industry_description = ""
    industry_explanation = ""
    if show_descriptions:
        response_industry_description = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Provide the INDDESC of the '{industry_code}' from the industry data: {industry_data}. Just the inddesc, nothing else."
                        }
                    ],
                }
            ],
            max_tokens=200
        )
        industry_description = response_industry_description.choices[0].message.content.strip()

    if show_explanations:
        response_industry_explanation = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Can you detail the reasoning behind assigning product code of '{industry_code}' from the dataset {industry_data} ? include Features or ingredients which helped to determine the code,is this product satisfying all Compliance with FDA regulations or classifications and what are they,Similar products and their assigned codes,Insights from subject matter experts and can you give everything in one phara and under 200 words"
                        }
                    ],
                }
            ],
            max_tokens=300
        )
        industry_explanation = response_industry_explanation.choices[0].message.content.strip()

    # Step 2: Get the Class Code and Explanation
    class_csv_file_path = f"class_data_industry_{industry_code}.csv"
    class_csv = pd.read_csv(class_csv_file_path)
    class_data = class_csv.to_json(orient='records')

    response_class = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Can you provide the class code of this product based on these images? Use the following FDA class data: {class_data}. Output only the class code."
                    },
                    *[{"type": "image_url", "image_url": {"url": img_data}} for img_data in image_data_list]
                ],
            }
        ],
        max_tokens=100
    )
    class_code = response_class.choices[0].message.content.strip()

    class_description = ""
    class_explanation = ""
    if show_descriptions:
        response_class_description = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Provide the CLASSDESC for the '{class_code}' from the class dataset: {class_data}. Just give the classdesc, nothing else."
                        }
                    ],
                }
            ],
            max_tokens=200
        )
        class_description = response_class_description.choices[0].message.content.strip()

    if show_explanations:
        if show_explanations:
            response_class_explanation = client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"Can you detail the reasoning behind assigning product code of '{class_code}' from the dataset {class_data} ? include Features or ingredients that helped to determined the code ,Compliance with FDA regulations or classifications ,Similar products and their assigned codes,Insights from subject matter experts and can you give everythinh in one phara and under 200 words"
                            }
                        ],
                    }
                ],
                max_tokens=300
            )
        class_explanation = response_class_explanation.choices[0].message.content.strip()

    # Step 3: Get Subclass Code and Explanation (if included)
    subclass_code = "No subclass provided"
    subclass_description = ""
    subclass_explanation = ""
    if include_subclass:
        response_subclass = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Can you provide the subclass code of this product based on these images? Use the following FDA subclass data: {subclass_data}. Output only the subclass code."
                        },
                        *[{"type": "image_url", "image_url": {"url": img_data}} for img_data in image_data_list]
                    ],
                }
            ],
            max_tokens=100
        )
        subclass_code = response_subclass.choices[0].message.content.strip()

        if show_descriptions:
            response_subclass_description = client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"Provide the SUBCLASSDESC for the '{subclass_code}' from the dataset {subclass_data}. Just give the SUBCLASSDESC, nothing else."
                            }
                        ],
                    }
                ],
                max_tokens=200
            )
            subclass_description = response_subclass_description.choices[0].message.content.strip()

        if show_explanations:
            response_subclass_explanation = client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"Can you detail the reasoning behind assigning product code of '{subclass_code}' from the dataset {subclass_data} ? include addressing any more granular attributes that distinguish this product ,Compliance with FDA regulations or classifications,Similar subclass that might be fit for this,Insights from subject matter experts and can you give everything in one phara and under 200 words"
                            }
                        ],
                    }
                ],
                max_tokens=300
            )
            subclass_explanation = response_subclass_explanation.choices[0].message.content.strip()

    # Step 4: Get PIC Code and Explanation
    response_PIC = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Can you provide the PIC code of this product based on these images? Use the following FDA PIC data: {pic_data}. Output only the PIC code."
                    },
                    *[{"type": "image_url", "image_url": {"url": img_data}} for img_data in image_data_list]
                ],
            }
        ],
        max_tokens=100
    )
    pic_code = response_PIC.choices[0].message.content.strip()

    pic_description = ""
    pic_explanation = ""
    if show_descriptions:
        response_PIC_description = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Provide the PICDESC for the '{pic_code}' from the pic dataset: {pic_data}. Just give the PICDESC, nothing else."
                        }
                    ],
                }
            ],
            max_tokens=200
        )
        pic_description = response_PIC_description.choices[0].message.content.strip()

    if show_explanations:
        response_PIC_explanation = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Can you detail the reasoning behind assigning product code of '{pic_code}' from the dataset {pic_data} ? include Features or ingredients that match specific criteria for a code,how this pic code satisfies with Compliance with FDA regulations or classifications and what are they,Similar products and their assigned codes,Insights from subject matter experts and give everytho=ing in one phara and under 200 words"
                        }
                    ],
                }
            ],
            max_tokens=300
        )
        pic_explanation = response_PIC_explanation.choices[0].message.content.strip()

    # Step 5: Get the Product Code and Explanation
    product_csv_file_path = f"product_data_industry_{industry_code}.csv"
    product_csv = pd.read_csv(product_csv_file_path)
    product_data = product_csv.to_json(orient='records')

    response_product = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"Can you provide the product code of this product based on these images? Use the following FDA product data: {product_data}. Output only the product code, just the  code nothing else."
                    },
                    *[{"type": "image_url", "image_url": {"url": img_data}} for img_data in image_data_list]
                ],
            }
        ],
        max_tokens=100
    )
    product_code = response_product.choices[0].message.content.strip()

    product_description = ""
    product_explanation = ""
    if show_descriptions:
        response_product_description = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Provide the PRODDESC for the '{product_code}' from the product dataset:give me all the product which matches {product_data}. Just give the PRODDESC, nothing else."
                        }
                    ],
                }
            ],
            max_tokens=200
        )
        product_description = response_product_description.choices[0].message.content.strip()

    if show_explanations:
        response_product_explanation = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Can you detail how it captures the product’s distinct identity for '{product_code} from the dataset {product_data} '? include Features or ingredients that match specific criteria for a code,is this product satisfies this Compliance with FDA regulations or classifications and what are they,Similar products and their assigned codes and its differences,Insights from subject matter experts and give everything in one phara and under 200 words"
                        }
                    ],
                }
            ],
            max_tokens=300
        )
        product_explanation = response_product_explanation.choices[0].message.content.strip()

    # Combine all collected data into the final object
    fda_code_data = {
        'industry': industry_code,
        'industry_description': industry_description,
        'industry_explanation': industry_explanation,
        'class': class_code,
        'class_description': class_description,
        'class_explanation': class_explanation,
        'subclass': subclass_code,
        'subclass_description': subclass_description,
        'subclass_explanation': subclass_explanation,
        'PIC': pic_code,
        'PIC_description': pic_description,
        'PIC_explanation': pic_explanation,
        'product': product_code,
        'product_description': product_description,
        'product_explanation': product_explanation,
        'fda_code': f"{industry_code} {class_code} {subclass_code} {pic_code} {product_code}"
    }

    return fda_code_data

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
