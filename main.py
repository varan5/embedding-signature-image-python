#Embedding hidden signature in an image
#to protect piracy by proving ownership

import cv2
SIGNATURE_LENGTH = 100
def normalize_signature(signature):
	#input= 'Image Owner: abc.com'
	#output = 'DS:[Image Owner: abc.com********************]'
	extra_needed = 5
	if len(signature) + extra_needed > SIGNATURE_LENGTH:
		print('Max signature length : ', SIGNATURE_LENGTH - extra_needed)
		return None
	#right padding the signature to len : 95
	signature = signature.ljust(SIGNATURE_LENGTH-extra_needed, '*')

	#set the format
	signature = 'DS:[' + signature + ']'
	return signature

def getEmbeddingPoints():
	points = []
	x = 7 #arbitrary value
	for y in range(0,SIGNATURE_LENGTH*2,2): #min: 0, max: 200, step: 2
		points.append((x,y))

	return points

#Break a byte into bit set 3bits,3bits,2bits
#example: 104 ---> [‭011,010,00‬]
def getBits(n):
	bit1 = n >>5
	bit2 = (n & 28)>>2
	bit3 = n & 3
	return [bit1,bit2, bit3]

#Compose a byte from bit set 3bits,3bits,2bits
#example: [‭011,010,00‬] ---> 104
def getByte(bits):
	temp = bits[0]<<3 #‭011000 <--- 011
	temp = temp | bits[1] #011010 <--- 011000 | 010
	temp = temp << 2 #01101000 <--- 011010
	temp = temp | bits[2] #01101000 <--- #01101000 | 00
	return temp


def embed(targetImage, sourceImage, signature):
	#loading an image as a ndarray
	img = cv2.imread(sourceImage)
	if img is None:
		print(sourceImage, 'not found')
		return
	#print(img.shape)

	#normalize the signature
	norm_sign = normalize_signature(signature)

	#get the embedding points
	points = getEmbeddingPoints()

	#embed
	cnt = 0
	for x,y in points:
		data = ord(norm_sign[cnt]) #example : h --> 104
		bits = getBits(data) #example 104: [011, 010, 00]

		img[x][y][2]= (img[x][y][2] & ~7) | bits[0]  # embed in RED band
		img[x][y][1]= (img[x][y][1] & ~7) | bits[1]  # embed in GREEN band
		img[x][y][0]= (img[x][y][0] & ~3) | bits[2]  # embed in BLUE band
		cnt+=1

	#save the resultant img
	cv2.imwrite(targetImage, img)


def extract(imageFile):
	#loading an image as a ndarray
	img = cv2.imread(imageFile)
	if img is None:
		print(imageFile, 'not found')
		return
	#print(img.shape)

	#get the embedding points
	points = getEmbeddingPoints()

	#extract

	signature = ''
	for x,y in points:
		bit1= img[x][y][2] & 7  # extract from RED band
		bit2= img[x][y][1] & 7  # extract from GREEN band
		bit3= img[x][y][0] & 3  # extract from BLUE band

		data = getByte([bit1, bit2, bit3])
		signature = signature + chr(data)

	return signature

src = 'd:/images/work.jpg'
res = 'd:/images/result.png'
signature = 'This image belongs to Python Student'

embed(res, src, signature)
ext_sign = extract(res)
print(ext_sign)
