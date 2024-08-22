import os
import pandas as pd


def get_words_number(data_frame: pd.DataFrame) -> int:
    words_number = 0
    for _, row in data_frame.iterrows():
        words_number += len(row['text'].split())
    return words_number


if __name__ == '__main__':
    csv_file_name = '../founders_dataset_IDP.csv'
    filter_columns = ['person_name']
    names = pd.read_csv(csv_file_name, usecols=filter_columns)

    twitter_csv_dir = '/Users/k/Desktop/Courses/idp/twitter_csv/'
    linkedin_csv_dir = '/Users/k/Desktop/Courses/idp/linkedin_csv/'
    result_csv_dir = '/Users/k/Desktop/Courses/idp/result_csv/'

    # set the minimum wnumber of ords one csv file should contain
    minimum_words_number = None

    for index, row in names.iterrows():
        name = row['person_name']
        twitter_csv_file = twitter_csv_dir + name + '.csv'
        linkedin_csv_file = linkedin_csv_dir + name + '.csv'
        result_csv_file = result_csv_dir + name + '.csv'
        if os.path.exists(twitter_csv_file) and \
                os.path.exists(linkedin_csv_file):
            twitter_data = pd.read_csv(twitter_csv_file)
            linkedin_data = pd.read_csv(linkedin_csv_file)
            result_data = pd.concat([twitter_data, linkedin_data], axis=1)
            if get_words_number(result_data) >= minimum_words_number:
                result_data.to_csv(result_csv_file, index=False)
        elif os.path.exists(twitter_csv_file):
            twitter_data = pd.read_csv(twitter_csv_file)
            if get_words_number(twitter_data) >= minimum_words_number:
                twitter_data.to_csv(result_csv_file, index=False)
        elif os.path.exists(linkedin_csv_file):
            linkedin_data = pd.read_csv(linkedin_csv_file)
            if get_words_number(linkedin_data) >= minimum_words_number:
                linkedin_data.to_csv(result_csv_file, index=False)
        else:
            continue
