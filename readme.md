# 操作說明
## 0. 安裝
```shell
pip install -r requirements.txt
```

## 1. 編輯 `evaluation.py`, `pipeline_settings.py`
> Note: 現階段仍需要手動修改、複製所有Dockerfile。SDK的自動更新也還沒有完成。
* ### 如何編寫 `evaluation.py`？
  * **不要在編輯區域外寫程式！否則會直接被忽略**
  * **不要變動`### USER IMPORT START ###`之類的字樣，否則會無法轉換**
  * 我們只會自動`import mitlab`的SDK檔案，其餘的需要加入在user import start的欄位中
  * 您可以直接利用 `pretrain_model_file_path` 變數讀取 Pretrained Model 的路徑，利用 `training_dataset_file_path` 變數讀取 Training Dataset的路徑。
  * 回傳指標時，請使用`dict`的資料型態回傳，並將變數名稱紀錄於`pipeline_settings.json`中。
* ### 如何編寫 `pipeline_settings.py`？
  * 這個檔案分成兩個部分，一般只需要動到 `basic` 的內容就好。
  * `basic` 欄位說明：
    * `input_dataset_filename`: 資料集檔案在壓縮檔中的名稱 (需要有副檔名)
    * `input_model_filename`: 模型檔案在壓縮檔中的名稱 (需要有副檔名)
    * `output_metrics_variable`: Metrics回傳的變數 (詳情請見`evaluation.py`的說明)
    * `output_metrics_type`: 輸出的模型指標類別 (accuracy, loss等等，詳情請見mitlab SDK的`metrics`部分。)
  * `advanced` 部分正常情況下應該不太需要設定，如需更動，請參考**kubeflow python sdk**。
## 2. 執行 `Py2Pipeline.py`
## 3. 上傳`Output`資料夾的輸出檔