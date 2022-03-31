from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from itertools import combinations


app = Flask(__name__)
app = Flask(__name__, template_folder='./templates')

app.config["UPLOAD_FOLDER"] = "static/"

	
def create_frequent_items(D, C_k, min_sup):
    items_freq = {}
    for transaction in D:
        for item in C_k:
            if item.issubset(transaction):
                if item in items_freq:
                    items_freq[item] += 1
                else:
                    items_freq[item] = 1

    transactions_count = len(D)
    freq_items = []
    for item in items_freq:
        support = items_freq[item] 
        if support >= min_sup:
            freq_items.append(item)

    return freq_items


def find_frequent_1_itemset(D, min_sup):
    C_1 = []
    for transaction in D:
        for item in transaction:
            item = frozenset([item])
            if item not in C_1:
                C_1.append(item)
    L_1 = create_frequent_items(D, C_1, min_sup)
    return L_1


def has_infrequent_subset(candidate, frequent_items):
    return candidate in frequent_items


def apriori_gen(frequent_items, k):
    C_k = []
    for l1, l2 in combinations(frequent_items, 2):
        intersection = l1 & l2
        if len(intersection) == k:
            c = l1 | l2
            if has_infrequent_subset(c, C_k):
                C_k.remove(c)
            else:
                C_k.append(c)
    return C_k


def apriori(D, min_sup):
    L = [set(find_frequent_1_itemset(D, min_sup))]
    k = 1  # python list use zero based indexing, hence a 1 instead of 2
    while len(L[k-1]) > 0:
        C_k = apriori_gen(L[k-1], k-1)
        L.append(set(create_frequent_items(D, C_k, min_sup)))
        k += 1
    return [set(s) for s in set.union(L[0], *L[1:])]



@app.route('/')
def upload_file():
    return render_template('index.html')
	
@app.route('/display', methods = ['GET', 'POST'])
def algorithm():
  if request.method == 'POST':
    f = request.files['file']      
    filename = secure_filename(f.filename)
    f.save(app.config['UPLOAD_FOLDER'] + filename)
    f = open(app.config['UPLOAD_FOLDER']+filename,'r')
    transactions = []
    for line in f.readlines():
        cells = line.split(',')
        item_cells = cells[1:]
        item_cells = [int(cell.strip()) for cell in item_cells]
        transactions.append(item_cells)           
    
    min_sup = int(request.form["min_sup"])       
    
    output = apriori(transactions, min_sup)
    return render_template('index1.html',result=output,total_items = len(output))
  return render_template('index.html')

if __name__ == '__main__':
    app.run(debug = True)
        
	
