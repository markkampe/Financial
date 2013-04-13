package accounting;

import java.util.Calendar;

/**
 * main class
 * 	process command line arguments
 * 	take a good guess at a reasonable reference date
 * 	invoke the graphical application
 * 
 * @author markk
 */
public class Accounting {
	
	private static final String LEDGER_ENV = "LEDGER";
	private static final String SWITCH_CHAR = "-";
	
	public static void main(String args[]) throws InterruptedException {
		
		// get the options singleton
		Options opts = Options.getInstance();
		
		// process the arguments
		String fileName = System.getenv(LEDGER_ENV);
		for( int i = 1; i < args.length; i++ ) {
			if (args[i].startsWith(SWITCH_CHAR)) {	
				opts.parseSwitch( args[i].substring(1));
			} else {
				fileName = args[i];		// name of accounting file
			}
		}
		
		// after arg parsing so we know whether or not to enable
		TimeStamp.logEvent("main called");
			
		// figure out the most plausible reporting date
		//		first of some month, either this or previous
		Calendar c = Calendar.getInstance();
		int year = c.get(Calendar.YEAR);
		int month = c.get(Calendar.MONTH) + 1;
		int day = c.get(Calendar.DAY_OF_MONTH);
		if (day < 15 && month > 1) {
			month--;
		}
		SimpleDate refdate = new SimpleDate( year, month, 1 );
		
		// see if we have been asked for invocation debug info
		if (opts.debugCommand) {
			System.out.println("File: " + fileName );
			System.out.println("Ref:  " + refdate );
			System.out.println("Opts: " + opts );
		}
		
		// create the basic screen
		new MainScreen( fileName, refdate );
	}
}