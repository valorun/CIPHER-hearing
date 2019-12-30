from sklearn.neighbors import KNeighborsClassifier 
from sklearn.model_selection import train_test_split 
import joblib
  

class LabeledDataset:
    def __init__(self, dataset:list, labels:list):
        self.dataset = dataset
        self.labels = labels


class Model:
    def __init__(self):
        pass
    
    def train(self, labeled_dataset:LabeledDataset):
        """     	
        Fit the model using a training dataset.
        """
        pass
    
    def predict(self, dataset:list):
        """
        Predict the class labels for the provided dataset.
        """
        pass

    def score(self, labeled_dataset:LabeledDataset):
        """
        Return the mean accuracy on the given test dataset.
        """
        pass

    def save(self):
        pass

    def load(self):
        pass


class KNNModel(Model):
    def __init__(self, k):
        super().__init__()
        self.knn = KNeighborsClassifier(n_neighbors=k)

    def train(self, labeled_dataset):
        self.knn.fit(labeled_dataset.dataset, labeled_dataset.labels)

    def predict(self, dataset):
        return self.knn.predict(dataset)

    def save(self, filename):
        joblib.dump(self.knn, filename)

    def load(self, filename):
        self.knn = joblib.load(filename) 

