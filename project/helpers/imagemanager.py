from project import app
from PIL import Image
import os
from project.config import constants as CONSTANTS
import sys
from project.helpers import tools

from project import app

currentFuncName = lambda n=0: sys._getframe(n + 1).f_code.co_name
currentFileName = os.path.basename(__file__)

class ImageManager:
	def __init__(self,image=None,save_path=None,path=None,custom_width=600,custom_height=800,ext='.png'):
		self.custom_width=custom_width
		self.custom_height=custom_height
		self.image=image
		self.save_path=save_path
		self.ext=ext

	def resize(self):
		success=None
		img_basename=os.path.basename(self.image)
		img_path=os.path.dirname(self.image)
		extension = os.path.splitext(self.image)[1][1:].strip()
		try:
			img = Image.open(self.image)
		except Exception as e:
			data=e,currentFileName,currentFuncName()
			tools.logHandler(data)
			success=False
		else:	
			img = img.resize((self.custom_width, self.custom_height), Image.ANTIALIAS)
			if self.save_path is None:
				self.save_path=img_path
			try:
				img.save(self.save_path+"/"+img_basename)
				success=True
			except Exception as e:
				data=e,currentFileName,currentFuncName()
				tools.logHandler(data)
				success=False
		return str(success)

	def to_base64(self):
		import base64
		extension = os.path.splitext(self.image)[1][1:].strip()
		try:
			image_file=open(self.image, "rb")
		except Exception as e:
			image_file=open(CONSTANTS.project_root+"/static/images/stream_not_found.png", "rb")
			encoded_string = base64.b64encode(image_file.read())
			decoded_string=encoded_string.decode("utf-8")
			decoded_string='data:image/jpeg;base64,'+str(decoded_string)
			return decoded_string
		else:
			with image_file:
				encoded_string = base64.b64encode(image_file.read())
				decoded_string=encoded_string.decode("utf-8")
				if extension=='jpg' or extension=='jpeg':
					decoded_string='data:image/jpeg;base64,'+str(decoded_string)
				elif extension=='png':
					decoded_string='data:image/png;base64,'+str(decoded_string)
				else:
					print('Invalid image format.')
					return False
		image_file.close()
		return decoded_string