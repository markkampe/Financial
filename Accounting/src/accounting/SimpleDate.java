package accounting;

/**
 * Simple dates (year/month/day), easier to use than Date+Calendar
 * 
 * @author markk
 */
public class SimpleDate {
	public int year;
	public int month;
	public int day;
	
	/**
	 * SimpleDate constructor (from numbers)
	 * 
	 * @param yr	year (e.g. 2010)
	 * @param mon	month (0-12) ... 0 is special case
	 * @param day_of_month (0-31) ... 0 is special case
	 */
	public SimpleDate( int yr, int mon, int day_of_month ) {
		year = yr;
		month = mon;
		day = day_of_month;
	}
	
	/**
	 * SimpleDate constructor (from string)
	 * 
	 * @param string to be parsed
	 * @param default year (int)
	 * 
	 * NOTE:
	 * 	In the original 1970s program, dates were hand
	 * 	entered, so I made days and years optional.  That
	 *  no longer makes sense ... but since I have old 
	 *  books in this format, this routine will happily
	 *  parse them (and plug in a specified default year)
	 */
	public SimpleDate( String str, int dfltYear ) throws NumberFormatException {
		day = 1;
		year = dfltYear;
		
		// trim leading and trailing white space
		str = str.trim();
		
		// make sure the string is non-empty
		if (str.length() < 1)
			throw new NumberFormatException("Date cannot be blank");
		
		// find the first slash, which delimits the month
		int slash = str.indexOf('/');
		if (slash < 0)
			throw new NumberFormatException("no / in date");
		if (slash == 0)
			throw new NumberFormatException("no month");
		try {
			month = Integer.parseInt(str.substring(0,slash));
		} catch (NumberFormatException e) {
			throw new NumberFormatException( "invalid month " + e.getMessage() );
		}
		if (month < 0 || month > 12)
			throw new NumberFormatException("illegal month number");
		
		// see if there is any more
		str = str.substring(slash+1);
		if (str.length() == 0)
			return;
		
		// see where the day (if any) ends
		int endDay = str.length();
		slash = str.indexOf('/');
		if (slash > 0)
			endDay = slash;
		try {
			day = Integer.parseInt(str.substring(0,endDay));
		} catch (NumberFormatException e) {
			throw new NumberFormatException( "invalid day " + e.getMessage() );
		}
		if (day < 1 || day > 31)
			throw new NumberFormatException("illegal day number");
		
		// see if there is a year
		if (slash > 0) {
			try {
				year = Integer.parseInt(str.substring(slash+1));
			} catch (NumberFormatException e) {
				throw new NumberFormatException( "invalid year " + e.getMessage() );
			}
			if (year < 100) {
				if (year < 70)
					year += 1900;
				else
					year += 2000;
			}
			if (year < 1900 || year > 2100)
				throw new NumberFormatException("illegal year number");
		}	
	}
	
	/**
	 * is this SimpleDate earlier than another
	 * 
	 * @param other date to be compared against
	 * @return	boolean
	 * 
	 * NOTE:	in SimpleDates, the year can be zero
	 * 			which we should take as being equal
	 */
	public boolean before( SimpleDate other ) {
		if (year != 0 && year < other.year)
			return true;
		if (year != 0 && year > other.year)
			return false;
		if (month < other.month)
			return true;
		if (month > other.month)
			return false;
		return (day < other.day);
	}
	
	/**
	 * is this SimpleDate later than another
	 * 
	 * @param other date to be compared against
	 * @return	boolean
	 * 
	 * NOTE:	in SimpleDates, the year can be zero
	 * 			which we should take as being equal
	 */
	public boolean after( SimpleDate other ) {
		if (year != 0 && year > other.year)
			return true;
		if (year != 0 && year < other.year)
			return false;
		if (month > other.month)
			return true;
		if (month < other.month)
			return false;
		return (day >= other.day);	// tie goes to the incumbant
	}
	
	
	/**
	 * standard (my way) date representation
	 * 		but if day or year are zero, don't show them
	 * 
	 * @return	String	common US representation of date
	 */
	public String toString() {
		if (day > 0) {
			if (year > 0) {
				return String.format("%2d/%02d/%4d", month, day, year);
			} else {
				return String.format("%2d/%02d     ", month, day);
			}
		} else {
			return String.format("%2d/       ", month);
		}
	}
}
