JAR=Accounting.jar

$(JAR): 
	javac -d bin src/accounting/*.java
	cd bin; jar -cvfm ../Accounting.jar ../Accounting.mf accounting/*.class accounting/images
