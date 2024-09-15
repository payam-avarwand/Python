import csv

def fill_missing_values(file1, file2, output_file):
    """
    Fills missing values in the 'cl1' column of file2 with corresponding values from file1 based on 'cl2' column.

    Args:
        file1 (str): Path to the first CSV file.
        file2 (str): Path to the second CSV file.
        output_file (str): Path to the output CSV file.
    """

    # Create a mapping between 'cl2' and 'cl1' values from file1
    mapping = {}
    with open(file1, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        for row in reader:
            mapping[row[1]] = row[0]

    # Fill missing values in file2
    with open(file2, 'r') as f, open(output_file, 'w', newline='') as output:
        reader = csv.reader(f)
        writer = csv.writer(output)
        writer.writerow(next(reader))  # Write header
        for row in reader:
            if not row[0]:
                row[0] = mapping.get(row[1], '')  # Fill missing value or use empty string
            writer.writerow(row)

# Example usage
file1 = 'D:\file01.csv'
file2 = 'D:\file02.csv'
output_file = 'D:\output.csv'
fill_missing_values(file1, file2, output_file)