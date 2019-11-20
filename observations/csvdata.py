import csv

def get_fields(rows):
    """find the fieldnames in a list of dictionaries"""
    fieldnames = set()
    for row in rows:
        if isinstance(row, dict):
            for k,v in row.items():
                fieldnames.add(k)
    return fieldnames

def write_csv(rows, filename, fieldnames=None):
    """write the data from the row dictionaries"""
    # if fieldnames is not specified, try to get the fields
    if fieldnames is None:
        fieldnames = get_fields(rows)
        
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)
    
def read_csv(filename):
    """read a csvfile into a list of dictionaries (each row is a dictionary)"""
    try:
        with open(filename, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            return list(reader)
    except Exception as e:
        return []
    
def findrow(rows, item):
    """find a row index that contains the item"""
    for idx, row in enumerate(rows):
        for k,v in item.items():
            if row.get(k) == v:
                return idx
    return -1


if __name__ == '__main__':
    # testing writing to a file
    annotations = []
    filename = 'test_annotations.csv'
    row = {'name':'Slim Shady','age':28,'musicstyle':'rap'}
    annotations.append(row)
    row = {'name':'Bruce Wayne','age':35, 'job':'superhero', 'secretidentity':'Batman'}
    annotations.append(row)
    fields = get_fields(annotations)
    print(fields)
    write_csv(annotations, filename)
    
    # test reading from a file
    temp = read_csv(filename)
    for idx, item in enumerate(temp):
        print(idx, item)
    
    # test integrity... note that in reality, we can only reliably store strings!
    for idx, row in enumerate(annotations):
        for k,v in row.items():
            if findrow(temp, {k:str(v)}) != idx:
                print("FAIL",idx,k,v)
    
    