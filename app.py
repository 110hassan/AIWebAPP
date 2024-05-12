from flask import Flask, render_template, request, url_for, session, redirect, jsonify
from datetime import date
import re
import time
import numpy as np
import cv2
import os
import random
import sqlite3 
import pandas as pd
import tensorflow
from tensorflow import keras
from keras.models import load_model
from flask_mysqldb import MySQL


app = Flask(__name__)

def is_valid_name(name):
    # Check if the name contains at least one alphabetic character and not entirely alphanumeric
    return any(char.isalpha() for char in name) and not name.isalnum()

def is_valid_place(place):
    # Check if place contains a comma and has two parts (city, country)
    parts = place.split(',')
    return len(parts) == 2 and all(part.strip() for part in parts)


app.config['SESSION_TYPE'] = 'memcached'
app.config['SECRET_KEY'] = 'super secret key'
#MySQL database connection
#app.config['MYSQL_HOST'] = 'localhost'
#app.config['MYSQL_USER'] = 'root'
#app.config['MYSQL_PASSWORD'] = ""
#app.config['MYSQL_DB'] = "aiwebapp"

#mysql = MySQL(app)

connect = sqlite3.connect('aiwebapp.db') 
connect.execute('''CREATE TABLE IF NOT EXISTS reports (
	report_id	INTEGER NOT NULL,
	Name	TEXT,
	Age	INTEGER,
	Gender	TEXT,
	Email	TEXT,
	Place	TEXT,
	Date	TEXT,
	Time	TEXT,
	Diagnosis	TEXT,
	Interpretations	TEXT,
	Recommendations	TEXT,
	Image	BLOB,
	PRIMARY KEY(report_id AUTOINCREMENT)
)''')

model_path = "models/Vgg16-5ClassesAdv.h5"
model2_path = "models/lungOpacityVgg19.h5"
model3_path = "models/otherCasesVgg16.h5"
model4_path = "models/IdentifierVGG16 (1).h5"


upload_folder = os.path.join('static', 'uploads')
 
app.config['UPLOAD'] = upload_folder

@app.route('/', methods=['GET'])
def start():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def predict():
    imageFile = request.files['imageFile']
    filename = imageFile.filename
    imagePath = os.path.join(app.config['UPLOAD'], filename)
    imageFile.save(imagePath)
    
    image_data = imageFile.read()
    name = request.form['name']
    age = request.form['age']
    gender = request.form['gender']
    contact = request.form['email']
    place = request.form['place']

    pneumonia_statements = [
        "The CXR image shows increased density areas and discernible infiltrates which suggests that there is Pneumonia found in the given image.",
        "Signs of pneumonia are evident in the CXR image, indicating an inflammatory condition in the lungs.",
        "The presence of infiltrates on the CXR image indicates a high likelihood of pneumonia.",
        "Pneumonia is suspected based on the observed opacities and consolidation patterns in the lungs.",
        "The CXR reveals findings consistent with pneumonia, warranting further evaluation and treatment."
    ]

    other_cases_statements = {
        0: [
            "The CXR reveals an enlarged cardiac silhouette, suggestive of cardiomegaly.",
            "Cardiomegaly is evident on the CXR, indicating an enlargement of the heart.",
            "Enlargement of the heart is observed on the CXR, consistent with cardiomegaly.",
            "Signs of cardiomegaly are noted on the CXR, indicative of an enlarged heart.",
            "Cardiomegaly is suspected based on the increased cardiac shadow observed on the CXR."
        ],
        1: [
            "Pulmonary edema is indicated by the presence of diffuse opacities and vascular congestion on the CXR.",
            "The CXR shows evidence of pulmonary edema, characterized by diffuse infiltrates and Kerley B lines.",
            "Interstitial edema is observed on the CXR, suggesting fluid accumulation in the lung interstitium.",
            "The CXR findings are consistent with pulmonary edema, reflecting fluid accumulation in the lungs.",
            "Pulmonary vascular congestion and interstitial edema are noted on the CXR, indicative of pulmonary edema."
        ],
        2: [
            "A pneumothorax is suspected based on the presence of a visible pleural line and absence of lung markings beyond it on the CXR.",
            "The CXR reveals evidence of a pneumothorax, characterized by the absence of lung markings and presence of a visible pleural line.",
            "A pneumothorax is indicated by the presence of a hyperlucent area and mediastinal shift on the CXR.",
            "The CXR shows signs of pneumothorax, with evidence of lung collapse and pleural air.",
            "Suspicion of pneumothorax is raised based on the presence of a visceral pleural line and absence of lung markings on the CXR."
        ]
    }


    lung_opacity_statements = {
        0: [
            "The CXR shows evidence of consolidation, indicating fluid or material filling the airspaces of the lungs.",
            "Consolidation is observed on the CXR, suggestive of inflammatory changes in the lung parenchyma.",
            "The presence of consolidation on the CXR suggests a localized area of lung infection or inflammation.",
            "Characteristic findings of consolidation, such as air bronchograms, are noted on the CXR.",
            "Consolidation is suspected based on the dense opacities observed on the CXR."
        ],
        1: [
            "Emphysema is evident on the CXR, characterized by hyperinflation and decreased lung markings.",
            "The CXR reveals signs of emphysema, including lung hyperinflation and flattened diaphragms.",
            "Destructive changes in the lung parenchyma consistent with emphysema are observed on the CXR.",
            "Emphysematous changes, such as bullae and decreased vascular markings, are noted on the CXR.",
            "The presence of emphysema is suspected based on the appearance of hyperlucent lung fields on the CXR."
        ],
        2: [
            "A nodule or mass is observed on the CXR, indicating a focal abnormality in the lung parenchyma.",
            "The CXR reveals a nodular or mass-like opacity, suggestive of a focal lesion in the lung tissue.",
            "The presence of a nodule or mass on the CXR raises concern for possible neoplastic or infectious etiologies.",
            "Characteristics of the nodule or mass, such as calcifications or spiculated margins, are noted on the CXR.",
            "Suspicion of a nodule or mass is raised based on the presence of a well-defined opacity on the CXR."
        ],
        3: [
            "Pulmonary fibrosis is indicated by the presence of reticular opacities and traction bronchiectasis on the CXR.",
            "The CXR shows evidence of fibrotic changes, characterized by linear opacities and honeycombing.",
            "Interstitial fibrosis is observed on the CXR, suggesting scarring and architectural distortion of the lung parenchyma.",
            "The presence of fibrotic bands and subpleural cysts is noted on the CXR, consistent with pulmonary fibrosis.",
            "Fibrotic changes in the lung parenchyma are suspected based on the presence of reticular opacities and volume loss on the CXR."
        ],
        4: [
            "The CXR reveals signs of lung infiltration, suggestive of inflammatory or infectious changes in the lung tissue.",
            "Infiltrates are observed on the CXR, indicating the presence of inflammatory cells or exudates within the lung parenchyma.",
            "The presence of infiltrates on the CXR suggests a pathological process, such as pneumonia or pulmonary edema.",
            "Characteristic patterns of infiltration, such as patchy opacities or air bronchograms, are noted on the CXR.",
            "Infiltrative changes in the lung parenchyma are suspected based on the presence of diffuse or localized opacities on the CXR."
        ],
        5: [
            "Atelectasis is evident on the CXR, characterized by lung collapse and mediastinal shift towards the affected side.",
            "The CXR reveals signs of atelectasis, including increased density and volume loss in the affected lung.",
            "Subsegmental or lobar collapse consistent with atelectasis is observed on the CXR.",
            "The presence of atelectasis is suspected based on the presence of airless lung parenchyma and crowding of vessels on the CXR.",
            "Atelectatic changes, such as loss of volume and opacification, are noted on the CXR."
        ],
        6: [
            "Pleural effusion is indicated by the presence of blunting of costophrenic angles and meniscus sign on the CXR.",
            "The CXR shows evidence of pleural effusion, characterized by a concave meniscus and obliteration of the diaphragm.",
            "The presence of pleural effusion is suspected based on the presence of a homogeneous opacity above the diaphragm on the CXR.",
            "Loculated or free-flowing pleural fluid is observed on the CXR, consistent with pleural effusion.",
            "The CXR reveals signs of pleural effusion, including a sharp interface between the fluid and adjacent lung parenchyma."
        ]
    }



    covid_statements = [
        "The CXR image displays bilateral ground-glass opacities and consolidations, predominantly in the lower lung zones with a peripheral distribution, indicative of COVID-19.",
        "Characteristic findings of COVID-19, such as ground-glass opacities, are observed on the CXR image.",
        "The presence of bilateral lung infiltrates suggests COVID-19 infection.",
        "COVID-19 pneumonia is suspected based on the radiographic findings.",
        "The CXR reveals patterns consistent with COVID-19 pneumonia, necessitating immediate medical attention."
    ]


    normal_statements = [
        "This is a normal CXR image without any abnormalities.",
        "No significant findings are noted on the CXR image, indicating a healthy condition.",
        "The CXR image appears within normal limits, suggesting no acute pathology.",
        "The absence of opacities or abnormalities in the lungs indicates a normal radiographic appearance.",
        "Normal lung fields are observed on the CXR image, indicating no evidence of disease."
    ]


    # Recommendations for each main class
    recommendations = {
        0: [
            "Consult a healthcare professional for appropriate treatment and follow-up. Antibiotics or antiviral medications may be prescribed depending on the type and severity of pneumonia.",
            "Seek prompt medical attention to prevent complications associated with pneumonia. Timely treatment is essential for a successful recovery.",
            "Follow your healthcare provider's recommendations closely and complete the prescribed course of medication for pneumonia treatment.",
            "Maintain good respiratory hygiene and rest adequately to support your body's immune response against pneumonia.",
            "Stay hydrated and nourished to aid in the recovery process and strengthen your body's defenses against pneumonia."
        ],
        1: [
            "Further evaluation by a healthcare professional is recommended for accurate diagnosis and appropriate management. Follow-up imaging studies or clinical assessments may be necessary to determine the underlying cause and severity of the condition.",
            "Follow your healthcare provider's recommendations for managing lung opacity, including medication adherence and lifestyle modifications.",
            "Attend regular check-ups with your healthcare provider to monitor changes in lung opacity and adjust treatment plans as necessary.",
            "Engage in pulmonary rehabilitation programs or breathing exercises to improve lung function and alleviate symptoms associated with lung opacity.",
            "Adopt strategies to reduce exposure to environmental pollutants and irritants that may exacerbate lung opacity and respiratory symptoms."
        ],
        2: [
            "Please isolate yourself and seek medical advice for further evaluation. Follow the recommended safety guidelines, such as wearing masks and practicing social distancing, to prevent the spread of the virus.",
            "Adhere to quarantine protocols and follow your healthcare provider's instructions for managing COVID-19 symptoms and preventing transmission to others.",
            "Monitor your symptoms closely and seek emergency medical care if you experience severe respiratory distress or worsening symptoms.",
            "Stay informed about updates on COVID-19 prevention and treatment measures from reliable sources such as public health authorities and medical professionals.",
            "Practice self-care techniques, such as adequate rest, hydration, and nutrition, to support your body's recovery from COVID-19."
        ],
        3: [
            "Immediate medical attention is required for further evaluation and management. Treatment options may include medications, lifestyle modifications, or surgical interventions depending on the underlying condition.",
            "Follow your healthcare provider's advice for managing the identified condition and attend regular follow-up appointments for monitoring.",
            "Implement lifestyle changes as recommended by your healthcare provider to optimize your overall health and well-being.",
            "Engage in activities that promote cardiovascular and respiratory health, such as regular exercise and smoking cessation, as advised by your healthcare provider.",
            "Adhere to prescribed medications and treatment regimens diligently to effectively manage the identified condition and minimize complications."
        ],
        4: [
            "No further action is required. Regular health check-ups are encouraged to monitor overall well-being.",
            "Maintain a healthy lifestyle with balanced nutrition, regular exercise, and adequate rest to support optimal health.",
            "Continue to follow preventive healthcare measures, such as vaccinations and screenings, as recommended by your healthcare provider.",
            "Stay vigilant for any changes in your health and promptly report any unusual symptoms to your healthcare provider.",
            "Take proactive steps to prevent the onset of respiratory illnesses and maintain lung health, such as avoiding exposure to smoke and air pollutants."
        ]
    }

    # Interpretations for each main class
    interpretations = {
        0: [
            "The presence of pneumonia indicates an inflammatory condition in the lungs. Early diagnosis and treatment are crucial to prevent complications and promote recovery.",
            "Pneumonia is a serious respiratory infection that requires prompt medical intervention. Timely treatment can prevent the spread of infection and improve outcomes.",
            "Infiltrates and increased density areas observed on the CXR suggest the presence of pneumonia. Close monitoring and appropriate management are essential for a successful recovery.",
            "The diagnosis of pneumonia underscores the importance of maintaining strong immune defenses and practicing preventive measures to reduce the risk of respiratory infections.",
            "Identification of pneumonia on the CXR highlights the need for comprehensive evaluation and individualized treatment plans to address the underlying cause and prevent recurrence."
        ],
        1: [
            "The presence of lung opacity suggests abnormalities in the lung structure. Prompt medical attention is advised to identify the underlying pathology and initiate timely treatment.",
            "Identification of lung opacity on the CXR indicates the need for further diagnostic evaluation and targeted interventions to address the underlying cause.",
            "The CXR findings suggest pathological changes in the lungs requiring comprehensive assessment and management.",
            "Abnormal opacities observed on the CXR warrant close monitoring and timely interventions to prevent disease progression and optimize patient outcomes.",
            "Detection of lung opacity underscores the importance of individualized care and collaborative decision-making between healthcare providers and patients."
        ],
        2: [
            "The presence of COVID-19 in the image indicates a potential viral infection. Immediate medical attention is advised to prevent further transmission and ensure proper care.",
            "Recognition of characteristic radiographic features of COVID-19 pneumonia on the CXR highlights the importance of prompt isolation and medical evaluation.",
            "Identification of COVID-19 pneumonia underscores the need for strict adherence to infection control measures and public health guidelines.",
            "The CXR findings suggest COVID-19 infection, necessitating timely testing, isolation, and medical management to reduce disease spread and severity.",
            "Confirmation of COVID-19 pneumonia on the CXR underscores the urgency of medical intervention and adherence to recommended protocols for disease management and containment."
        ],
        3: [
            "The presence of cardiac abnormalities or lung conditions suggests potential cardiovascular or respiratory issues. Prompt assessment and appropriate interventions are necessary to address the identified abnormalities and prevent complications.",
            "Identification of other cardiopulmonary abnormalities on the CXR underscores the importance of further evaluation and targeted management strategies.",
            "Abnormal findings on the CXR indicate the presence of conditions other than pneumonia, necessitating specialized care and tailored treatment approaches.",
            "The CXR reveals additional abnormalities warranting comprehensive evaluation and multidisciplinary management to optimize patient outcomes.",
            "Recognition of other classes of abnormalities on the CXR highlights the complexity of differential diagnosis and the need for a systematic approach to patient care."
        ],
        4: [
            "The absence of abnormalities suggests a healthy condition of the lungs. This is a reassuring finding, indicating no significant pathology detected.",
            "Normal lung fields observed on the CXR indicate optimal respiratory function and absence of acute pathology.",
            "Recognition of a normal CXR underscores the importance of regular screening and preventive healthcare measures for maintaining lung health.",
            "The absence of abnormalities on the CXR supports a favorable prognosis and overall well-being.",
            "Normal radiographic findings reassure the absence of acute respiratory illness or structural abnormalities in the lungs."
        ]
    }

    model = load_model(model_path)
    model2 = load_model(model2_path)
    model3 = load_model(model3_path)
    model4 = load_model(model4_path)

    def generate_report(img_path):
        image = cv2.imread(img_path)
        # Resize the image
        image = cv2.resize(image, (224, 224))
        # Convert the image to grayscale
        # Normalize pixel values to the range [0, 1]
        image = image / 255.0
        # Expand dimensions to match the input shape expected by the model
        image = np.expand_dims(image, axis=0)
        # Convert to numpy array (optional, as the previous line already returns a NumPy array)
        image = np.array(image)
    
        #NOt CXr = 0, CXR = 1
        predictions = model4.predict(image)
        cxr_identifier = np.argmax(predictions[0])

        # If the image is not a CXR, return an error message
        if cxr_identifier == 0:
            return "The uploaded image is not a CXR. Please upload a CXR PA image for proper and accurate diagnosis.", "", "", "",""
        else:
            # Continue with the diagnosis if the image is a CXR
            predictions = model.predict(image)
            highest_prob_index = np.argmax(predictions[0])
            confidence_value = predictions[0][highest_prob_index] * 100
            confidence = round(confidence_value, 1)

            if highest_prob_index == 2 and confidence < 80:
                # If the highest predicted class is COVID and confidence is less than 70%
                # Find the second highest probability class
                predictions[0][highest_prob_index] = 0  # Exclude the COVID class
                second_highest_prob_index = np.argmax(predictions[0])
                highest_prob_index = second_highest_prob_index

            class_label = highest_prob_index
            #["Pneumonia","Other Classes","Lung Opacity","Covid","Normal"]
            #"Pneumonia","Lung Opacity","Covid","Other Cases","Normal"
            # Select caption based on class label using if-else statements
            if class_label == 0:  # Pneumonia
                caption = random.choice(pneumonia_statements)
                recommendation = random.choice(recommendations[class_label])
                interpretation = random.choice(interpretations[class_label])
    
            elif class_label == 1:  # Lung Opacity
                caption = ""
                pred = model2.predict(image)
                sub_class = np.argmax(pred[0])
                #['Consolidation','Emphysema','Nodule & Mass','Fibrosis','Infiltration','Atelectasis','Effusion']
                if sub_class == 0:
                    caption = random.choice(lung_opacity_statements[sub_class])
                elif sub_class == 1:
                    caption = random.choice(lung_opacity_statements[sub_class])
                elif sub_class == 2:
                    caption = random.choice(lung_opacity_statements[sub_class])
                elif sub_class == 3:
                    caption = random.choice(lung_opacity_statements[sub_class])
                elif sub_class == 4:
                    caption = random.choice(lung_opacity_statements[sub_class])
                elif sub_class == 5:
                    caption = random.choice(lung_opacity_statements[sub_class])
                elif sub_class == 6:
                    caption = random.choice(lung_opacity_statements[sub_class])
                recommendation = random.choice(recommendations[class_label])
                interpretation = random.choice(interpretations[class_label])
    
            elif class_label == 2:  # COVID
                caption = random.choice(covid_statements)
                recommendation = random.choice(recommendations[class_label])
                interpretation = random.choice(interpretations[class_label])
            
            elif class_label == 3:  # Other Classes
                caption = ""
                pred = model3.predict(image)
                sub_class = np.argmax(pred[0])
                #['Cardiomegaly','Edema','Pneumothorax']
                if sub_class == 0:
                    caption = random.choice(other_cases_statements[sub_class])
                elif sub_class == 1:
                    caption = random.choice(other_cases_statements[sub_class])
                elif sub_class == 2:
                    caption = random.choice(other_cases_statements[sub_class])
                recommendation = random.choice(recommendations[class_label])
                interpretation = random.choice(interpretations[class_label])
    
            elif class_label == 4:  # Normal
                caption = random.choice(normal_statements)
                recommendation = random.choice(recommendations[class_label])
                interpretation = random.choice(interpretations[class_label])
    
    
            return "", caption, recommendation, interpretation, confidence

    # Generate report using caption, recommendation, and interpretation
    message, caption, recommendation, interpretation, confidence = generate_report(imagePath)

    if not is_valid_name(name):
        session['error'] = 'Name should contain at least one alphabetic character and not consist entirely of numbers or alphanumeric characters.'
        return redirect(url_for('error_page'))
    
    try:
        age = int(age)
        if age <= 0:
            session['error'] = 'Age should be greater than 0.'
            return redirect(url_for('error_page'))
    except ValueError:
        session['error'] = 'Invalid age format. Age should be a valid integer.'
        return redirect(url_for('error_page'))
    
    if not is_valid_place(place):
        session['error'] = 'Invalid place format. It should be City, Country.'
        return redirect(url_for('error_page'))

    t = time.localtime()
    clock = time.strftime("%H:%M:%S", t)

    today = date.today()
    d = today.strftime("%B %d, %Y")

    with sqlite3.connect("aiwebapp.db") as reports: 
        cur = reports.cursor()
        cur.execute("INSERT INTO reports (Name, Age, Gender, Email, Place, Date, Time, Diagnosis, Interpretations, Recommendations, Image) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (name,age,gender,contact,place,today,clock,caption,interpretation,recommendation,image_data))
        reports.commit()

    #print("GENERATED REPORT")
    #print("\nDiagnosis:", caption)
    #print("\nRecommendation:", recommendation)
    #print("\nInterpretations:", interpretation)

    #if request.method == 'POST':
    #session["recommendation"] = recommendation
        #return redirect(url_for('print', recommendation=recommendation))
    return render_template('predict.html',img=imagePath,date=str(d),time=clock,name=name,age=age,contact=contact,place=place,gender=gender,message=message,diagnosis=caption,recommendations=recommendation,interpretations=interpretation,confidence=confidence)

@app.route('/error')
def error_page():
    error = session.get("error")
    return render_template('error.html',error=error)

@app.route('/reports') 
def reports(): 
    connect = sqlite3.connect('aiwebapp.db') 
    cursor = connect.cursor() 
    cursor.execute('SELECT * FROM reports') 
  
    data = cursor.fetchall() 
    return render_template("reports.html", data=data)


if __name__ == '__main__':
    app.run(debug=False)
