package FinSim;

/**
 * singleton class for (global) run-time options
 *
 */
public class Options {
	public boolean readOnly;		// no file updates
	public boolean verbose;			// chatty commentary
	public boolean debugFile;		// file operations
	public boolean debugCommand;	// command line options
	
	static Options instance;
	
	private Options() {
		verbose = false;
		readOnly = false;
		debugFile = false;
		debugCommand = false;
	}
	
	/**
	 * allocate an instance if we don't already have one
	 * @return	(Options) reference to that instance
	 */
	public static Options getInstance() {
		if (instance == null)
			instance = new Options();
		return( instance );
	}
	
	/**
	 * parse a switch specification and set options accordingly
	 * 
	 * @param arg	String to be parsed (less the switch character)
	 */
	public void parseSwitch( String arg ) {
		// figure out what the option is
		char c = arg.charAt(0);
		switch (c) {
		case 'v':
			verbose = true;
			return;
		case 'r':
			readOnly = true;
			return;
		case 'D':	// DEBUG options
			String opts = arg.substring(1);
			if (opts.contains("C"))
				debugCommand = true;
			if (opts.contains("F"))
				debugFile = true;
			return;
		}
	}
	
	/**
	 * render the options into a string suitable for printing
	 * (as a diagnostic "what options are in effect).
	 */
	public String toString() {
		String opts = "";
		opts += readOnly ? "read-only" : "read/write";
		opts += ",";
		opts += verbose ? "verbose" : "quiet";
		
		String dbg = "";
		if (debugFile) dbg += dbg.isEmpty() ? "File" : ",File";
		if (debugCommand) dbg += dbg.isEmpty() ? "Command" : ",Command";
		
		if (dbg.isEmpty())
			return opts;
		else
			return( opts + " + DEBUG(" + dbg + ")" );
	}
}
