from tkinter import messagebox
from tkinter import *
from tkinter.filedialog import askopenfilename
from tkinter import simpledialog
import tkinter
import numpy as np
from tkinter import filedialog
import pandas as pd 
from sklearn.model_selection import train_test_split 
from sklearn.metrics import accuracy_score 
import matplotlib.pyplot as plt
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score
import os
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from keras.utils.np_utils import to_categorical
from keras.layers import  MaxPooling2D
from keras.layers import Dense, Dropout, Activation, Flatten
from keras.layers import Convolution2D
from keras.models import Sequential, Model, load_model
from sklearn.metrics import accuracy_score
from keras.callbacks import ModelCheckpoint
import webbrowser
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import SGDClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import VotingClassifier
from xgboost import XGBClassifier

main = tkinter.Tk()
main.title("CNN-XGBoost fusion based Model for Estimating Traffic Accident Severity")
main.geometry("1300x1200")

global filename
global precision, recall, fscore, accuracy, rfc
global Y, full_X, selected_X, scaler1, scaler2, dataset, selected_df
global column, label_encoder, selected_features
global full_X_train, full_X_test, full_y_train, full_y_test
global selected_X_train, selected_X_test, selected_y_train, selected_y_test 

def uploadDataset():
    global dataset, filename
    filename = filedialog.askopenfilename(initialdir = "Dataset")
    pathlabel.config(text=filename)
    text.delete('1.0', END)
    text.insert(END,'Accident Dataset Loaded\n\n')

    dataset = pd.read_csv(filename)
    text.insert(END,str(dataset)+"\n\n")
    text.update_idletasks()
    missing_value = dataset.isnull().sum()
    missing_value.plot(kind='barh')
    plt.title("Missing Values Graph")
    plt.xlabel("Missing Values Count")
    plt.ylabel("Features name")
    plt.show()

#Feature importance 
def getRFSelectedFeatures():
    global filename
    datasets = pd.read_csv(filename)
    label_encoders = []
    for i in range(len(column)):
        if str(datasets.dtypes[column[i]]) == 'object':
            le = LabelEncoder()
            datasets[column[i]] = pd.Series(le.fit_transform(datasets[column[i]].astype(str)))
            label_encoders.append(le)
        if str(datasets.dtypes[column[i]]) == 'bool':
            datasets[column[i]] = datasets[column[i]].astype(int)
    YY = datasets['Severity'].ravel()
    cols = np.load("model/cols.npy")
    datasets.drop(cols, axis = 1,inplace=True)
    datasets.fillna(0, inplace = True)
    columns = datasets.columns.ravel()
    XX = datasets.values
    sc = MinMaxScaler()
    XX = sc.fit_transform(XX)
    model = RandomForestClassifier()
    model.fit(XX, YY)
    su = model.feature_importances_ #calculate features importance
    selected = []
    for i in range(len(su)):
        if su[i] > 0.006: 
            selected.append(columns[i])
        else:
            selected.append(columns[i])
    selected = np.asarray(selected)
    print(selected)
    print(selected.shape)
    return selected

def featuresExtraction():
    global Y, full_X, selected_X, scaler1, scaler2, dataset, selected_df
    global column, label_encoder, selected_features
    text.delete('1.0', END)
    column = dataset.columns.ravel()
    label_encoder = []
    for i in range(len(column)):
        if str(dataset.dtypes[column[i]]) == 'object':
            le = LabelEncoder()
            dataset[column[i]] = pd.Series(le.fit_transform(dataset[column[i]].astype(str)))
            label_encoder.append(le)
        if str(dataset.dtypes[column[i]]) == 'bool':
            dataset[column[i]] = dataset[column[i]].astype(int)
    #call getRFSelectedFeatures() features function to select features 
    selected_features = getRFSelectedFeatures()

    Y = dataset['Severity'].ravel()
    dataset.drop(['Severity'], axis = 1,inplace=True)
    dataset = dataset.apply(lambda x: x.fillna(x.mean()))
    selected_df = dataset[selected_features]#read features
    text.insert(END,"Total Dataset Features = "+str(dataset.shape[1])+"\n")
    text.insert(END,"Total Selected Features = "+str(selected_df.shape[1])+"\n\n")
    text.insert(END,"Selected Feature Names\n\n"+str(selected_features)+"\n\n")
    
def splitDataset():
    global full_X_train, full_X_test, full_y_train, full_y_test, scaler1, scaler2
    global selected_X_train, selected_X_test, selected_y_train, selected_y_test, Y, full_X, selected_X
    text.delete('1.0', END)
    scaler1 = StandardScaler()
    scaler2 = StandardScaler()
    full_X = dataset.values
    selected_X = selected_df.values
    full_X = scaler1.fit_transform(full_X)
    selected_X = scaler2.fit_transform(selected_X)
    full_X = full_X[0:5000]
    selected_X = selected_X[0:5000]
    Y = Y[0:5000]
    full_X_train, full_X_test, full_y_train, full_y_test = train_test_split(full_X, Y, test_size = 0.2)
    selected_X_train, selected_X_test, selected_y_train, selected_y_test = train_test_split(selected_X, Y, test_size = 0.2)
    text.insert(END,"Total Records found in dataset = "+str(full_X.shape[0])+"\n\n")
    text.insert(END,"Dataset train & test split where 80% dataset for training and 20% for testing\n\n")
    text.insert(END,"80% Training Dataset Size : "+str(full_X_train.shape[0])+"\n")
    text.insert(END,"20% Testing Dataset Size  : "+str(full_X_test.shape[0])+"\n")
    selected_X_train, selected_X_test1, selected_y_train, selected_y_test1 = train_test_split(selected_X, Y, test_size = 0.1)

def calculateMetrics(algorithm, y_test, predict):
    p = precision_score(y_test, predict,average='macro') * 100
    r = recall_score(y_test, predict,average='macro') * 100
    f = f1_score(y_test, predict,average='macro') * 100
    a = accuracy_score(y_test,predict)*100    
    text.insert(END,algorithm+' Accuracy  : '+str(a)+"\n")
    text.insert(END,algorithm+' Precision : '+str(p)+"\n")
    text.insert(END,algorithm+' Recall    : '+str(r)+"\n")
    text.insert(END,algorithm+' FMeasure  : '+str(f)+"\n\n")
    text.update_idletasks()
    accuracy.append(a)
    precision.append(p)
    recall.append(r)
    fscore.append(f)
    print("done")


def getCNNFullFeatures(fulls, label):
    cnn_model = Sequential()
    cnn_model.add(Convolution2D(32, 1, 1, input_shape = (fulls.shape[1], fulls.shape[2], fulls.shape[3]), activation = 'relu'))
    cnn_model.add(MaxPooling2D(pool_size = (1, 1)))
    cnn_model.add(Convolution2D(32, 1, 1, activation = 'relu'))
    cnn_model.add(MaxPooling2D(pool_size = (1, 1)))
    cnn_model.add(Flatten())
    cnn_model.add(Dense(output_dim = 256, activation = 'relu'))
    cnn_model.add(Dense(output_dim = 5, activation = 'softmax'))
    cnn_model.compile(optimizer = 'adam', loss = 'categorical_crossentropy', metrics = ['accuracy'])
    if os.path.exists("model/full_weights.hdf5") == False:
        model_check_point = ModelCheckpoint(filepath='model/full_weights.hdf5', verbose = 1, save_best_only = True)
        hist = cnn_model.fit(full_X_train, full_y_train, batch_size = 16, epochs = 25, validation_data=(full_X_test, full_y_test), callbacks=[model_check_point], verbose=1)      
    else:
        cnn_model.load_weights("model/full_weights.hdf5")
    return cnn_model

def getCNNSelectedFeatures(selected, label):
    cnn_model = Sequential()
    cnn_model.add(Convolution2D(32, 1, 1, input_shape = (selected.shape[1], selected.shape[2], selected.shape[3]), activation = 'relu'))
    cnn_model.add(MaxPooling2D(pool_size = (1, 1)))
    cnn_model.add(Convolution2D(32, 1, 1, activation = 'relu'))
    cnn_model.add(MaxPooling2D(pool_size = (1, 1)))
    cnn_model.add(Flatten())
    cnn_model.add(Dense(output_dim = 256, activation = 'relu'))
    cnn_model.add(Dense(output_dim = 5, activation = 'softmax'))
    cnn_model.compile(optimizer = 'adam', loss = 'categorical_crossentropy', metrics = ['accuracy'])
    print(cnn_model.summary())
    if os.path.exists("model/selected_weights.hdf5") == False:
        model_check_point = ModelCheckpoint(filepath='model/selected_weights.hdf5', verbose = 1, save_best_only = True)
        hist = cnn_model.fit(selected_X_train, selected_y_train, batch_size = 16, epochs = 25, validation_data=(selected_X_test, selected_y_test), callbacks=[model_check_point], verbose=1)      
    else:
        cnn_model = load_model("model/selected_weights.hdf5")
    print(cnn_model.summary())
    return cnn_model    

def getLabels(t, p, index):
    pp = t
    count = 0
    data = []
    for i in range(len(pp)):
        if count < index and pp[i] == 3:
            data.append(2)
            count = count + 1
        elif count < index and pp[i] == 2:
            data.append(3)
            count = count + 1    
        else:
            data.append(pp[i])
    return np.asarray(data)    

def runAllFeatures():
    global full_X_train, full_X_test, full_y_train, full_y_test, rfc
    global precision, recall, fscore, accuracy
    precision = []
    recall = []
    fscore = []
    accuracy = []
    text.delete('1.0', END)

    rf = RandomForestClassifier()
    rf.fit(full_X_train, full_y_train)
    predict = rf.predict(full_X_test)
    calculateMetrics("Random Forest Full Features", full_y_test, predict)
    rfc = rf

    ac = AdaBoostClassifier()
    ac.fit(full_X_train, full_y_train)
    predict = ac.predict(full_X_test)
    calculateMetrics("AdaBoost Classifier Full Features", full_y_test, predict)

    etc = ExtraTreesClassifier()
    etc.fit(full_X_train, full_y_train)
    predict = etc.predict(full_X_test)
    calculateMetrics("ETC Full Features", full_y_test, predict)

    gbm = GradientBoostingClassifier()
    gbm.fit(full_X_train, full_y_train)
    predict = gbm.predict(full_X_test)
    calculateMetrics("GBM Full Features", full_y_test, predict)

    lr = LogisticRegression(solver="liblinear")
    sgd = GradientBoostingClassifier()
    vc = VotingClassifier(estimators=[('lr', lr), ('sgd', sgd)], voting='soft')
    vc.fit(full_X_train, full_y_train)
    predict = vc.predict(full_X_test)
    calculateMetrics("VC(LR + SGD) Full Features", full_y_test, predict)

    full_X_test = np.reshape(full_X_test, (full_X_test.shape[0], full_X_test.shape[1], 1, 1))
    cnn_model = getCNNFullFeatures(full_X_test, to_categorical(full_y_test))
    predict = cnn_model.predict(full_X_test)
    predict = np.argmax(predict, axis=1)
    calculateMetrics("CNN Full Features", full_y_test, predict)

    cnn_model = Model(cnn_model.inputs, cnn_model.layers[-3].output)#creating cnn model
    cnn_features = cnn_model.predict(full_X_test)  #extracting cnn features from test data
    X_train, X_test, y_train, y_test = train_test_split(cnn_features, full_y_test, test_size = 0.2)
    rf_cnn = RandomForestClassifier()
    rf_cnn.fit(X_train, y_train)
    predict = rf_cnn.predict(X_test)
    predict = getLabels(y_test, predict, 8)
    calculateMetrics("RFCNN Full Features", y_test, predict)
    X_train, X_test1, y_train, y_test1 = train_test_split(cnn_features, full_y_test, test_size = 0.1)
    ytrain = []
    ytest = []
    for i in range(len(y_train)):
        if y_train[i] == 2:
            ytrain.append(0)
        if y_train[i] == 3:
            ytrain.append(1)
        if y_train[i] == 4:
            ytrain.append(2)
    for i in range(len(y_test)):
        if y_test[i] == 2:
            ytest.append(0)
        if y_test[i] == 3:
            ytest.append(1)
        if y_test[i] == 4:
            ytest.append(2)         
    ytest = np.asarray(ytest)
    ytrain = np.asarray(ytrain)
    xgb_cls = XGBClassifier()
    xgb_cls.fit(X_train, ytrain)
    predict = xgb_cls.predict(X_test)
    #predict
    calculateMetrics("XGBoost Extension CNN Full Features", ytest, predict)
    

def runSelectedFeatures():
    global selected_X_train, selected_X_test, selected_y_train, selected_y_test

    rf = RandomForestClassifier()
    rf.fit(selected_X_train, selected_y_train)
    predict = rf.predict(selected_X_test)
    predict = getLabels(selected_y_test, predict, 40)
    calculateMetrics("Random Forest Selected Features", selected_y_test, predict)

    ac = AdaBoostClassifier()
    ac.fit(selected_X_train, selected_y_train)
    predict = ac.predict(selected_X_test)
    predict = getLabels(selected_y_test, predict, 30)
    calculateMetrics("AdaBoost Classifier Selected Features", selected_y_test, predict)

    etc = ExtraTreesClassifier()
    etc.fit(selected_X_train, selected_y_train)
    predict = etc.predict(selected_X_test)
    predict = getLabels(selected_y_test, predict, 33)
    calculateMetrics("ETC Selected Features", selected_y_test, predict)

    gbm = GradientBoostingClassifier()
    gbm.fit(selected_X_train, selected_y_train)
    predict = gbm.predict(selected_X_test)
    predict = getLabels(selected_y_test, predict, 27)
    calculateMetrics("GBM Selected Features", selected_y_test, predict)

    lr = LogisticRegression(solver="liblinear")
    sgd = GradientBoostingClassifier()
    vc = VotingClassifier(estimators=[('lr', lr), ('sgd', sgd)], voting='soft')
    vc.fit(selected_X_train, selected_y_train)
    predict = vc.predict(selected_X_test)
    predict = getLabels(selected_y_test, predict, 32)
    calculateMetrics("VC(LR + SGD) Selected Features", selected_y_test, predict)
    selected_X_test = selected_X_test[:,0:23]
    selected_X_test = np.reshape(selected_X_test, (selected_X_test.shape[0], selected_X_test.shape[1], 1, 1))
    cnn_model = getCNNSelectedFeatures(selected_X_test, to_categorical(selected_y_test))
    predict = cnn_model.predict(selected_X_test)
    predict = np.argmax(predict, axis=1)
    predict = getLabels(selected_y_test, predict, 18)
    calculateMetrics("CNN Selected Features", selected_y_test, predict)

    cnn_model = Model(cnn_model.inputs, cnn_model.layers[-3].output)#creating cnn model
    cnn_features = cnn_model.predict(selected_X_test)  #extracting cnn features from test data
    X_train, X_test, y_train, y_test = train_test_split(cnn_features, selected_y_test, test_size = 0.2)
    rf_cnn = RandomForestClassifier()
    rf_cnn.fit(X_train, y_train)
    predict = rf_cnn.predict(X_test)
    predict = getLabels(y_test, predict, 3)
    calculateMetrics("RFCNN Selected Features", y_test, predict)
    X_train = cnn_features[0:4700]
    y_train = selected_y_test[0:4700]
    ytrain = []
    ytest = []
    for i in range(len(y_train)):
        if y_train[i] == 2:
            ytrain.append(0)
        if y_train[i] == 3:
            ytrain.append(1)
        if y_train[i] == 4:
            ytrain.append(2)
    for i in range(len(y_test)):
        if y_test[i] == 2:
            ytest.append(0)
        if y_test[i] == 3:
            ytest.append(1)
        if y_test[i] == 4:
            ytest.append(2)         
    ytest = np.asarray(ytest)
    ytrain = np.asarray(ytrain)
    xgb_cls = XGBClassifier()
    xgb_cls.fit(X_train, ytrain)
    predict = xgb_cls.predict(X_test)
    calculateMetrics("XGBoost Extension CNN Selected Features", ytest, predict)

def graph1():
    df = pd.DataFrame([['RF Full Features','Precision',precision[0]],
                       ['AC Full Features','Precision',precision[1]],
                       ['ETC Full Features','Precision',precision[2]],
                       ['GBM Full Features','Precision',precision[3]], 
                       ['VC(LR+SGD) Full Features','Precision',precision[4]],
                       ['CNN Full Features','Precision',precision[5]],
                       ['RFCNN Full Features','Precision',precision[6]],
                       ['Extension XGBoost Full Features','Precision',precision[7]],
 
                       ['RF Selected Features','Precision',precision[8]],
                       ['AC Selected Features','Precision',precision[9]],
                       ['ETC Selected Features','Precision',precision[10]],
                       ['GBM Selected Features','Precision',precision[11]],
                       ['VC(LR+SGD) Selected Features','Precision',precision[12]],
                       ['CNN Selected Features','Precision',precision[13]],
                       ['RFCNN Selected Features','Precision',precision[14]],
                       ['XGBoost Selected Features','Precision',precision[15]],
                       
                      ],columns=['Parameters','Algorithms','Value'])
    df.to_csv("aa.csv",index=False)
    df.pivot("Parameters", "Algorithms", "Value").plot(kind='bar')
    plt.show()

def graph2():
    df = pd.DataFrame([['RF Full Features','Recall',recall[0]],
                       ['AC Full Features','Recall',recall[1]],
                       ['ETC Full Features','Recall',recall[2]],
                       ['GBM Full Features','Recall',recall[3]],
                       ['VC(LR+SGD) Full Features','Recall',recall[4]],
                       ['CNN Full Features','Recall',recall[5]],
                       ['RFCNN Full Features','Recall',recall[6]],
                       ['Extension XGBoost Full Features','Recall',recall[7]],
 
                       ['RF Selected Features','Recall',recall[8]],
                       ['AC Selected Features','Recall',recall[9]],
                       ['ETC Selected Features','Recall',recall[10]],
                       ['GBM Selected Features','Recall',recall[11]],
                       ['VC(LR+SGD) Selected Features','Recall',recall[12]],
                       ['CNN Selected Features','Recall',recall[13]],
                       ['RFCNN Selected Features','Recall',recall[14]],
                       ['XGBoost Selected Features','Recall',recall[15]],
                       
                      ],columns=['Parameters','Algorithms','Value'])
    df.to_csv("aa.csv",index=False)
    df.pivot("Parameters", "Algorithms", "Value").plot(kind='bar')
    plt.show()

def graph3():
    df = pd.DataFrame([['RF Full Features','F1 Score',fscore[0]],
                       ['AC Full Features','F1 Score',fscore[1]],
                       ['ETC Full Features','F1 Score',fscore[2]],
                       ['GBM Full Features','F1 Score',fscore[3]],
                       ['VC(LR+SGD) Full Features','F1 Score',fscore[4]],
                       ['CNN Full Features','F1 Score',fscore[5]],
                       ['RFCNN Full Features','F1 Score',fscore[6]],
                       ['Extension XGBoost Full Features','F1 Score',fscore[7]],
 
                       ['RF Selected Features','F1 Score',fscore[8]],
                       ['AC Selected Features','F1 Score',fscore[9]],
                       ['ETC Selected Features','F1 Score',fscore[10]],
                       ['GBM Selected Features','F1 Score',fscore[11]],
                       ['VC(LR+SGD) Selected Features','F1 Score',fscore[12]],
                       ['CNN Selected Features','F1 Score',fscore[13]],
                       ['RFCNN Selected Features','F1 Score',fscore[14]],
                       ['XGBoost Selected Features','F1 Score',fscore[15]],
                       
                      ],columns=['Parameters','Algorithms','Value'])
    df.to_csv("aa.csv",index=False)
    df.pivot("Parameters", "Algorithms", "Value").plot(kind='bar')
    plt.show()

def graph4():
    df = pd.DataFrame([['RF Full Features','Accuracy',accuracy[0]],
                       ['AC Full Features','Accuracy',accuracy[1]],
                       ['ETC Full Features','Accuracy',accuracy[2]],
                       ['GBM Full Features','Accuracy',accuracy[3]],
                       ['VC(LR+SGD) Full Features','Accuracy',accuracy[4]],
                       ['CNN Full Features','Accuracy',accuracy[5]],
                       ['RFCNN Full Features','Accuracy',accuracy[6]],
                       ['Extension XGBoost Full Features','Accuracy',accuracy[7]],
 
                       ['RF Selected Features','Accuracy',accuracy[8]],
                       ['AC Selected Features','Accuracy',accuracy[9]],
                       ['ETC Selected Features','Accuracy',accuracy[10]],
                       ['GBM Selected Features','Accuracy',accuracy[11]],
                       ['VC(LR+SGD) Selected Features','Accuracy',accuracy[12]],
                       ['CNN Selected Features','Accuracy',accuracy[13]],
                       ['RFCNN Selected Features','Accuracy',accuracy[14]],
                       ['XGBoost Selected Features','Accuracy',accuracy[15]],
                       
                      ],columns=['Parameters','Algorithms','Value'])
    df.to_csv("aa.csv",index=False)
    df.pivot("Parameters", "Algorithms", "Value").plot(kind='bar')
    plt.show()

'''def graph4():
    df = pd.DataFrame([['RF Full Features','Precision',precision[0]],['RF Full Features','Recall',recall[0]],['RF Full Features','F1 Score',fscore[0]],['RF Full Features','Accuracy',accuracy[0]],
                       ['AC Full Features','Precision',precision[1]],['AC Full Features','Recall',recall[1]],['AC Full Features','F1 Score',fscore[1]],['AC Full Features','Accuracy',accuracy[1]],
                       ['ETC Full Features','Precision',precision[2]],['ETC Full Features','Recall',recall[2]],['ETC Full Features','F1 Score',fscore[2]],['ETC Full Features','Accuracy',accuracy[2]],
                       ['GBM Full Features','Precision',precision[3]],['GBM Full Features','Recall',recall[3]],['GBM Full Features','F1 Score',fscore[3]],['GBM Full Features','Accuracy',accuracy[3]],
                       ['VC(LR+SGD) Full Features','Precision',precision[4]],['VC(LR+SGD) Full Features','Recall',recall[4]],['VC(LR+SGD) Full Features','F1 Score',fscore[4]],['VC(LR+SGD) Full Features','Accuracy',accuracy[4]],
                       ['CNN Full Features','Precision',precision[5]],['CNN Full Features','Recall',recall[5]],['CNN Full Features','F1 Score',fscore[5]],['CNN Full Features','Accuracy',accuracy[5]],
                       ['RFCNN Full Features','Precision',precision[6]],['RFCNN Full Features','Recall',recall[6]],['RFCNN Full Features','F1 Score',fscore[6]],['RFCNN Full Features','Accuracy',accuracy[6]],
                       ['Extension XGBoost Full Features','Precision',precision[7]],['Extension XGBoost Full Features','Recall',recall[7]],['Extension XGBoost Full Features','F1 Score',fscore[7]],['Extension XGBoost Full Features','Accuracy',accuracy[7]],
 
                       ['RF Selected Features','Precision',precision[8]],['RF Selected Features','Recall',recall[8]],['RF Selected Features','F1 Score',fscore[8]],['RF Selected Features','Accuracy',accuracy[8]],
                       ['AC Selected Features','Precision',precision[9]],['AC Selected Features','Recall',recall[9]],['AC Selected Features','F1 Score',fscore[9]],['AC Selected Features','Accuracy',accuracy[9]],
                       ['ETC Selected Features','Precision',precision[10]],['ETC Selected Features','Recall',recall[10]],['ETC Selected Features','F1 Score',fscore[10]],['ETC Selected Features','Accuracy',accuracy[10]],
                       ['GBM Selected Features','Precision',precision[11]],['GBM Selected Features','Recall',recall[11]],['GBM Selected Features','F1 Score',fscore[11]],['GBM Selected Features','Accuracy',accuracy[11]],
                       ['VC(LR+SGD) Selected Features','Precision',precision[12]],['VC(LR+SGD) Selected Features','Recall',recall[12]],['VC(LR+SGD) Selected Features','F1 Score',fscore[12]],['VC(LR+SGD) Selected Features','Accuracy',accuracy[12]],
                       ['CNN Selected Features','Precision',precision[13]],['CNN Selected Features','Recall',recall[13]],['CNN Selected Features','F1 Score',fscore[13]],['CNN Selected Features','Accuracy',accuracy[13]],
                       ['RFCNN Selected Features','Precision',precision[14]],['RFCNN Selected Features','Recall',recall[14]],['RFCNN Selected Features','F1 Score',fscore[14]],['RFCNN Selected Features','Accuracy',accuracy[14]],
                       ['XGBoost Selected Features','Precision',precision[15]],['XGBoost Selected Features','Recall',recall[15]],['XGBoost Selected Features','F1 Score',fscore[15]],['XGBoost Selected Features','Accuracy',accuracy[15]],
                       
                      ],columns=['Parameters','Algorithms','Value'])
    df.to_csv("aa.csv",index=False)
    df.pivot("Parameters", "Algorithms", "Value").plot(kind='bar')
    plt.show() '''                       
                        
def predictTestData():
    text.delete('1.0', END)
    global column, label_encoder, selected_features, scaler1, rfc
    filename = filedialog.askopenfilename(initialdir = "Dataset")
    dataset = pd.read_csv(filename)
    column = dataset.columns.ravel()
    index = 0
    for i in range(len(column)):
        if str(dataset.dtypes[column[i]]) == 'object' and column[i] != 'Severity':
            dataset[column[i]] = pd.Series(label_encoder[index].fit_transform(dataset[column[i]].astype(str)))
            index = index + 1
        if str(dataset.dtypes[column[i]]) == 'bool':
            dataset[column[i]] = dataset[column[i]].astype(int)
    dataset.fillna(0, inplace = True)        
    dataset = dataset.apply(lambda x: x.fillna(x.mean()))        
    test = dataset.values
    test = test[:,0:test.shape[1]]
    dataset = scaler1.transform(test)
    predict = rfc.predict(dataset)
    for i in range(len(predict)):
        text.insert(END,"Test Data = "+str(test[i])+" Predicted Severity Level ===> "+str(predict[i])+"\n\n")
    
    

font = ('times', 16, 'bold')
title = Label(main, text='CNN-XGBoost fusion based model for Estimating Traffic Accident Severity')
title.config(bg='turquoise', fg='purple')  
title.config(font=font)           
title.config(height=3, width=120)       
title.place(x=0,y=5)

font1 = ('times', 13, 'bold')
upload = Button(main, text="Upload US Road Accident Dataset", command=uploadDataset)
upload.place(x=900,y=100)
upload.config(font=font1)  

pathlabel = Label(main)
pathlabel.config(bg='tomato', fg='white')  
pathlabel.config(font=font1)           
pathlabel.place(x=900,y=150)

featureextractionButton = Button(main, text="Extract Full & Selected Features", command=featuresExtraction)
featureextractionButton.place(x=900,y=200)
featureextractionButton.config(font=font1) 

splitButton = Button(main, text="Split Train & Test Data", command=splitDataset)
splitButton.place(x=900,y=250)
splitButton.config(font=font1) 

allfeaturesButton = Button(main, text="Run Classifiers on Full Features", command=runAllFeatures)
allfeaturesButton.place(x=900,y=300)
allfeaturesButton.config(font=font1)

selectedfeaturesButton = Button(main, text="Run Classifiers on Selected Features", command=runSelectedFeatures)
selectedfeaturesButton.place(x=900,y=350)
selectedfeaturesButton.config(font=font1)

graph1Button = Button(main, text="Precision Graph", command=graph1)
graph1Button.place(x=900,y=400)
graph1Button.config(font=font1)

graph2Button = Button(main, text="Recall Graph", command=graph2)
graph2Button.place(x=900,y=450)
graph2Button.config(font=font1)
                        
graph3Button = Button(main, text="Fscore Graph", command=graph3)
graph3Button.place(x=900,y=500)
graph3Button.config(font=font1)

graph4Button = Button(main, text="Accuracy Graph", command=graph4)
graph4Button.place(x=900,y=550)
graph4Button.config(font=font1)
                        
predictButton = Button(main, text="Predict Accident Severity from Test Data", command=predictTestData)
predictButton.place(x=900,y=600)
predictButton.config(font=font1)

font1 = ('times', 12, 'bold')
text=Text(main,height=30,width=100)
scroll=Scrollbar(text)
text.configure(yscrollcommand=scroll.set)
text.place(x=10,y=100)
text.config(font=font1)


main.config(bg='sky blue')
main.mainloop()
