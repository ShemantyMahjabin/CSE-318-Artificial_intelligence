import random
from typing import List,Tuple
import sys
import csv
import time
import os
import re


class Graph:
    def __init__(self,numvertices:int):
        self.numvertices=numvertices
        self.edges=[]
    def addEdge(self,src:int,des:int,weight:float):
        self.edges.append((src,des,weight))

class solutionpair:
    def __init__(self,X:List[int],Y:List[int],weights:List[List[float]],graph:Graph):
        self.X=X
        self.Y=Y
        self.weights=weights
        self.graph=graph
        self.num_iteration=0

    def get_sigmaS(self,v:int):
        return sum(self.weights[v][u] for u in self.Y)
    def get_sigmaS_prime(self,v:int):
        return sum(self.weights[v][u] for u in self.X)
    def is_in_S(self,v:int)->bool:
        return v in self.X
    def is_in_S_prime(self,v:int)->bool:
        return v in self.Y
    def remove_from_S(self,v:int):
        self.X.remove(v)
    def add_to_S(self,v:int):
        self.X.append(v)
    def remove_from_S_prime(self,v:int):
        self.Y.remove(v)
    def add_to_S_prime(self,v:int):
        self.Y.append(v)
    def get_S(self)->List[int]:
        return self.X
    def get_S_prime(self)->List[int]:
        return self.Y
    def compute_cut_weight(self) -> float:
        total = 0
        Xset, Yset = set(self.X), set(self.Y)
        for u, v, w in self.graph.edges:
            if (u in Xset and v in Yset) or (u in Yset and v in Xset):
                total += w
        return total




def find_min_weight(weights:List[List[float]])->float:
    return min(min(row) for row in weights)
def find_max_weight(weights:List[List[float]])->float:
    return max(max(row) for row in weights)
def find_largest_edge(graph:Graph,weights:List[List[float]])->Tuple[int,int,float]:
    maxweight=float('-inf')
    laregest_weight=None
    for i in range(1,graph.numvertices+1):
        for j in range(i+1,graph.numvertices+1):
            if weights[i][j]>maxweight:
                maxweight=weights[i][j]
                laregest_weight=(i,j,maxweight)
    return laregest_weight

def Greedy_max_cut(graph: Graph, weights: List[List[float]]) -> solutionpair:
    u, v, _ = find_largest_edge(graph, weights)
    sol = solutionpair([u], [v], weights, graph)
    v_prime = {v_ for v_ in range(1, graph.numvertices + 1) if v_ not in (u, v)}
    for z in v_prime:
        wX = sol.get_sigmaS(z)
        wY = sol.get_sigmaS_prime(z)
        if wX > wY:
            sol.add_to_S(z)
        else:
            sol.add_to_S_prime(z)
    return sol

def RandomizedMaxCut(graph:Graph,weights:List[List[float]],n:int)->float:
    total_cut_weight = 0.0
    for _ in range(n):
        X,Y=set(),set()
        for v in range(1,graph.numvertices+1):
            if random.random()>=0.5:
                X.add(v)
            else:
                Y.add(v)
        sol = solutionpair(X, Y, weights,graph)
        cut_weight = sol.compute_cut_weight()
        total_cut_weight += cut_weight

    average_cut_weight = total_cut_weight / n
    return average_cut_weight

def semi_greedy_max_cut(graph:Graph,weights:List[List[float]])->solutionpair:
    alpha=random.random()
    Wmin=find_min_weight(weights)
    Wmax=find_max_weight(weights)
    meu=Wmin+alpha*(Wmax-Wmin)
    RCLe=[edge for edge in graph.edges if weights[edge[0]][edge[1]]>=meu]
    random_edge=random.choice(RCLe)
    solution=solutionpair([random_edge[0]],[random_edge[1]],weights,graph)
    all_vertices_set=set(range(1,graph.numvertices+1))
    while len(solution.get_S())+len(solution.get_S_prime())<graph.numvertices:
        VPrime=all_vertices_set-set(solution.get_S())-set(solution.get_S_prime())
        sigmaX={v: solution.get_sigmaS(v) for v in VPrime}
        sigmaY={v:solution.get_sigmaS_prime(v) for v in VPrime}
        newWmin=min(min(sigmaX.values()),min(sigmaY.values()))
        newWmax=max(max(sigmaX.values()),max(sigmaY.values()))
        newMeu=newWmin+alpha*(newWmax-newWmin)
        RCLv=[v for v in VPrime if max(sigmaX[v],sigmaY[v])>=newMeu]
        vstar=random.choice(RCLv)
        if sigmaX[vstar]>sigmaY[vstar]:
            solution.add_to_S(vstar)
        else:
            solution.add_to_S_prime(vstar)
    return solution

def local_search_maxcut(initialsolution:solutionpair,weights:List[List[float]], max_iters=1000)->solutionpair:
    change=True
    initialsolution.num_iteration=0
    while(change) and initialsolution.num_iteration < max_iters:
        change=False
        initialsolution.num_iteration+=1
        for v in range(1,len(weights)):
            sigmaS=initialsolution.get_sigmaS(v)
            sigmaSprime=initialsolution.get_sigmaS_prime(v)
            if initialsolution.is_in_S(v) and sigmaSprime-sigmaS>0:
                initialsolution.remove_from_S(v)
                initialsolution.add_to_S_prime(v)
                change=True

            elif initialsolution.is_in_S_prime(v) and sigmaS-sigmaSprime>0:
                initialsolution.remove_from_S_prime(v)
                initialsolution.add_to_S(v)
                change=True
    return initialsolution
                



def main():
    input_dir = r"graph_GRASP\set2" 
    graph_files = [f for f in os.listdir(input_dir) if f.endswith(".rud")]

    def natural_key(text):
        return [int(s) if s.isdigit() else s.lower() for s in re.split(r'(\d+)', text)]

    graph_files.sort(key=natural_key)

    output_file = "result2.csv"


    with open(output_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
        "Problem", "", "",  
        "Constructive Algorithm", "", "", 
        "Local Search Algorithm", "",  
        "GRASP Algorithm", "",  
        "Known Best Solution"
    ])


        writer.writerow([
            "Name", "|V| or n", "|E| or m",
            "Simple Randomized", "Simple Greedy", "Semi Greedy",
            "No of iterations", "Best Value",
            "No of iterations", "Best Value",
            "Value"
        ])

    for filename in graph_files:
        filepath = os.path.join(input_dir, filename)
        with open(filepath, "r") as f:
            lines = f.read().strip().split("\n")

        v, e = map(int, lines[0].split())
        graph = Graph(v)
        weights = [[0.0] * (v + 1) for _ in range(v + 1)]
#       lines = sys.stdin.read().strip().split("\n")
#       v, e = map(int, lines[0].split())

#       graph = Graph(v)
#       weights = [[0.0] * (v + 1) for _ in range(v + 1)]
        for i in range(1, e + 1):
            u, v_, w = lines[i].split()
            u = int(u)
            v_ = int(v_)
            w = float(w)
            graph.addEdge(u, v_, w)
            weights[u][v_] = w
            weights[v_][u] = w  

      
        greedy_sol = Greedy_max_cut(graph, weights)
        greedy_cut = greedy_sol.compute_cut_weight()
#        print("In greedy approach value is:", greedy_cut)
        rand_weight = RandomizedMaxCut(graph, weights, 10)
        #rand_weight = rand_sol.compute_cut_weight()
        semi_solution = semi_greedy_max_cut(graph, weights)
        semi_weight_cut = semi_solution.compute_cut_weight()
        local_solution = local_search_maxcut(semi_solution, weights, max_iters=1000)
        local_weight_cut = local_solution.compute_cut_weight()
        numiteration=local_solution.num_iteration


        #rand_total, semi_total, local_total = 0.0, 0.0, 0.0
        #iter_total = 0
        w_best = float('-inf')
        trials = 10

        for _ in range(trials):
            # rand_sol = RandomizedMaxCut(graph, weights, 1)
            # rand_weight = rand_sol.compute_cut_weight()
            # rand_total += rand_weight
            #print("SHEM")
            semi_sol = semi_greedy_max_cut(graph, weights)
            #semi_weight = semi_sol.compute_cut_weight()
            #semi_total += semi_weight

            local_sol = local_search_maxcut(semi_sol, weights, max_iters=1000)
            local_weight = local_sol.compute_cut_weight()
            #local_total += local_weight
            #iter_total += local_sol.num_iteration

            if local_weight > w_best:
                w_best = local_weight
        




#       print("In purely Randomized approach average value is:", rand_weight)
#       print("In SemiGreedy approach average value is:", semi_weight_cut)
#       print("In local Search approach average iterations:", numiteration)
#       print("In local Search approach average value is:", local_weight_cut)
#       print("GRASP Best Weight:", w_best)
        
        print(f"Finished: {filename}")
        print(f"Greedy: {greedy_cut}")
        print(f"Randomized : {int(rand_weight)}")
        print(f"Semi-Greedy : {semi_weight_cut}")
        print(f"Local Search : {local_weight_cut}")
        print(f"Local Iter : {numiteration}")
        print(f"GRASP Best: {w_best}")
        print("-" * 60)

        
        with open(output_file, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                os.path.splitext(filename)[0], v, e,
                f"{int(rand_weight)}", f"{greedy_cut}", f"{semi_weight_cut}",
                f"{numiteration}", f"{local_weight_cut}",
                trials, f"{w_best}",
                "-"
    ])

if __name__ == "__main__":
    main()


