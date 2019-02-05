from StringIO import StringIO
from gzip import GzipFile
import base64
import inspect
import json
import requests
import struct
import time

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class API(object):
	def __init__(self):
		self.s=requests.Session()
		self.s.headers.update({'Content-Type':'application/json','Accept-Language':'en-gb','Accept-Encoding':'gzip, deflate','User-Agent':'idleminertycoon/23477 CFNetwork/808.2.16 Darwin/16.3.0','X-PlayFabSDK':'UnitySDK-2.37.180129','X-ReportErrorAsSuccess':'true','X-Unity-Version':'2017.4.11f1'})
		self.s.verify=False
		self.TitleId='B343'
		self.X_Authorization=None
		self.AppVersion='2.29.0:23477'
		self.SavegameVersion=105

	def setDeviceId(self,id):
		self.log('setting device_id:%s'%(id))
		self.DeviceId=id

	def setSavegameId(self,id):
		self.log('setting savegame_id:%s'%(id))
		self.SavegameId=id

	def log(self,msg):
		print '[%s]%s'%(time.strftime('%H:%M:%S'),msg.encode('utf-8'))

	def DecompressString(self,msg):
		return GzipFile(fileobj=StringIO(base64.b64decode(msg)[4:])).read().rstrip()
		
	def CompressString(self,msg):
		s=msg.rstrip()
		out = StringIO()
		with GzipFile(fileobj=out, mode="w") as f:
			f.write(s.encode('utf-8'))
		res= struct.pack("<L",len(s.encode('utf-8')))+out.getvalue()
		return base64.b64encode(res)

	def callAPI(self,data):
		if self.X_Authorization:
			r=self.s.post('https://b343.playfabapi.com/Client/'+inspect.stack()[1][3],data=json.dumps(data),headers={'X-Authorization':self.X_Authorization})
		else:
			r=self.s.post('https://b343.playfabapi.com/Client/'+inspect.stack()[1][3],data=data)
		if 'Savegame' in r.content:
			self.log('have savegame')
			self.Savegame=json.loads(self.DecompressString(json.loads(json.loads(r.content)['data']['InfoResultPayload']['UserData']['Savegame']['Value'])['Savegame']))
			self.NetWorth=json.loads(json.loads(r.content)['data']['InfoResultPayload']['UserData']['Savegame']['Value'])['NetWorth']
		if 'SessionTicket' in r.content:
			self.X_Authorization=json.loads(r.content)['data']['SessionTicket']
			self.log(self.X_Authorization)
		return r.content

	def LoginWithIOSDeviceID(self):
		return self.callAPI('{"CreateAccount":true,"DeviceId":"%s","DeviceModel":"iPad Air 2","EncryptedRequest":null,"InfoRequestParameters":{"GetCharacterInventories":false,"GetCharacterList":false,"GetPlayerProfile":false,"GetPlayerStatistics":false,"GetTitleData":false,"GetUserAccountInfo":true,"GetUserData":true,"GetUserInventory":false,"GetUserReadOnlyData":false,"GetUserVirtualCurrency":false,"PlayerStatisticNames":null,"ProfileConstraints":null,"TitleDataKeys":null,"UserDataKeys":null,"UserReadOnlyDataKeys":null},"LoginTitlePlayerAccountEntity":null,"OS":"iOS 10.2","PlayerSecret":null,"TitleId":"%s"}'%(self.DeviceId,self.TitleId))

	def GetAccountInfo(self):
		return self.callAPI('{"Email":null,"PlayFabId":null,"TitleDisplayName":null,"Username":null}')

	def UpdateUserData(self):
		save='{"SavegameId":"%s","DeviceId":"%s","SavegameVersion":%s,"AppVersion":"%s","Savegame":"%s","NetWorth":%s}'%(self.SavegameId,self.DeviceId,self.SavegameVersion,self.AppVersion,self.Savegame,self.NetWorth)
		return self.callAPI({"Data":{"Savegame":save},"KeysToRemove":None,"Permission":None})

	def haveSavegame(self):
		if not hasattr(self,'Savegame'):
			self.log('! could not load savegame..')
			exit(1)
		return True

	def addSkill(self,cnt):
		self.haveSavegame()
		for idx,s in enumerate(self.Savegame['Data']['Resources']['WorldSkillpoints']):
			self.Savegame['Data']['Resources']['WorldSkillpoints'][idx]=self.Savegame['Data']['Resources']['WorldSkillpoints'][idx]+cnt
		self.Savegame=self.CompressString(json.dumps(self.Savegame,separators=(',', ':')))
		self.UpdateUserData()

	def addSuperCash(self,cnt):
		self.haveSavegame()
		self.log('cash:%s'%(self.Savegame['Data']['Resources']['SuperCash']))
		self.Savegame['Data']['Resources']['SuperCash']=float(self.Savegame['Data']['Resources']['SuperCash']+cnt)
		self.log('cash:%s'%(self.Savegame['Data']['Resources']['SuperCash']))
		self.Savegame=self.CompressString(json.dumps(self.Savegame,separators=(',', ':')))
		self.UpdateUserData()

	def addChests(self,cnt):
		self.haveSavegame()
		print self.Savegame['Data']['Chests']
		for idx,c in enumerate(self.Savegame['Data']['Chests']):
			self.Savegame['Data']['Chests'][idx]['Amount']+=cnt
		print self.Savegame['Data']['Chests']
		self.Savegame=self.CompressString(json.dumps(self.Savegame,separators=(',', ':')))
		self.UpdateUserData()

if __name__ == "__main__":
	a=API()
	a.setDeviceId('YOURID')
	a.setSavegameId('YOURID')
	a.LoginWithIOSDeviceID()
	a.addSuperCash(50000)
	#a.addChests(100)
	#a.addSkill(10000)