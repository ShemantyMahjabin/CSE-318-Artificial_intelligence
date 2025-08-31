#include <bits/stdc++.h>
using namespace std;



using board= vector<vector<int>>;
int k,n;
board goalBoard;


class tilesPosition{
    public:
        int r,c;
};

vector<tilesPosition>goalPositions;

int getInvCount(const vector<int>& oneDarray) {
    int inversions = 0;
    for (int i = 0; i < oneDarray.size(); ++i) {
        if (oneDarray[i] == k * k) continue; 
        for (int j = i + 1; j < oneDarray.size(); ++j) {
            if (oneDarray[j] == k * k) continue; 
            if (oneDarray[i] > oneDarray[j]) {
                ++inversions;
            }
        }
    }
    return inversions;
}
bool Solvable(const board& Board){
    vector<int> oneDarray;
    int blanktilesrow = -1;
    for(int i = 0; i < k; ++i){
        for(int j = 0; j < k; ++j){
            int x = Board[i][j];
            if(x == k * k){
                blanktilesrow = i; 
            }
            oneDarray.push_back(x);
        }
    }

    int inversions = getInvCount(oneDarray);

    if(k % 2 == 1){
        return inversions % 2 == 0;
    } else {
        int blankRowFromBottom = k - blanktilesrow; 
        return (inversions + blankRowFromBottom) % 2 == 1;
    }
}
int Hamming(const board& Board){
    int c=0;
    for(int i=0;i<k;i++){
        for(int j=0;j<k;j++){
            int x=Board[i][j];
            if(x==k*k) continue;
            tilesPosition goal=goalPositions[x-1];
            if(goal.r!=i || goal.c!=j){
                ++c;
            }
        }
    }
    return c;
}

int Manhattan(const board& Board){
    int d=0;
    for(int i=0;i<k;++i){
        for(int j=0;j<k;++j){
            int x=Board[i][j];
            if(x==k*k) continue;
            tilesPosition goal=goalPositions[x-1];
            d+=abs(i-goal.r)+abs(j-goal.c);
        }
    }
    return d;
}


int Euclidean(const board& Board) {
    double d = 0.0;
    for(int i=0; i<k; i++){
        for(int j=0; j<k; j++){
            int x = Board[i][j];
            if(x == k*k) continue;
            tilesPosition goal = goalPositions[x-1];
            d += sqrt(pow(i - goal.r, 2) + pow(j - goal.c, 2));
        }
    }
    return static_cast<int>(round(d));
}

int LinearConflict(const board& Board){
    int manhattandistance=Manhattan(Board);
    int conflict=0;
    
    for (int i = 0; i < k; ++i) {
        for (int j = 0; j < k - 1; ++j) {
            for (int l = j + 1; l < k; ++l) {
                int p=Board[i][j];
                int q=Board[i][l];
                if(p==k*k || q==k*k) continue;
                tilesPosition tj=goalPositions[p-1];
                tilesPosition tk=goalPositions[q-1];
                if (tj.r == i && tk.r == i && tj.c > tk.c)
                    conflict++;
            }
        }
    }
    
    for (int j = 0; j < k; ++j) {
        for (int i = 0; i < k - 1; ++i) {
            for (int l = i + 1; l < k; ++l) {
                int p=Board[i][j];
                int q=Board[l][j];
                if(p==k*k || q==k*k) continue;
                tilesPosition tj=goalPositions[p-1];
                tilesPosition tk=goalPositions[q-1];
                if (tj.c == j && tk.c == j && tj.r > tk.r)
                    conflict++;
            }
        }
    }
    int linearConflictHeuristic= manhattandistance+2*conflict;
    return linearConflictHeuristic;

}


tilesPosition find_pos(const board& Board,int v){
    for(int i=0;i<k;i++){
        for(int j=0;j<k;j++){
            if(Board[i][j]==v){
                return {i,j};
            }
        }
    }
    return {-1,-1};
}


class Node{
    public:
         board Board;
         int g,h;
         Node* parent;
         tilesPosition blank;

         Node(board b,int g_,int h_,Node* p=nullptr):Board(b),g(g_),h(h_),parent(p){
            blank=find_pos(Board,k*k);
         }

         int function() const{
            return g+h;
         }

         bool operator>(const Node& a)const{
            return function()>a.function() || (function()==a.function() && h>a.h );
         }
};

vector<board> Neighbourboard(Node* node){
    vector<board>neighboursboard;
    int directionrow[4]={-1,1,0,0};
    int directioncolumn[4]={0,0,-1,1};  
    //up->(-1,0),down->(1,0),left(0,-1),right->(0,1)
    for(int dir=0;dir<4;++dir){
        int nr=node->blank.r+directionrow[dir];
        int nc=node->blank.c+directioncolumn[dir];
        if(nr>=0 && nr<k && nc>=0 && nc<k){
            board b=node->Board;
            swap(b[node->blank.r][node->blank.c],b[nr][nc]);
            if(!node->parent || b!=node->parent->Board){
                neighboursboard.push_back(b);
            }
        }
    }
    return neighboursboard;
}


string boardToString(const board& Board) {
    string result = "";
    for (int i = 0; i < k; ++i)
        for (int j = 0; j < k; ++j)
            result += to_string(Board[i][j]) + ",";
    return result;
}


void puzzleSolver(board givenBoard,int(*heuristic)(const board&)){
    struct Compare{
        bool operator()(Node* a,Node* b){
            return *a>*b;
        }
    };
    int explored=0;
    int expanded=0;
    priority_queue<Node*,vector<Node*>,Compare>pq;
    unordered_set<string>visited;
    Node* start=new Node(givenBoard,0,heuristic(givenBoard));
    pq.push(start);
    explored++;
    
    while(!pq.empty()){
        Node* current=pq.top();
        pq.pop();
        expanded++;

        if(current->Board==goalBoard){
            vector<board>path;
            while(current){
                path.push_back(current->Board);
                current=current->parent;

            }
            reverse(path.begin(),path.end());

            for(int i=0;i<path.size();i++){
                board Board=path[i];
                for(int i=0;i<k;i++){
                    for(int j=0;j<k;j++){
                        if(Board[i][j]==k*k){
                            cout<<"0 ";
                        }else{
                            cout<<Board[i][j]<<" ";
                        }
                        
                    }
                    cout<<endl;
                }
                cout<<endl;
            }
            expanded--;

            cout << "Steps to solve: " << path.size() - 1 << endl;
            cout << "Nodes explored: " << explored << endl;
            cout << "Nodes expanded: " << expanded << endl;
            return;
            
        }


        string state = boardToString(current->Board);
        if (visited.count(state)) continue;
        visited.insert(state);

        vector<board> neighbours = Neighbourboard(current);
        //explored += neighbours.size();
        for (int i = 0; i < neighbours.size(); ++i) {
            string nextState = boardToString(neighbours[i]);
            if (!visited.count(nextState)) {
                Node* child = new Node(neighbours[i], current->g + 1, heuristic(neighbours[i]), current);
                pq.push(child); 
                explored++; 
    }
    
}
    }

    cout << "No solution found.\n";

}

int main()
{
    cout<<"Enter Grid size: ";
    cin>>k;
    n=k*k-1;

    board givenBoard(k,vector<int>(k));
    cout<<"Enter initial board(Use 0 for blank):\n";
    for (int i=0;i<k;i++){
        for(int j=0;j<k;j++){
            int x;
            cin>>x;
            if(x==0){
                x=k*k;
            }
            givenBoard[i][j]=x;

        }
    }


    goalBoard.resize(k,vector<int>(k));
    goalPositions.resize(n);
    
    int x=1;
    for(int i=0;i<k;i++){
        for(int j=0;j<k;j++){
            goalBoard[i][j]=x;
            if(x!=k*k){
                goalPositions[x-1]={i,j};
            }
            x++;
        }
    }

    

    if(!Solvable(givenBoard)){
        cout<<"Puzzle not Solvable.\n";
        return 0;
    }

    cout << "Choose a heuristic (manhattan/hamming/euclidean/linear): ";
    string choice;
    cin >> choice;
    int (*heuristic)(const board&);
    if (choice == "manhattan") heuristic = Manhattan;
    else if (choice == "hamming") heuristic = Hamming;
    else if (choice == "euclidean") heuristic = Euclidean;
    else heuristic = LinearConflict;

    puzzleSolver(givenBoard, heuristic);

    return 0;

}