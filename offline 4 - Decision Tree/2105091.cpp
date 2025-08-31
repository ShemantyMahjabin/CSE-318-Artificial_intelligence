#include <iostream>
#include <vector>
#include <string>
#include <fstream>
#include <sstream>
#include <cmath>
#include <map>
#include <unordered_map>
#include <set>
#include <algorithm>
#include <random>
#include <ctime>

using namespace std;

enum Criterion {
    IG,
    IGR,
    NWIG
};

struct Encoder {
    unordered_map<string, int> nameToId;
    vector<string> idToName;
    //strig theke number conversion
    int encode(const string& s) {
        auto it = nameToId.find(s);
        if (it != nameToId.end()) {
            return it->second;
        }
        int idx = idToName.size();
        nameToId[s] = idx;
        idToName.push_back(s);
        return idx;
    }
    string decode(int id) const {
        if (id >= 0 && id < (int)idToName.size()) {
            return idToName[id];
        }
        return "?";// Invalid
    }
};


struct Example {
    vector<double> numFeatures;
    vector<int> catFeatures;
    int label;
    
    bool operator<(const Example& other) const {
        if (label != other.label) return label < other.label;
        if (numFeatures != other.numFeatures) return numFeatures < other.numFeatures;
        return catFeatures < other.catFeatures;
    }
};



class Dataset {
public:
    vector<Example> data;
    vector<Encoder> featureEncoders;
    Encoder labelEncoder;
    vector<bool> isNumericFeature;

    int size() const {
        return data.size();
    }

    int numFeatures() const {
        return isNumericFeature.size();
    }

    void readCSV(const string& filename, bool hasHeader) {
        data.clear();
        featureEncoders.clear();
        isNumericFeature.clear();
        
        ifstream fin(filename);
        if (!fin.is_open()) {
            cerr << "Error: Cannot open file " << filename << endl;
            return;
        }
        
        string line;
        if (hasHeader) getline(fin, line);
        
        vector<vector<string>> rawData;
        while (getline(fin, line)) {
            if (line.empty()) continue;
            stringstream ss(line);
            string item;
            vector<string> fields;
            while (getline(ss, item, ',')) {
                size_t start = item.find_first_not_of(" \t");
                size_t end = item.find_last_not_of(" \t");
                if (start == string::npos) item = "";
                else item = item.substr(start, end - start + 1);
                fields.push_back(item);
            }
            if (fields.size() < 2) continue;
            
            bool missing = false;
            for (const auto& f : fields) {
                if (f == "?" || f.empty()) {
                    missing = true;
                    break;
                }
            }
            if (missing) continue;
            rawData.push_back(fields);
        }
        
        if (rawData.empty()) {
            cerr << "Error: No valid data found in file" << endl;
            return;
        }
        
        bool isIris = filename.find("Iris.csv") != string::npos;
        int featureStart = isIris ? 1 : 0;
        int nFeatures = rawData[0].size() - 1 - featureStart;
        
        featureEncoders.resize(nFeatures);
        isNumericFeature.resize(nFeatures, true);
        
        //  features numeric na categorical
        for (int i = 0; i < nFeatures; ++i) {
            for (const auto& row : rawData) {
                try {
                    stod(row[i + featureStart]);
                } catch (...) {
                    isNumericFeature[i] = false;
                    break;
                }
            }
        }
        
        // Process
        for (const auto& fields : rawData) {
            Example ex;
            ex.numFeatures.resize(nFeatures);
            ex.catFeatures.resize(nFeatures);
            
            for (int i = 0; i < nFeatures; ++i) {
                if (isNumericFeature[i]) {
                    ex.numFeatures[i] = stod(fields[i + featureStart]);
                    ex.catFeatures[i] = 0;
                } else {
                    ex.numFeatures[i] = 0.0;
                    ex.catFeatures[i] = featureEncoders[i].encode(fields[i + featureStart]);
                }
            }
            ex.label = labelEncoder.encode(fields.back());
            data.push_back(ex);
        }
        
        cout << "Loaded " << data.size() << " examples with " << nFeatures << " features" << endl;
    }



    pair<Dataset, Dataset> split(double trainRatio) const {
        vector<Example> shuffled = data;
        static random_device rd;
        static mt19937 g(rd());
        shuffle(shuffled.begin(), shuffled.end(), g);
        
        int trainSize = static_cast<int>(trainRatio * shuffled.size());
        Dataset train, test;
        
        train.featureEncoders = featureEncoders;
        train.labelEncoder = labelEncoder;
        train.isNumericFeature = isNumericFeature;
        test.featureEncoders = featureEncoders;
        test.labelEncoder = labelEncoder;
        test.isNumericFeature = isNumericFeature;
        
        train.data.assign(shuffled.begin(), shuffled.begin() + trainSize);
        test.data.assign(shuffled.begin() + trainSize, shuffled.end());
        
        return {train, test};
    }
};



class Node {
public:
    int splitAttribute;
    double splitThreshold;
    int classLabel;
    map<int, Node*> children;
    Node* left;
    Node* right;
    bool isLeaf;
    bool isNumericSplit;

    Node() : isLeaf(false), splitAttribute(-1), classLabel(-1), splitThreshold(0), left(nullptr), right(nullptr), isNumericSplit(false) {}
    Node(int label) : classLabel(label), isLeaf(true), splitAttribute(-1), splitThreshold(0), left(nullptr), right(nullptr), isNumericSplit(false) {}

    ~Node() {
        // Safe deletion
        for (auto& pair : children) {
            if (pair.second) {
                delete pair.second;
                pair.second = nullptr;
            }
        }
        children.clear();
        
        if (left) {
            delete left;
            left = nullptr;
        }
        if (right) {
            delete right;
            right = nullptr;
        }
    }
};



double entropy(const vector<Example>& examples) {
    if (examples.empty()) return 0.0;
    
    unordered_map<int, int> freq;
    for (const auto& e : examples) {
        freq[e.label]++;
    }
    
    double entropy = 0.0;
    for (const auto& p : freq) {
        double probability = static_cast<double>(p.second) / examples.size();
        if (probability > 0) {
            entropy -= probability * log2(probability);
        }
    }
    return entropy;
}


double InformationGain(const vector<Example>& examples, int attrID, const Dataset& dataset) {
    if (examples.empty()) return 0.0;
    
    double totalEntropy = entropy(examples);
    
    map<int, vector<Example>> splits;
    for (const auto& e : examples) {
        splits[e.catFeatures[attrID]].push_back(e);
    }
    
    double weightedEntropy = 0.0;
    for (const auto& p : splits) {
        double subsetEntropy = entropy(p.second);
        double weight = static_cast<double>(p.second.size()) / examples.size();
        weightedEntropy += weight * subsetEntropy;
    }
    
    return totalEntropy - weightedEntropy;
}


double InformationGainRatio(const vector<Example>& examples, int attrID, const Dataset& dataset) {
    if (examples.empty()) return 0.0;
    
    double gain = InformationGain(examples, attrID, dataset);
    
    map<int, vector<Example>> splits;
    for (const auto& e : examples) {
        splits[e.catFeatures[attrID]].push_back(e);
    }
    
    double intrinsicValue = 0.0;
    for (const auto& p : splits) {
        double probability = static_cast<double>(p.second.size()) / examples.size();
        if (probability > 0) {
            intrinsicValue -= probability * log2(probability);
        }
    }
    
    if (intrinsicValue == 0) return 0.0;
    return gain / intrinsicValue;
}



double NormalizedWeightedInformationGain(const vector<Example>& examples, int attrID, const Dataset& dataset) {
    if (examples.empty()) return 0.0;
    
    double gain = InformationGain(examples, attrID, dataset);
    
    map<int, vector<Example>> splits;
    for (const auto& e : examples) {
        splits[e.catFeatures[attrID]].push_back(e);
    }
    
    int k = splits.size();
    int S = examples.size();
    
    if (k <= 1) return 0.0;
    
    double nwig = (gain / log2(k)) * (1.0 - (k - 1.0) / S);
    return nwig;
}



int majorityLabelOf(const vector<Example>& data) {
    if (data.empty()) return 0;
    
    unordered_map<int, int> freq;
    for (const auto& ex : data) freq[ex.label]++;
    
    int majority = data[0].label;
    int maxCount = 0;
    for (const auto& p : freq) {
        if (p.second > maxCount) {
            maxCount = p.second;
            majority = p.first;
        }
    }
    return majority;
}



class DecisionTree {
public:
    Node* root;
    Criterion criterion;
    int maxDepth;
    const Dataset* datasetPtr;

    DecisionTree(Criterion crit, int maxDepth)
        : root(nullptr), criterion(crit), maxDepth(maxDepth), datasetPtr(nullptr) {}

    ~DecisionTree() {
        deleteTree(root);
    }

    void train(const Dataset& ds) {
        datasetPtr = &ds;
        int numFeatures = ds.numFeatures();
        vector<int> attrIdxs(numFeatures);
        for (int i = 0; i < numFeatures; ++i) {
            attrIdxs[i] = i;
        }
        root = buildTree(ds.data, attrIdxs, 1);
    }

    int predict(const Example& ex) const {
        if (root == nullptr) return -1;
        Node* n = root;
        while (!n->isLeaf) {
            if (n->isNumericSplit) {
                double val = ex.numFeatures[n->splitAttribute];
                if (val <= n->splitThreshold) {
                    if (n->left) n = n->left;
                    else return n->classLabel;
                } else {
                    if (n->right) n = n->right;
                    else return n->classLabel;
                }
            } else {
                int val = ex.catFeatures[n->splitAttribute];
                if (n->children.count(val)) {
                    n = n->children.at(val);
                } else {
                    return n->classLabel;
                }
            }
        }
        return n->classLabel;
    }

    double accuracy(const Dataset& testSet) const {
        if (testSet.size() == 0) return 0.0;
        int correct = 0;
        for (const auto& ex : testSet.data) {
            int predictedLabel = predict(ex);
            if (predictedLabel == ex.label) {
                correct++;
            }
        }
        return static_cast<double>(correct) / testSet.size();
    }

    int countNodes() const {
        if (root == nullptr) return 0;
        return countNodes(root);
    }

    int treeDepth() const {
        if (root == nullptr) return 0;
        return treeDepth(root);
    }

private:
    Node* buildTree(const vector<Example>& data, const vector<int>& attrIdx, int depth) {
        if (data.empty()) {
            return new Node(0);
        }
        
        // Check if same label
        map<int, int> frequency;
        for (const auto& ex : data) {
            frequency[ex.label]++;
        }
        if (frequency.size() == 1) {
            return new Node(data[0].label);
        }
        
        if (attrIdx.empty() || (maxDepth > 0 && depth >= maxDepth)) {
            int majorityLabel = majorityLabelOf(data);
            return new Node(majorityLabel);
        }

        
        double bestScore = -1e9;
        int bestAttr = -1;
        double bestThresh = 0.0;
        bool bestIsNumeric = false;
        vector<Example> bestLeft, bestRight;
        map<int, vector<Example>> bestSplits;
        
        for (int idx : attrIdx) {
            if (datasetPtr->isNumericFeature[idx]) {
                // limit threshold
                set<double> uniqueVals;
                for (const auto& ex : data) {
                    uniqueVals.insert(ex.numFeatures[idx]);
                }
                
                if (uniqueVals.size() < 2) continue;
                
                vector<double> vals(uniqueVals.begin(), uniqueVals.end());
                int maxTests = min(10, (int)vals.size() - 1); // Limit to 10 thresholds max
                
                for (int i = 1; i <= maxTests; ++i) {
                    int pos = (i * (vals.size() - 1)) / maxTests;
                    double thresh = (vals[pos] + vals[pos + 1]) / 2.0;
                    
                    vector<Example> left, right;
                    for (const auto& ex : data) {
                        if (ex.numFeatures[idx] <= thresh) {
                            left.push_back(ex);
                        } else {
                            right.push_back(ex);
                        }
                    }
                    
                    if (left.empty() || right.empty()) continue;
                    
                    double score = 0;
                    switch (criterion) {
                        case IG: {
                            double totalEntropy = entropy(data);
                            double weightedEntropy = (left.size() * entropy(left) + right.size() * entropy(right)) / data.size();
                            score = totalEntropy - weightedEntropy;
                            break;
                        }
                        case IGR: {
                            double gain = entropy(data) - (left.size() * entropy(left) + right.size() * entropy(right)) / data.size();
                            double splitInfo = 0.0;
                            double pL = (double)left.size() / data.size();
                            double pR = (double)right.size() / data.size();
                            if (pL > 0) splitInfo -= pL * log2(pL);
                            if (pR > 0) splitInfo -= pR * log2(pR);
                            if (splitInfo == 0) score = 0;
                            else score = gain / splitInfo;
                            break;
                        }
                        case NWIG: {
                            double gain = entropy(data) - (left.size() * entropy(left) + right.size() * entropy(right)) / data.size();
                            int k = 2;
                            int S = data.size();
                            double nwig = (gain / log2(k)) * (1.0 - (k - 1.0) / S);
                            score = nwig;
                            break;
                        }
                    }
                    
                    if (score > bestScore) {
                        bestScore = score;
                        bestAttr = idx;
                        bestThresh = thresh;
                        bestIsNumeric = true;
                        bestLeft = left;
                        bestRight = right;
                    }
                }
            } else {
                // Categorical feature
                double score = 0;
                switch (criterion) {
                    case IG:
                        score = InformationGain(data, idx, *datasetPtr);
                        break;
                    case IGR:
                        score = InformationGainRatio(data, idx, *datasetPtr);
                        break;
                    case NWIG:
                        score = NormalizedWeightedInformationGain(data, idx, *datasetPtr);
                        break;
                }
                
                if (score > bestScore) {
                    bestScore = score;
                    bestAttr = idx;
                    bestIsNumeric = false;
                    bestSplits.clear();
                    for (const auto& ex : data) {
                        bestSplits[ex.catFeatures[idx]].push_back(ex);
                    }
                }
            }
        }
        
        if (bestAttr == -1 || bestScore <= 0) {
            return new Node(majorityLabelOf(data));
        }
        
        Node* node = new Node();
        node->splitAttribute = bestAttr;
        node->isLeaf = false;
        node->classLabel = majorityLabelOf(data);
        node->isNumericSplit = bestIsNumeric;
        
        if (bestIsNumeric) {
            node->splitThreshold = bestThresh;
            if (!bestLeft.empty()) {
                node->left = buildTree(bestLeft, attrIdx, depth + 1);
            }
            if (!bestRight.empty()) {
                node->right = buildTree(bestRight, attrIdx, depth + 1);
            }
        } else {
            vector<int> newAttrIdx;
            newAttrIdx.reserve(attrIdx.size() - 1);
            for (int idx : attrIdx) {
                if (idx != bestAttr) newAttrIdx.push_back(idx);
            }
            
            for (const auto& pair : bestSplits) {
                if (!pair.second.empty()) {
                    node->children[pair.first] = buildTree(pair.second, newAttrIdx, depth + 1);
                }
            }
        }
        
        return node;
    }

    void deleteTree(Node* node) {
        if (node != nullptr) {
            delete node;
        }
    }

    int countNodes(Node* node) const {
        if (node == nullptr) return 0;
        int count = 1;
        for (const auto& pair : node->children) {
            count += countNodes(pair.second);
        }
        if (node->left) count += countNodes(node->left);
        if (node->right) count += countNodes(node->right);
        return count;
    }

    int treeDepth(Node* node) const {
        if (node == nullptr) return 0;
        int maxDepth = 0;
        for (const auto& pair : node->children) {
            maxDepth = max(maxDepth, treeDepth(pair.second));
        }
        if (node->left) maxDepth = max(maxDepth, treeDepth(node->left));
        if (node->right) maxDepth = max(maxDepth, treeDepth(node->right));
        return maxDepth + 1;
    }
};

int main(int argc, char* argv[]) {
    if (argc != 3) {
        cout << "Usage: ./decision_tree <criterion> <maxDepth>\n";
        cout << "Criterion: IG, IGR, or NWIG\n";
        cout << "MaxDepth: positive integer or 0 for no limit\n";
        return 1;
    }
    
    string criterionStr = argv[1];
    int maxDepth = stoi(argv[2]);
    
    Criterion criterion;
    if (criterionStr == "IG") {
        criterion = IG;
    } else if (criterionStr == "IGR") {
        criterion = IGR;
    } else if (criterionStr == "NWIG") {
        criterion = NWIG;
    } else {
        cout << "Invalid criterion. Use IG, IGR, or NWIG.\n";
        return 1;
    }
    
    string filename = "Datasets/adult.data";
    bool hasHeader = false;
    //string filename = "Datasets/Iris.csv"; 
    //bool hasHeader = true;
    
    Dataset dataset;
    dataset.readCSV(filename, hasHeader);
    
    if (dataset.size() == 0) {
        cout << "No data loaded. Please check the file path and format.\n";
        return 1;
    }
    
    int runs = 20;  
    double totalAccuracy = 0.0;
    int totalNodes = 0, totalDepth = 0;
    
    cout << "Running " << runs << " experiments with criterion: " << criterionStr 
         << ", max depth: " << maxDepth << endl;
    
    for (int r = 0; r < runs; ++r) {
        auto splitted = dataset.split(0.8);
        Dataset trainSet = splitted.first;
        Dataset testSet = splitted.second;
        
        DecisionTree tree(criterion, maxDepth);
        tree.train(trainSet);
        
        double accuracy = tree.accuracy(testSet);
        totalAccuracy += accuracy;
        totalNodes += tree.countNodes();
        totalDepth += tree.treeDepth();
        
        cout << "Run " << (r + 1) << ": Accuracy = " << accuracy * 100 << "%, "
             << "Nodes = " << tree.countNodes() << ", "
             << "Depth = " << tree.treeDepth() << endl;
    }
    
    cout << "\n=== FINAL RESULTS ===" << endl;
    cout << "Average accuracy: " << (totalAccuracy / runs) * 100 << "%" << endl;
    cout << "Average nodes: " << totalNodes / runs << endl;
    cout << "Average depth: " << totalDepth / runs << endl;
    
    cout << "\nLabel mapping (int -> string):" << endl;
    for (int i = 0; i < (int)dataset.labelEncoder.idToName.size(); ++i) {
        cout << "  " << i << " -> " << dataset.labelEncoder.decode(i) << endl;
    }
    
    return 0;
}
