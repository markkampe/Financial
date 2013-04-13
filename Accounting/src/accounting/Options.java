package accounting;

/**
 * singleton class for (global) run-time options
 *
 */
public class Options {
	
	public boolean writeable;		// we are allowed to write
	public boolean verbose;			// chatty commentary
	public boolean debugFile;		// file operations
	public boolean debugCommand;	// command line options
	public boolean debugTime;		// timestamps
	
	static Options instance;
	
	private Options() {
		writeable = true;
		verbose = false;
		debugFile = false;
		debugCommand = false;
		debugTime = false;
	}
	
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
			writeable = false;
			return;
		case 'D':	// DEBUG options
			String opts = arg.substring(1);
			if (opts.contains("C"))
				debugCommand = true;
			if (opts.contains("F"))
				debugFile = true;
			if (opts.contains("T"))
				debugTime = true;
			return;
		}
	}
	
	public String toString() {
		String opts = "";
		opts += writeable ? "write" : "read-only";
		opts += ",";
		opts += verbose ? "verbose" : "quiet";
		
		String dbg = "";
		if (debugFile) dbg += dbg.isEmpty() ? "File" : ",File";
		if (debugCommand) dbg += dbg.isEmpty() ? "Command" : ",Command";
		if (debugTime) dbg += dbg.isEmpty() ? "Timing" : ",Timing";
		
		if (dbg.isEmpty())
			return opts;
		else
			return( opts + " + DEBUG(" + dbg + ")" );
	}
}
