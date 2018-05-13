from bigchaindb_driver import BigchainDB
from bigchaindb_driver.crypto import generate_keypair
import time
from pprint import pprint

bdb_root_url='http://localhost:59984'
bdb = BigchainDB(bdb_root_url)

# define asset
oliveoil={'data':{'ml':{'origin':'lamia','quality':'A'},},}

# create keys
pr = generate_keypair()
tr1 = generate_keypair() #1st trader
tr2 = generate_keypair() #2nd trader


#create asset
def create(asset_name, public_key,private_key,amount):
	prep_cr_tx = bdb.transactions.prepare(operation='CREATE',signers=pr.public_key,recipients=[([public_key],amount)],asset=asset_name,)
	ful_cr_tx = bdb.transactions.fulfill(prep_cr_tx,private_keys=private_key)
	sent_cr_tr = bdb.transactions.send(ful_cr_tx)
	asset_id = sent_cr_tr['id']

	time.sleep(3)

	print("\n\n Create transaction *******************************************************************\n\n")
	pprint(sent_cr_tr)

	return (sent_cr_tr,asset_id)


#transfer tokens
def transfer(sent_cr_tr,output_index,sender_private_key,sender_public_key, receiver_public_key, value): # pr -> sender / tr -> receiver
	if sent_cr_tr['operation'] == "CREATE" :
		asset_id= sent_cr_tr['id'] 
		tx_id = sent_cr_tr['id']
		output = sent_cr_tr['outputs'][output_index]
		tr_input = { 'fulfillment':output['condition']['details'], 'fulfills':{'output_index':output_index,'transaction_id':tx_id,},'owners_before':output['public_keys'],}
		dif = int(output['amount']) - value
		pr_tr_tx = bdb.transactions.prepare(operation='TRANSFER', asset = {'id':asset_id,},inputs=tr_input,recipients=[([receiver_public_key],value),([sender_public_key],dif)])
		ful_tr_tx = bdb.transactions.fulfill(pr_tr_tx,private_keys=sender_private_key)
		sent_tr_tx = bdb.transactions.send(ful_tr_tx)

		print("\n\n Send transaction *******************************************************************\n\n")
		pprint(sent_tr_tx)

		time.sleep(3)

	elif sent_cr_tr['operation'] == "TRANSFER" :
		output = sent_cr_tr['outputs'][0]
		asset_id = sent_cr_tr['asset']['id']
		tx_id = sent_cr_tr['id']
		tr_input = { 'fulfillment':output['condition']['details'], 'fulfills':{'output_index':output_index,'transaction_id':tx_id,},'owners_before':output['public_keys'],}
		dif = int(output['amount']) - value
		pr_tr_tx = bdb.transactions.prepare(operation='TRANSFER', asset = {'id':asset_id,},inputs=tr_input,recipients=[([receiver_public_key],value),([sender_public_key],dif)])
		ful_tr_tx = bdb.transactions.fulfill(pr_tr_tx,private_keys=sender_private_key)
		sent_tr_tx = bdb.transactions.send(ful_tr_tx)

		print("\n\n Transfer transaction *******************************************************************\n\n")
		pprint(sent_tr_tx)

		time.sleep(3)

	return sent_tr_tx

#count tokens for a certain trader
def count(public_key,asset_id):
	balance=0
	for t in bdb.transactions.get(asset_id = asset_id):

		if public_key == t['inputs'][0]['owners_before'][0] and t['operation']=='TRANSFER' :
			for o in t['outputs']:
				balance = balance - int(o['amount'])
				print("-",o['amount'])

		for o in t['outputs']:
			if o['public_keys'][0]==public_key:
				balance = balance + int(o['amount'])
				print("+",o['amount'])
	return balance
			


sent_cr_tr,asset_id=create(oliveoil,pr.public_key,pr.private_key,1000)		#pr == 1000 tokens
tx = transfer(sent_cr_tr,0,pr.private_key,pr.public_key,tr1.public_key,600)	# pr --> tr1
tx = transfer(tx,0,tr1.private_key,tr1.public_key,tr2.public_key,400)		# tr1 --> tr2
tx = transfer(tx,0,tr2.private_key,tr2.public_key,pr.public_key,100)		# tr2 --> pr

#print how many tokens Producer has
print("\n Producer's transactions: ")
print(count(pr.public_key,asset_id))





