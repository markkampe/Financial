package FinSim;


/**
 * main class
 * 
 * @author markk
 */
public class FinSim {
	
	private static final String FINSIM_ENV = "FINSIM";
	private static final String SWITCH_CHAR = "-";
	
	public static void main(String args[]) throws InterruptedException {
		
		// get the options singleton
		Options opts = Options.getInstance();
		
		// process the arguments
		String fileName = System.getenv(FINSIM_ENV);
		for( int i = 1; i < args.length; i++ ) {
			if (args[i].startsWith(SWITCH_CHAR)) {	
				opts.parseSwitch( args[i].substring(1));
			} else {
				fileName = args[i];		// name of accounting file
			}
		}
		
		// see if we have been asked for invocation debug info
		if (opts.debugCommand) {
			System.out.println("File: " + fileName );
			System.out.println("Opts: " + opts );
		}
		
		// create the basic screen
		// new MainScreen( fileName );
	}
}