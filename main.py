import argparse

from evaluation import evaluate_results
from generatereport import generate_report
from preprocessing import preprocessing_data
from embedding import embeddings
from classification import training_classifier
from function import delete_files_embeddings, delete_files_graphics, delete_files_preprocessing, delete_files_results, get_output_dirs
from statisticaltest import test_statistical_tests
from error_analysis import analyze_errors

def parse_args():
    parser = argparse.ArgumentParser(description="Run the clinical embedding benchmark pipeline.")
    parser.add_argument(
        "--dataset", choices=["heart_disease", "diabetes130"], default="heart_disease",
        help="Clinical dataset to use (default: heart_disease)."
    )
    return parser.parse_args()

def main():
    args = parse_args()

    #each dataset gets its own datas/<dataset>/ tree, so switching --dataset never
    #touches the previous run of a different dataset
    dirs = get_output_dirs(args.dataset)

    #phase 0: clean up this dataset's own prior run (embeddings, preprocessing, results, graphics)
    delete_files_embeddings(dirs["embeddings"])
    delete_files_preprocessing(dirs["preprocessing"])
    delete_files_results(dirs["results"])
    delete_files_graphics(dirs["graphics"])

    #preprocessing phase 1: load, clean, encode, scale data
    X,y = preprocessing_data(dataset=args.dataset)

    #embedding generation phase 2: generate embeddings with ollama
    embeddings(X, y, dataset=args.dataset)

    #classification phase 3: train and evaluate classifier
    training_classifier(dataset=args.dataset)

    #evaluation phase 4: analyze results, plot graphs, save summary table
    evaluate_results(dataset=args.dataset)

    #error analysis phase 5: trace misclassified cases back to clinical features
    analyze_errors(dataset=args.dataset)

    #test phase 6: perform statistical tests and save results
    test_statistical_tests(dataset=args.dataset)

    #report generation phase 7: create markdown report with results and graphs
    generate_report(dataset=args.dataset)

if __name__ == "__main__":
    main()

