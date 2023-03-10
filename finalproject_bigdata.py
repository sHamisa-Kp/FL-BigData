# -*- coding: utf-8 -*-
"""FinalProject_BigData.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1iKKHKs_m-RIKIm4UktJmPBYxiB9D84n4

#Import Libraries
"""

# Commented out IPython magic to ensure Python compatibility.
import numpy as np
import pylab as pl
import pandas as pd

import scipy.stats
import random
import sys,itertools
from time import process_time

import matplotlib.pyplot as plt 
# %matplotlib inline
from matplotlib.cm import get_cmap
from matplotlib.colors import rgb2hex
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import style
style.use('ggplot')

import io
import requests
from sklearn.utils import shuffle
from sklearn.preprocessing import StandardScaler, LabelEncoder, MinMaxScaler
from sklearn import decomposition
from sklearn import discriminant_analysis
from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score, KFold
from sklearn.manifold import TSNE


from sklearn import svm
from sklearn import metrics
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import roc_auc_score
from mlxtend.feature_selection import SequentialFeatureSelector as SFS

from numpy.linalg import svd

import tensorflow as tf
import tensorflow.keras as tfkeras
from tensorflow.keras import backend as K

from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import Dense, Flatten, Dropout, MaxPooling1D, Conv1D, BatchNormalization, Activation
from tensorflow.keras.optimizers import SGD

TRAIN_URL = "https://drive.google.com/uc?export=download&id=16q7ZkNOSHgJ6TtEg4ngQ_MtBoC824ByN"
TEST_URL = "https://drive.google.com/uc?export=download&id=1Nd9GZT6cvx0KHEhg0bDt6VnF6picYlED"

"""# Dataset Loading and pre-processing"""

train_data_raw = requests.get(TRAIN_URL).content
train_data = shuffle(pd.read_csv(io.StringIO(train_data_raw.decode("utf-8"))))
train_data.head()

train_data.describe()
# train_data.plot(kind='box', subplots=True, layout=(33,17), sharex=False, sharey=False)
# plt.show()

test_data_raw = requests.get(TEST_URL).content
test_data = shuffle(pd.read_csv(io.StringIO(test_data_raw.decode("utf-8"))))
test_data.head()

# Splitting train features and labels
X_train = train_data.iloc[:,:-2]
y_train_string = train_data.iloc[:,-1]

X_test = test_data.iloc[:,:-2]
y_test_string = test_data.iloc[:,-1]


print('Shape of Train data : ', train_data.shape)
print('Shape of X_Train : ', X_train.shape)
print('Shape of Train class : ', y_train_string.shape)
print('Shape of Test data : ', test_data.shape)
print('Shape of X_test : ', X_test.shape)
print('Shape of Test class : ', y_test_string.shape)

# Processing the raw data with MinMaxScaler scalar
mmsc = MinMaxScaler(feature_range=(0, 1))
X_train_scaled = mmsc.fit_transform(X_train)
X_test_scaled = mmsc.transform(X_test)

labels = np.unique(y_train_string)
# labels

encoder = LabelEncoder()

y_train = encoder.fit_transform(y_train_string)
y_train_FL = pd.get_dummies(y_train).values
# y_train

y_test = encoder.fit_transform(y_test_string)
y_test_FL = pd.get_dummies(y_test).values
# y_test

label_counts = y_train_string.value_counts()
label_counts

n = y_train_string.unique().shape[0]
colormap = get_cmap('tab10')
colors = [rgb2hex(colormap(col)) for col in np.arange(0, 1.01, 1/(n-1))]
# colors

"""## Data visualisation with PCA"""

pca = decomposition.PCA(n_components=0.9, random_state=3)
pca_fit = pca.fit(X_train)
X_train_pca = pca_fit.transform(X_train)

# Transform data
tsne = TSNE(random_state=3)
tsne_transformed = tsne.fit_transform(X_train_pca)

# Create subplots
fig, axarr = plt.subplots(1, 1, figsize=(15,10))

# Plot each activity
for i, group in enumerate(label_counts.index):
    # Mask to separate sets
    mask = (y_train_string == group).values
    axarr.scatter(x=tsne_transformed[mask][:,0], y=tsne_transformed[mask][:,1], c=colors[i], alpha=0.5, label=group)
axarr.set_title('Activity Visualisation')
axarr.legend()

plt.show()

"""The PCA plot shows that the features a almost separable. So, we can use linearly separable functions.

Now we will find the variance spread of data in the range of principal components
"""

pca_var = decomposition.PCA(n_components= 561)
X_pca = pca_var.fit_transform(X_train)
var_explained = pca_var.explained_variance_ratio_

cumulative_variance = np.cumsum(var_explained)
x = np.array(range(1,562))
plt.plot(x, cumulative_variance)
plt.xlabel("Number of components")
plt.ylabel("Cumulative explained variance")
plt.title("Explained variance vs Number of components")
plt.show()

# Finding the resultant dimension of PCs
principal_components = 0
for item in cumulative_variance:
    if item <= 0.99:
        principal_components += 1
print("Resultant PCA at variance of 99% is: {}".format(principal_components + 1))

"""We can infer that we can get most of the variance of data at 99% of variation spread, so we can reduce the dimension the dataset with first 155 Principal components in feature space."""

pca_var = decomposition.PCA(n_components=155, random_state=3)

pca_training = pca_var.fit(X_train)

pca_training.explained_variance_
pca_training.n_components_
X_train_pca = pca_training.transform(X_train)
X_test_pca = pca_training.transform(X_test)

X_train_pca.shape

y_test_string

"""## Feature Selection

### SFS using Desicion tree wrapper
"""

sfs = SFS(DecisionTreeClassifier(random_state=0),
         k_features = (1, 20),
          forward= True,
          floating = False,
          verbose= 2,
          scoring= 'accuracy',
          cv = 4,
          n_jobs= -1
         ).fit(X_train, y_train)

sfs.k_score_

sfs.k_feature_names_

X_train_sfs = sfs.transform(X_train)
X_test_sfs = sfs.transform(X_test)

X_train_sfs.shape

"""### SFFS using Gaussian NB wrapper"""

sffs = SFS(GaussianNB(),
         k_features = (1, 50),
          forward= True,
          floating = False,
          verbose= 2,
          scoring= 'accuracy',
          cv = 4,
          n_jobs= -1
         ).fit(X_train, y_train)

sffs.k_score_

sffs.k_feature_names_

X_train_sffs = sffs.transform(X_train)
X_test_sffs = sffs.transform(X_test)

X_train_sffs.shape

"""# Classifier Model"""

def plot_confusion_matrix(cm,lables):
    fig, ax = plt.subplots(figsize=(6,4))
    im = ax.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    ax.figure.colorbar(im, ax=ax)

    ax.set(xticks=np.arange(cm.shape[1]),
    yticks=np.arange(cm.shape[0]),
    xticklabels=lables, yticklabels=lables,
    ylabel='True label',
    xlabel='Predicted label')
    plt.xticks(rotation = 90)
    thresh = cm.max() / 2.
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, int(cm[i, j]),ha="center", va="center",color="white" if cm[i, j] > thresh else "black")
    fig.tight_layout()

clf_models = [
    KNeighborsClassifier(5),
    svm.SVC(kernel='rbf', C=1000, gamma=0.0001),
    DecisionTreeClassifier(max_depth=7),
    RandomForestClassifier(),
    GaussianNB(),
    MLPClassifier(max_iter= 1000),
    LogisticRegression(max_iter= 2000)
]

def model_score(X_tr, X_te, y_tr, y_te):
    for clf in clf_models:
        start_tm = process_time()
        clf.fit(X_tr,y_tr)
        y_pred = clf.predict(X_te)
        f = metrics.f1_score(y_true=y_te,y_pred=y_pred,average="macro")
        print("Training accuracy for ", clf.__class__.__name__,": ", cross_val_score(clf, X_tr, y_tr, cv=5).mean())
        stop_tm = process_time()
        elapsed_tm = stop_tm - start_tm
        print(f"F1_score: {round(f,3)} \t Time taken: {round(elapsed_tm,3)} secs \t Classifier: {clf.__class__.__name__}")
        cm_raw = metrics.confusion_matrix(y_te, y_pred)
        print("Classification Report for ", clf.__class__.__name__,":\n",metrics.classification_report(y_te, y_pred))
        plt.figure(figsize=(4,4))
        print("Confusion matrix plot showing for ", {clf.__class__.__name__},"\n")
        plot_confusion_matrix(cm_raw, labels)
        plt.show() 
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n")

# evaluating with Raw data
model_score(X_train, X_test, y_train_string, y_test_string)

# evaluating using sfs encoded data
model_score(X_train_sfs, X_test_sfs, y_train_string, y_test_string)

# evalauating PCA encoded data
model_score(X_train_pca, X_test_pca, y_train_string, y_test_string)

model_score(X_train_sffs, X_test_sffs, y_train_string, y_test_string)

"""# Federated Learning Model"""

X_train_FL = X_train.to_numpy()
X_test_FL = X_test.to_numpy()

mms = MinMaxScaler(feature_range=(0, 1))
X_train_FL = mms.fit_transform(X_train_FL)
X_test_FL = mms.transform(X_test_FL)

# expanding the dimension for 1D convolution
X_test_FL = np.expand_dims(X_test_FL, axis=2)
X_train_FL = np.expand_dims(X_train_FL, axis=2)
X_train_FL.shape

# #binarize the labels
# lb = LabelBinarizer()
# y_train_FL = lb.fit_transform(y_train)
# y_test_FL = lb.transform(y_test)

def create_clients(data, label, clients_num):

    client_names = ['{}{}'.format('client', i + 1) for i in range(clients_num)]

    #data shuffling
    dataset = list(zip(data, label))
    random.shuffle(dataset)

    #dividing the data according to clients_num
    size = len(dataset)//clients_num
    partitions = [dataset[i:i + size] for i in range(0, size * clients_num, size)]

    if(len(partitions) != clients_num):
        print("Number of clients and data partitions should be the same!")

    partitions_dict = {client_names[i] : partitions[i] for i in range(clients_num)}

    return partitions_dict

class CNN_model:
    @staticmethod
    def build(n_features, n_timsteps, classes):

        model = Sequential()
        model.add(Conv1D(filters=64, kernel_size=7, activation='relu', input_shape=(n_features, n_timsteps)))
        model.add(Conv1D(filters=64, kernel_size=7, activation='relu'))
        model.add(Dropout(0.4))
        model.add(MaxPooling1D(pool_size=2))
        model.add(Flatten())
        model.add(Dense(512, activation='relu'))
        model.add(Dropout(0.4))
        model.add(BatchNormalization())
        model.add(Activation("relu"))
        model.add(Dense(256))
        model.add(Activation("relu"))
        model.add(Dense(classes))
        model.add(Activation("softmax"))

        return model
    

def scalling_factor(clients_trn_data, client_name):

    client_names = list(clients_trn_data.keys())
    temp = [tf.data.experimental.cardinality(clients_trn_data[cn]).numpy() for cn in client_names]
    global_count = sum(temp)
    local_count = tf.data.experimental.cardinality(clients_trn_data[client_name]).numpy()
    scale_factor = local_count/global_count

    return scale_factor


def scale_model_weights(weight, scale_factor):
    w_f = []
    for i in range(len(weight)):
        w_f.append(scale_factor * weight[i])
    return w_f



def sum_scaled_weights(scaled_weights):
    avg = []
    for w in zip(*scaled_weights):
        l_mean = tf.math.reduce_sum(w, axis=0)
        avg.append(l_mean)    
    return avg


def test_model(X_test, Y_test,  model, epoch):
    start = process_time()
    logits = model.predict(X_test)
    acc = accuracy_score(tf.argmax(logits, axis=1), tf.argmax(Y_test, axis=1))
    end = process_time()
    print('epoch: {} | Accuracy: {:.3%} | Testing time: {:.3} sec'.format(epoch, acc, end - start))
    return acc

#making the clients 
clients_num = 5
clients = create_clients(X_train_FL, y_train_FL, clients_num)

#batch size for each epoch
batch_size = 64

#converting each partition to tfds object according to batch_size
client_b = dict()
for (client_name, data) in clients.items():
    data_p, label_p = zip(*data)
    dataset = tf.data.Dataset.from_tensor_slices((list(data_p), list(label_p)))
    client_b[client_name] = dataset.shuffle(len(label_p)).batch(batch_size)

#converting the test data to tfds object
test_batched = tf.data.Dataset.from_tensor_slices((X_test_FL, y_test_FL)).batch(len(y_test_FL))

#number of global epochs
global_epochs = 50

#optimizer
lr = 0.01 
optimizer = SGD(lr=lr, decay=lr / global_epochs, momentum=0.9) 

#dimension for 1D convlution
n_features = X_train_FL.shape[1]
n_timesteps = X_train_FL.shape[2]

#initialize global model
CNN = CNN_model()
global_model = CNN.build(n_features, n_timesteps, 6)
FL_Accuracy = []

for epoch in range(global_epochs):
            
    global_w = global_model.get_weights()
    scaled_local_weight = []

    client_names= list(client_b.keys())
    random.shuffle(client_names)
    
    for client in client_names:
        CNN_local = CNN_model()
        local_model = CNN_local.build(n_features, n_timesteps, 6)
        local_model.compile(loss = 'categorical_crossentropy', 
                      optimizer =optimizer, 
                      metrics = ['accuracy'])
        
        local_model.set_weights(global_w)
        local_model.fit(client_b[client], epochs=2, verbose=0) 

        scaling_factor = scalling_factor(client_b, client)
        scaled_weights = scale_model_weights(local_model.get_weights(), scaling_factor)
        scaled_local_weight.append(scaled_weights)

        K.clear_session()

    avg_w = sum_scaled_weights(scaled_local_weight)
    global_model.set_weights(avg_w)

    for(Xtest, ytest) in test_batched:
        global_acc = test_model(Xtest, ytest, global_model, epoch)
        FL_Accuracy.append(global_acc)

plt.plot(FL_Accuracy)
plt.xlabel("Number of Global epochs")
plt.ylabel("Accuracy")
plt.title("Testing accuracy of Global model")
plt.show()

CNN = CNN_model()
model = CNN.build(n_features, n_timesteps, 6) 

model.compile(loss='categorical_crossentropy', 
              optimizer=optimizer, 
              metrics=['accuracy'])

history = model.fit(X_train_FL, y_train_FL, epochs=50, verbose=0)

for(Xtest, ytest) in test_batched:
        CNN_acc = test_model(Xtest, ytest, model, 1)