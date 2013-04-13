If a project was checked in to git from eclipse:

	eclipse will very nicely share projects to git and import
	projects from git ... but if a java project is not already 
  	in git as an eclipse java project, I found it very difficult 
	to get eclipse to play with it in situ, or build a java
	project it did not create.

	easy: import, from git, existing project

If a java project is just a bunch of source files:

	select new project wizard, java project
	create java project (e.g. Accounting)
	create package (e.g. accounting)
	import all the java files into appropriate  package
	   (subdirectories are automatically imported under package)

	or, alternatively, ...
	    import the general hierarch


	new run configuration
	    name: ... something attractive, you'll see it a lot
	    project: name of the project
	    main class: <package>.<class>

	when you are ready to turn it into an application
	   export as jar
	   with all required classes
