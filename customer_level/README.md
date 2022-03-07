# Phân mức khách hàng
## Giới thiệu
Bài toán này phục vụ mục đích với những thông tin có được của khách hàng có thể dự đoán được khách hàng thuộc phân khúc nào: bình dân, trung lưu, thượng lưu. 
## Data
Dữ liệu được chia làm 2 tập train và test nằm trong thư mục **Data**.

Dữ liệu sử dụng bao gồm 7 thuộc tính: Chỗ ở, lương, bằng cấp, công việc, tuổi, thẻ tín dụng, phương tiện.

**- Chỗ ở** : chung cư, nhà thuê, phòng trọ, nhà riêng

**- Lương** : <10, 10-15, 15-20, 20-30, 30-40, >40

**- Bằng cấp** : phổ thông, cao đẳng, đại học, >đại học

**- Công việc** : hành chính, TX con người, công nhân, kỹ thuật, văn hoá nghệ thuật, TX tự nhiên

**- Tuổi** : <23, 23-30, 30-40, 40-50, > 50

**- Thẻ tín dụng** : có, không

**- Phương tiện** : ô tô, xe máy,phương tiện công cộng

## Cài package
```
pip install -r requirements.txt
```

## Training
- Multi Layer Perceptron và K-fold

Parameter: (batch_size, num_epochs, num_fold_steps, num_class)


- Random Forest

Parameter: n_estimatos

Chạy câu lệnh: 
```
python Main.py
```

## Model
Model được lưu trong thư mục **Model**







