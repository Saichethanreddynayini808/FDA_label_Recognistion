Project Overview This web app allows users to upload product images, which are analyzed to produce an FDA product code along with relevant descriptions and explanations. The app utilizes Flask as the backend framework, OpenAI for data processing, and HTML/CSS with JavaScript for the frontend. Features • Product Code Identification: Extracts and displays FDA product codes from uploaded images. • Detailed Descriptions and Explanations: Optionally display explanations and descriptions for each code component, such as industry, class, subclass, PIC, and product. • Dynamic UI: Updates output fields and displays descriptions/explanations only when requested. • User-Friendly Interface: A clean, responsive layout with a visually engaging background and straightforward controls.


Technologies Used • Backend: Flask,python • API: OpenAI API for image analysis and FDA code identification • Frontend: HTML, CSS (Bootstrap), JavaScript • Other: Pandas for CSV data handling in Python

**Installation:**

1.Download the zip file: or bash Copy code ‘git clone https://github.com/Saichethanreddynayini808/FDA_label_Recognistion.git’
2.Install dependencies: bash Copy code pip install -r requirements.txt 
3.API Key Configuration: Copy the openai key and paste it in app.py Copy code client = OpenAI( api_key="your api key here" # replace with your actual key )

Run the Flask application 
4. Open the application(app.py): 
  o Go to http://127.0.0.1:5000 in your web browser to access the app. 
  
**  Usage**

**Upload Images**: Click the "Upload" button to select product label images. Multiple images can be uploaded.

**Choose Options:** o Subclass: Enable or disable subclass detection. 

**Show Code Descriptions:** Check this option to display detailed descriptions of each code category. 
**Show Code Explanations:** Check this option to display explanations of each code category.
**View Results:** o Once processed, the FDA product code will be displayed along with optional descriptions and explanations if selected.
**Output Display:** o The main FDA Product Code section will show only the codes, while individual sections for each code (industry, class, etc.) will show both codes and descriptions or explanations 

if you want to view the database open **database.py** file from the zipfile and execute it. open http://127.0.0.1:5000/view_fda_codes
if enabled. File Structure plaintext
app.py/ │ ├── static/ │ ├── styles.css # Custom CSS for the app │ └── products.jpg # Background image │ ├── templates/ │ └── index6.html, index2.html # Main HTML template for the frontend │ ├── app.py # Flask backend application ├── requirements.txt # Python dependencies └── README.md # Project documentation
