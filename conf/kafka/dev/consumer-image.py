from kafka import KafkaConsumer
from json import loads, dump
from time import sleep
import base64
import io
import os, sys
from PIL import Image

def get_script_path():
    return os.path.dirname(os.path.realpath(sys.argv[0]))

consumer = KafkaConsumer(
    'image-topic',
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='latest',
    enable_auto_commit=True,
    group_id='online-image',
    # value_deserializer=lambda x: loads(x.decode('utf-8'))
)
# reset to the end of the stream
#consumer.poll()
#consumer.seek_to_end()
#
n=0
fpath = get_script_path()
for msg in consumer:
    img_base64 = msg.value.decode('utf-8')
    img_bytes = base64.b64decode(img_base64)
    data = {}
    data['img'] = img_base64
    dump(data['img'], open(fpath+'/image.json', 'w'))

    n+=1
    print("received image", n)
    
    # # Display or save the image
    # #img.show()
    # # Load image bytes into PIL Image object
    # img = Image.open(io.BytesIO(img_bytes))
    # rgb_im = img.convert('RGB')
    # rgb_im.save('received_image.png', format="png")
    # #img.save('received_image.jpeg')
    sleep(0.1)