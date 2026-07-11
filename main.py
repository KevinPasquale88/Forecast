from evaluation import evaluate_results
from generatereport import generate_report
from preprocessing import preprocessing_data
from embedding import embeddings
from classification import training_classifier
from function import delete_files_embeddings, delete_files_graphics, delete_files_preprocessing, delete_files_results
from statisticaltest import test_statistical_tests
from error_analysis import analyze_errors

def main():
    #phase 0: clean up files pipelines and embeddings
    delete_files_embeddings()
    delete_files_preprocessing()
    delete_files_results()
    delete_files_graphics()
    
    #preprocessing phase 1: load, clean, encode, scale data
    X,y = preprocessing_data()

    #embedding generation phase 2: generate embeddings with ollama
    embeddings(X,y)

    #classification phase 3: train and evaluate classifier
    training_classifier()
    
    #evaluation phase 4: analyze results, plot graphs, save summary table
    evaluate_results()

    #error analysis phase 5: trace misclassified cases back to clinical features
    analyze_errors()

    #test phase 6: perform statistical tests and save results
    test_statistical_tests()
    
    #report generation phase 7: create markdown report with results and graphs
    generate_report()

if __name__ == "__main__":
    main()

