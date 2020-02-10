from sklearn.neighbors import KNeighborsClassifier 
from sklearn.model_selection import train_test_split 
import joblib


class LabeledDataset:
    def __init__(self, features:list, labels:list):
        self.features = features
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

    def predict_proba(self, dataset:list):
        """
        Return probability estimates for the provided dataset.
        """
        pass

    #def score(self, labeled_dataset:LabeledDataset):
    #    """
    #    Return the mean accuracy on the given test data and labels.
    #    """
    #    pass

    def save(self):
        pass

    def load(self):
        pass


class KNNModel(Model):
    def __init__(self, k, min_proba):
        super().__init__()
        self.knn = KNeighborsClassifier(n_neighbors=k)
        self.min_proba = min_proba # min proba allowing a classe being selected

    def train(self, labeled_dataset):
        self.knn.fit(labeled_dataset.features, labeled_dataset.labels)

    def predict(self, dataset):
        probabilities = self.predict_proba(dataset)
        prediction = self.knn.predict(dataset)

        # delete all distant predictions
        return [prediction[i] for i in range(len(probabilities)) if max(probabilities[i]) > self.min_proba]

    def predict_proba(self, dataset):
        return self.knn.predict_proba(dataset)

    #def score(self, labeled_dataset):
    #    return self.knn.score(labeled_dataset.features, labeled_dataset.labels)

    def save(self, filename):
        joblib.dump(self.knn, filename)

    def load(self, filename):
        self.knn = joblib.load(filename) 

