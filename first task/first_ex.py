import csv

from analyzer import Analyzer


def is_numeric_value(val: str) -> bool:
    try:
        float(val)
        return True
    except ValueError:
        return False


with open("first task/student_performance_dataset.csv") as file:
    reader = csv.DictReader(file)

    first_row = next(reader)

    numeric_keys = [
        key
        for key, val in first_row.items()
        if is_numeric_value(val) and "_id" not in key
    ]

    dataset = {key: [float(first_row[key])] for key in numeric_keys}

    for row in reader:
        for key in numeric_keys:
            dataset[key].append(float(row[key]))

data_analyz = Analyzer(dataset)
data_analyz.avg()
data_analyz.std()
data_analyz.min_in_column()
data_analyz.max_in_column()
data_analyz.quantile(0.5)
data_analyz.median()
data_analyz.mode()
data_analyz.correlation('final_exam_score')
data_analyz.covariance('final_exam_score')

with open('first task/result.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerow(['metrics', *data_analyz.result['metrics']])
    for key, val in data_analyz.result.items():
        if key != 'metrics':
            writer.writerow([key, *val])