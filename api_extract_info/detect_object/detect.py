import os
import sys
sys.path.insert(0, os.getcwd() + '/detect_object')
from torchvision import transforms
import sys
from detect_object.utils import *
from PIL import Image, ImageDraw, ImageFont


def detect(original_image, min_score, max_overlap, top_k):
    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    # Load model checkpoint
    checkpoint = './checkpoint_ssd300.pth.tar'
    checkpoint = torch.load(checkpoint)

    model = checkpoint['model']
    model = model.to(device)
    model.eval()

    # Transforms
    resize = transforms.Resize((300, 300))
    to_tensor = transforms.ToTensor()
    normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                    std=[0.229, 0.224, 0.225])
    """
    Detect objects in an image with a trained SSD300, and visualize the results.

    :param original_image: image, a PIL Image
    :param min_score: minimum threshold for a detected box to be considered a match for a certain class
    :param max_overlap: maximum overlap two boxes can have so that the one with the lower score is not suppressed via Non-Maximum Suppression (NMS)
    :param top_k: if there are a lot of resulting detection across all classes, keep only the top 'k'
    :param suppress: classes that you know for sure cannot be in the image or you do not want in the image, a list
    :return: annotated image, a PIL Image
    """

    # Transform
    image = normalize(to_tensor(resize(original_image)))

    # Move to default device
    image = image.to(device)

    # Forward prop.
    predicted_locs, predicted_scores = model(image.unsqueeze(0))

    # Detect objects in SSD output
    det_boxes, det_labels, det_scores = model.detect_objects(predicted_locs, predicted_scores, min_score=min_score,
                                                             max_overlap=max_overlap, top_k=top_k)
    # Move detections to the CPU
    det_boxes = det_boxes[0].to(device)

    # Transform to original image dimensions
    original_dims = torch.FloatTensor(
        [original_image.width, original_image.height, original_image.width, original_image.height]).unsqueeze(0)
    det_boxes = det_boxes.to(device) * original_dims.to(device)

    # Decode class integer labels
    det_labels = [rev_label_map[l] for l in det_labels[0].to(device).tolist()]

    return det_labels

   

def detect_vehicle(user_id):
    list_image = os.listdir('../user/'+ str(user_id) + '/img/')
    list_image_moto = []
    list_image_car = []
    
    for image in list_image:
        label = None
        original_image = Image.open('../user/'+ str(user_id) + '/img/' + str(image), mode='r')
        original_image = original_image.convert('RGB')
        label = detect(original_image, min_score=0.3, max_overlap=0.6, top_k=200)
        if 'motorbike' in label:
            list_image_moto.append(image.split('.')[0])
        elif 'car' in label:
            list_image_car.append(image.split('.')[0])
    
    return list_image_moto, list_image_car
