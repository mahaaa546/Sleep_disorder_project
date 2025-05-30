# -*- coding: utf-8 -*-
"""Untitled7.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1C63kZiEtNx-PGupdf_6aF1oI9dIx0ML4
"""

from google.colab import files
import io
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, mean_squared_error
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
import os
import matplotlib.pyplot as plt
import seaborn as sns

uploaded = files.upload()
data = pd.read_csv(io.BytesIO(uploaded['sleep_health_and_lifestyle_dataset.csv']))

le = LabelEncoder()
data['Gender'] = le.fit_transform(data['Gender'])
data['Occupation'] = le.fit_transform(data['Occupation'])
data['BMI Category'] = le.fit_transform(data['BMI Category'])
data['Sleep Disorder'] = le.fit_transform(data['Sleep Disorder'])

bp_split = data['Blood Pressure'].str.split('/', expand=True)
data['Systolic_BP'] = pd.to_numeric(bp_split[0])
data['Diastolic_BP'] = pd.to_numeric(bp_split[1])
data.drop('Blood Pressure', axis=1, inplace=True)

X = data.drop(['Person ID', 'Sleep Disorder'], axis=1)
y = data['Sleep Disorder']

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

models = {}

def evaluate_model(name, model):
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    models[name] = model
    print(f"--- {name} ---")
    print("Accuracy:", acc)
    print("Classification Report:\n", classification_report(y_test, y_pred))
    print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))
    print("\n")
    return acc, y_pred

accuracies = {}
acc, pred = evaluate_model("LogisticRegression", LogisticRegression())
accuracies["LogisticRegression"] = acc

acc, pred = evaluate_model("SVM", SVC())
accuracies["SVM"] = acc

acc, pred = evaluate_model("NaiveBayes", GaussianNB())
accuracies["NaiveBayes"] = acc

acc, pred = evaluate_model("KNN", KNeighborsClassifier())
accuracies["KNN"] = acc

acc, pred = evaluate_model("RandomForest", RandomForestClassifier())
accuracies["RandomForest"] = acc

acc, pred = evaluate_model("DecisionTree", DecisionTreeClassifier())
accuracies["DecisionTree"] = acc

lin_reg = LinearRegression()
lin_reg.fit(X_train, y_train)
y_pred_lin = lin_reg.predict(X_test)
mse = mean_squared_error(y_test, y_pred_lin)
print("--- Linear Regression ---")
print("Mean Squared Error:", mse)
print("\n")

ann = Sequential()
ann.add(Dense(32, activation='relu', input_shape=(X_train.shape[1],)))
ann.add(Dense(16, activation='relu'))
ann.add(Dense(len(np.unique(y)), activation='softmax'))
ann.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
ann.fit(X_train, y_train, epochs=50, batch_size=16, verbose=0)
loss, accuracy = ann.evaluate(X_test, y_test)
print("--- ANN ---")
print("Accuracy:", accuracy)
accuracies["ANN"] = accuracy

if not os.path.exists('Results'):
    os.makedirs('Results')

for name, model in models.items():
    y_pred = model.predict(X_test)
    df_pred = pd.DataFrame({'Actual': y_test, 'Predicted': y_pred})
    df_pred.to_csv(f'Results/predictions_{name}_model.csv', index=False)

y_pred_ann = np.argmax(ann.predict(X_test), axis=1)
df_pred_ann = pd.DataFrame({'Actual': y_test, 'Predicted': y_pred_ann})
df_pred_ann.to_csv('Results/predictions_ANN_model.csv', index=False)

plt.figure(figsize=(10,6))
sns.barplot(x=list(accuracies.keys()), y=list(accuracies.values()))
plt.title('Model Accuracy Comparison')
plt.ylabel('Accuracy')
plt.xlabel('Model')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()