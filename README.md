# PST-KDD-2024-Heart-Rank8

## 基本环境
- Python 3.8.13
- PyTorch 2.0.1+cu117
- CUDA 11.7
- NVADIA RTX3090 24G
## 安装依赖包：
```bash
pip install -r requirements.txt
```

## 下载预训练模型并放在bert_models目录下
scibert: https://huggingface.co/allenai/scibert_scivocab_uncased/tree/main 

deberta: https://huggingface.co/microsoft/deberta-v3-base/tree/main

roberta: https://huggingface.co/allenai/dsp_roberta_base_dapt_cs_tapt_sciie_3219/tree/main

## 目录结构
```
--main
  |--data  
    |--PST
      |--paper-xml  ## 存放数据
      |--DBLP-Citation-network-V15.json  ## 官方允许使用的 dblp 数据
      |--paper_source_trace_train_ans.json
      |--paper_source_trace_valid_wo_ans.json
      |--submission_example_valid.json
      |--paper_source_trace_test_wo_ans.json
      |--submission_example_test.json
  |--bert_models  ## 存放预训练权重
      |--deberta_v3_base
      |--dsp_roberta_base_dapt_cs_tapt_sciie_3219
      |--scibert_scivocab_uncased
  |--rf  ## 存放树模型训练代码
      |--process_kddcup_data_test.py
      |--model_rf_test.py
  |--out  #模型输出结果保存，共六个模型
      |--kddcup
        |--deberta-base
        |--roberta-base
        |--scibert
        |--rf
  |--submit  ## 最终提交文件存放处

  |--deberta_training.ipynb  ## training后缀为训练程序
  |--deberta_test_inference.ipynb  ## inference后缀为推理程序

  |--roberta_0fold_training.ipynb
  |--roberta_0fold_test_inference.ipynb

  |--roberta_3fold_training.ipynb
  |--roberta_3fold_test_inference.ipynb

  |--scibert_0fold_training.ipynb
  |--scibert_0fold_test_inference.ipynb

  |--scibert_4fold_training.ipynb
  |--scibert_4fold_test_inference.ipynb

  |--lgb_prepare_data.ipynb  # 准备数据
  |--lgb_train.ipynb  # LGB训练
  |--lgb_inference.ipynb  # LGB推理，推理前必须先运行lgb_prepare_data.ipynb !!! 

  |--merge.ipynb # 融合模型
```

## 数据集下载
在[比赛官网](https://www.biendata.xyz/competition/pst_kdd_2024/data/)下载数据集，存放路径如目录结构所示。

## 训练及推理过程
运行六个模型的训练代码：
 - deberta_training.ipynb
 - roberta_0fold_training.ipynb
 - roberta_3fold_training.ipynb
 - scibert_0fold_training.ipynb
 - scibert_4fold_training.ipynb
 - lgb_train.ipynb

之后运行相应的inference代码。

最后运行merge.ipynb生成最终的提交文件（保存在submit目录下）。

## model_checkpoint下载
链接：https://pan.baidu.com/s/1yh0opO7gUdDPWyC8TrAiIA?pwd=sqed 
提取码：sqed

解压后直接覆盖out文件夹

然后运行相关的inference代码（运行前请确保数据路径正确，并且lgb_inference.ipynb需要先运行lgb_prepare_data.ipynb）

## 有任何问题请联系：1206392134@qq.com
