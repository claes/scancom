import zbar
import Image


fname = 'testimages/qr-test1.jpg'
img = Image.open(fname).convert('L')
width, height = img.size 

scanner = zbar.ImageScanner()
scanner.parse_config('enable')
zbar_img = zbar.Image(width, height, 'Y800', img.tostring())

# scan the image for barcodes
scanner.scan(zbar_img)

for symbol in zbar_img:
    print symbol 