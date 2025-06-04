import sys

chinese = u"Chinese Unicode: \u8fd9\u662f\u4e00\u4e2a\u6d4b\u8bd5\u7684\u4e2d\u6587\u5b57\u7b26\u3002"
japanese = u"Japanese Unicode: \u3053\u306e\u65e5\u672c\u8a9e\u306e\u6587\u5b57\u306e\u305f\u3081\u306e\u30c6\u30b9\u30c8\u3067\u3059\u3002"
russian = u"Russian Unicode: \u042d\u0442\u043e \u0442\u0435\u0441\u0442 \u0434\u043b\u044f \u0440\u0443\u0441\u0441\u043a\u0438\u0445 \u0441\u0438\u043c\u0432\u043e\u043b\u043e\u0432."

def run():
	# Note: The default encoding is set in BWAutoImport.py
	encoding = sys.getdefaultencoding()

	print u"Unicode Test -", encoding
	print chinese
	print japanese
	print russian

	if encoding == "utf-8":
		import utf8_test
		utf8_test.run()
	elif encoding == "gb18030":
		import gb18030_test
		gb18030_test.run()

# unicode_test.py
