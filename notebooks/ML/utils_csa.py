# Utils functions

# 1 / Verif function (print accuracy, precision, recall, F1, etc. for an algo)
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_curve, auc
from sklearn.metrics import confusion_matrix
from matplotlib import pyplot as plt
import pandas as pd
#%matplotlib inline

def show_model_accuracy(algo_name, model, pX_test, py_test, pX_columns, do_roc_curve = False, do_features_importance = False):
    predicted = model.predict(pX_test)
    confusion = confusion_matrix(py_test, predicted)
    fpr, tpr, thresholds = roc_curve(py_test, predicted)
    roc_auc = auc(fpr, tpr)
    
    # Infos
    print('----------------------------------------------------------')
    print('Results for algorithm : ' + algo_name)
    print('----------------------------------------------------------\n')
    print('Confusion Matrix\n', confusion)
    print('Accuracy: {:.2f}'.format(accuracy_score(py_test, predicted)))
    print('Precision: {:.2f}'.format(precision_score(py_test, predicted)))
    print('Recall: {:.2f}'.format(recall_score(py_test, predicted)))
    print('F1: {:.2f}'.format(f1_score(py_test, predicted)))
    print('AUC: {:.2f}'.format(roc_auc))
    print('----------------------------------------------------------\n')
    
    # Plot ROC curve
    #if do_plot is not None && do_plot <> False :
    if do_roc_curve:
        plt.title('Receiver Operating Characteristic (ROC Curve)')
        plt.plot(fpr, tpr, 'b', label = 'AUC = %0.2f' % roc_auc)
        plt.legend(loc = 'lower right')
        plt.plot([0, 1], [0, 1],'r--')
        plt.xlim([0, 1])
        plt.ylim([0, 1])
        plt.ylabel('True Positive Rate')
        plt.xlabel('False Positive Rate')
        plt.show()
        
    # View a list of the features and their importance scores
    if do_features_importance:
        importances = model.feature_importances_
        feat_importances = pd.Series(model.feature_importances_, index=pX_columns)
        feat_importances.nlargest(20).plot(kind='barh')
        plt.show()