
import pprint



ANAESTHETISTS = {
	'tt': 'Dr T Thompson',
	'sv': 'Dr S Vuong',
	'cb': 'Dr C Brown',
	'jr': 'Dr J Riley',
	'js': 'Dr J Stevens',
	'db': 'Dr D Bowring',
	'gos': "Dr G O'Sullivan",
	'jt': 'Dr J Tester',
	'rw': 'Dr Rebecca Wood',
	'mm': 'Dr M Moyle',
	'mon': "Dr Martine O'Neill",
	'ni': 'Dr N Ignatenko',
	'ns': 'Dr N Steele',
	'tr': 'Dr Timothy Robertson',
	'ms': 'Dr M Stone',
	'fd': 'Dr Felicity Doherty',
	'bm': 'Dr B Manasiev',
	'eoh': "Dr E O'Hare",
	'locum': 'locum',
	'jrt': 'Dr J Tillett'
	}
	
# very basic print out. this is not easy to read.	
print ( ANAESTHETISTS )

print('-' * 10)

# import pprint. print out is clear.
pprint.pprint ( ANAESTHETISTS )

print('-' * 10)

# somehow i get a value from a key of the dictionary
print ( ANAESTHETISTS.get ('tt'))

print('-' * 10)

# prompting user to type in 
print (f"type initial of replacing anaesthetist. \n > ", end='' )


anaesthetist = input()
print ( ANAESTHETISTS.get ( anaesthetist ))


# sliced out anaesthetist surname. 
# does not work anaesthetist with full first name ie rebecca

#offset = 5
#length = 10
#sliced = ANAESTHETISTS.get ( anaesthetist )[offset:offset+length]
#print (sliced)


# tfs title firstname surname
tfs = ( ANAESTHETISTS.get ( anaesthetist ))
print ( tfs.split())


# s  surname only
s = ( ANAESTHETISTS.get ( anaesthetist )).split(' ', 2)
surname_only = s[2]
print (surname_only)





