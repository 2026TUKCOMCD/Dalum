from PIL import Image
import requests
from io import BytesIO
from recommender.style_classifier import StyleClassifier

url = "https://image.msscdn.net/thumbnails/images/goods_img/20250808/5306800/5306800_17560943469578_big.jpg?w=1200"
image = Image.open(BytesIO(requests.get(url).content))

classifier = StyleClassifier()
print(classifier.classify_with_scores(image))