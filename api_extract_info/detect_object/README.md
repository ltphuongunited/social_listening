<h1>Detect objection</h1>

1. **Data**:

Dữ liệu chứa các hình ảnh với 20 loại đối tượng khác nhau.

```
{'aeroplane', 'bicycle', 'bird', 'boat', 'bottle', 'bus', 'car', 'cat', 'chair', 'cow', 'diningtable', 'dog', 'horse', 'motorbike', 'person', 'pottedplant', 'sheep', 'sofa', 'train', 'tvmonitor'}
```
- [2007 _trainval_](http://host.robots.ox.ac.uk/pascal/VOC/voc2007/VOCtrainval_06-Nov-2007.tar) (460MB)

- [2012 _trainval_](http://host.robots.ox.ac.uk/pascal/VOC/voc2012/VOCtrainval_11-May-2012.tar) (2GB)

- [2007 _test_](http://host.robots.ox.ac.uk/pascal/VOC/voc2007/VOCtest_06-Nov-2007.tar) (451MB)

2.**Training**:

- Sau khi tải data chạy file ***create_data_list.py*** để tạo file json đường dẫn tới ảnh và bounding-box, label
- Chạy lệnh ***python train.py*** để train
```
python train.py
```

3. **Evaluation**: File ***eval.py***

4. **Detect**:

File ***detect.py*** dùng để phát hiện đối tượng
- Hàm ***detect()*** input là ảnh và các tham số, output là list cái đối tượng có trong ảnh
- Hàm ***detect_vehicle()*** duyệt tất cả các tấm ảnh của **user** và trả về list các ảnh có ô tô và mô tô

Code được tham khảo tại link: https://github.com/sgrvinod/a-PyTorch-Tutorial-to-Object-Detection
