import os
from os.path import join
import numpy as np
from tqdm import tqdm
from bs4 import BeautifulSoup
import set_param
import pickle
from sklearn import svm
from sklearn.ensemble import RandomForestClassifier
import json
from sklearn.metrics import average_precision_score
import warnings
from sklearn.linear_model import LogisticRegression
from fuzzywuzzy import fuzz

warnings.filterwarnings("ignore")

import utils 
import settings

## add 
import lightgbm as lgb
from lightgbm import LGBMClassifier



def calculate_TPFN(pre_result, label):
    TP, TN, FP, FN = 0, 0, 0, 0
    total = len(label)
    for item, jtem in zip(pre_result, label):
        if item == 1 and jtem == 1:
            TP += 1
        elif item == 0 and jtem == 1:
            FP += 1
        elif item == 1 and jtem == 0:
            FN += 1
        else:
            TN += 1
    print("Accuracy:", (TP + TN) / total)
    print("Precision:", TP / (TP + FP))
    print("Recall:", TP / (TP + FN))


def train_classifier(seed=42, model_type = "RandomForest"):
    params = set_param.Args(model_type)
    feature_dir = join(settings.OUT_DIR, "kddcup", "rf")
    data = np.loadtxt(open(join(feature_dir, "train_data.csv"), "rb"), delimiter=",")
    label = np.loadtxt(open(join(feature_dir, "train_label.csv"), "rb"), delimiter=",")
    if model_type == "SVM":
        model = svm.SVC(C=params.C, kernel=params.kernel, verbose=params.verbose, max_iter=params.max_iter,
                        tol=params.tol, probability=True)
    elif model_type == "RandomForest":
        model = RandomForestClassifier(n_estimators=params.n_estimators)
    elif model_type == "LR":
        model = LogisticRegression(solver=params.solver, multi_class=params.multi_class)
    elif model_type == "LGB": 
        # seed = 42
        lgb_params = {
            'learning_rate': 0.01,
            'boosting_type': 'gbdt',
            'objective': 'binary',  # mse mape
            'metric': ['auc', 'binary_logloss'],
            # 'max_depth': 6,
            'num_leaves': 64,
            'verbose': -1,
            'feature_fraction': 0.8,
            'bagging_fraction': 0.8,
            'bagging_freq': 5,

            'lambda_l1': 0.05,
            'lambda_l2': 0.1,

            'n_jobs': -1,
            'verbose': -1,
            "device_type": "cpu",
            'feature_fraction_seed': seed,
            'bagging_seed': seed,
            'seed': seed,
        }
        model = LGBMClassifier(**lgb_params)
        
    ## 产生索引 
    indices = np.arange(len(data))
    if seed > 100:  ## 观察指标发现，0，42，seed 不打乱好
        ## 随机打乱
        np.random.shuffle(indices)
    
    ## 模型数据训练 
    model.fit(data[indices], label[indices])
    save_model = pickle.dumps(model)
    # os.makedirs("saved_model", exist_ok=True)
    write_file = open(join(feature_dir, "{}_{}.pkl".format(model_type, seed)), 'wb')
    write_file.write(save_model)
    write_file.close()
    pre_result = model.predict(data)
    calculate_TPFN(pre_result, label)  


def eval_classifier(seed=42, model_type="RandomForest", role="test"):
    feature_dir = join(settings.OUT_DIR, "kddcup", "rf")
    with open(join(feature_dir, f"{role}_data.json")) as read_file:
        eval_features = json.load(read_file)

    data_dir = join(settings.DATA_TRACE_DIR, "PST") 
    papers = utils.load_json(data_dir, "paper_source_trace_test_wo_ans.json")
    paper_info_more = utils.load_json(data_dir, "paper_info_hit_from_dblp.json")


    with open(join(feature_dir, "{}_{}.pkl".format(model_type, seed)), 'rb') as read_file:
        model = pickle.loads(read_file.read())

    xml_dir = join(data_dir, "paper-xml")
    sub_dict = {}
    sub_example_dict = utils.load_json(data_dir, "submission_example_test.json")

    for paper in tqdm(papers):
        cur_pid = paper["_id"]
        file = join(xml_dir, cur_pid + ".xml")
        f = open(file, encoding='utf-8')
        xml = f.read()
        bs = BeautifulSoup(xml, "xml")
        f.close()

        ref_ids = paper.get("references", [])
        cur_title_to_pid = {}
        for ref_id in ref_ids:
            if ref_id in paper_info_more:
                cur_title_to_pid[paper_info_more[ref_id]["title"].lower()] = ref_id

        references = bs.find_all("biblStruct")
        bid_to_title = {}
        n_refs = 0
        cur_title_to_b_idx = {}
        for ref in references:
            if "xml:id" not in ref.attrs:
                continue
            bid = ref.attrs["xml:id"]
            if ref.analytic is None:
                continue
            if ref.analytic.title is None:
                continue
            bid_to_title[bid] = ref.analytic.title.text.lower()
            b_idx = int(bid[1:]) + 1
            cur_title_to_b_idx[ref.analytic.title.text.lower()] = b_idx - 1
            if b_idx > n_refs:
                n_refs = b_idx

        assert len(sub_example_dict[cur_pid]) == n_refs
        y_score = [0] * n_refs
        cur_feature = eval_features[cur_pid]

        for r_idx, ref_id in enumerate(ref_ids):
            if ref_id not in paper_info_more:
                continue
            cur_title = paper_info_more[ref_id].get("title", "").lower()
            if len(cur_title) == 0:
                continue
            cur_ref_feature = cur_feature[r_idx]
            if len(cur_ref_feature) == 0:
                continue
            cur_b_idx = None
            for b_title in cur_title_to_b_idx:
                cur_sim = fuzz.ratio(cur_title, b_title)
                if cur_sim >= 75:
                    cur_b_idx = cur_title_to_b_idx[b_title]
                    break
            if cur_b_idx is None:
                continue
            cur_prob = model.predict_proba([cur_ref_feature])[0][1]
            y_score[cur_b_idx] = float(cur_prob)
        
        # print(y_score)
        sub_dict[cur_pid] = y_score
    
    utils.dump_json(sub_dict, feature_dir, f"{role}_sub_{model_type}_{seed}.json")


if __name__ == "__main__":
    ## SVM
    ## RandomForest
    ## LR
    ## LGB
    global model_type
    model_type = 'LGB'
    for seed in [0, 42, 6565, 987456]:
        print('seed >>> ', seed)
        train_classifier(seed, model_type=model_type)
        eval_classifier(seed, model_type, "test") 