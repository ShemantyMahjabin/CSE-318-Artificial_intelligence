# CSE 318 — Offline (Decision Trees): Experimental Analysis

This repository contains an implementation and empirical study of **Decision Tree** classifiers with three splitting criteria:
- **Information Gain (IG)**
- **Information Gain Ratio (IGR)**
- **Normalized Weighted Information Gain (NWIG)**

It includes the **source code**, the **experimental report**, and the **result artifacts** . The code reads CSV datasets, handles mixed numeric/categorical features, builds decision trees with optional depth limits (pruning), and evaluates accuracy over repeated train/test splits. 

---

## 📌 What the Assignment Asked You To Do

**Goal:** Implement a Decision Tree learner that supports **both numeric and categorical attributes**, expose multiple **split criteria** (IG, IGR, NWIG), allow **depth-limited trees** (as a form of pre-pruning), and run a **systematic experimental analysis** on at least two datasets (e.g., **Iris** and **Adult**) to compare accuracy, model size (nodes), and depth under different criteria/depths. Summarize findings and draw conclusions about overfitting, pruning, and criterion behavior. 

**Core tasks (as reflected in this repo):**
1. **Parsing datasets (CSV)**, inferring which features are numeric vs. categorical; encoding string labels and categories to integers; skipping rows with missing tokens like `?`.
2. **Training Decision Trees** with:
   - Multiway splits for **categorical** attributes.
   - Binary threshold splits for **numeric** attributes (searching candidate thresholds).
3. **Split criteria**: implement **IG**, **IGR**, and **NWIG**; choose the best split per node using the selected criterion. 
4. **Optional depth limit** (maxDepth) to study pruning/overfitting trade-offs.
5. **Evaluation protocol**: repeat random **train/test splits** (e.g., 80/20) for multiple runs, report **average accuracy**, **average node count**, and **average depth**; present results for multiple `maxDepth` settings per criterion. 
6. **Analysis & Report**: discuss dataset characteristics, criterion behavior, pruning effects, and accuracy vs. complexity trade-offs, with tables/plots. 

---




