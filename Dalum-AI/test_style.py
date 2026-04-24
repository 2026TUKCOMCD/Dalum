from PIL import Image
import requests
from io import BytesIO
from recommender.style_classifier import StyleClassifier

url = "https://image.msscdn.net/thumbnails/images/goods_img/20230801/3439140/3439140_16921611517541_big.jpg?w=1200"
image = Image.open(BytesIO(requests.get(url).content))

classifier = StyleClassifier()
print(classifier.classify_with_scores(image))