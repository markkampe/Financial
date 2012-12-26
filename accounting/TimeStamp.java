package accounting;

import java.util.Calendar;

public class TimeStamp {
	static Options opts;
	
	static private long startTime = 0L;
	
	static public void logEvent( String msg ) {
		
		// see if we have been enabled
		if (opts == null)
			opts = Options.getInstance();
		if (opts.debugTime == false)
			return;
		
		Calendar now = Calendar.getInstance();
		long ms = now.getTimeInMillis();
		
		// normalize all times to the time of first call
		if (startTime == 0L)
			startTime = ms;
	
		String seconds = String.format("%3d", (ms-startTime)/1000);
		String millis = String.format(".%03d", (ms-startTime)%1000);
		
		System.out.println( seconds + millis + ": " + msg );
	}
}
