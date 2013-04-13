package accounting;

/**
 * a single ledger entry
 * 
 * @author markk
 */
public class Ledger {
	// the spacing of the fields in a printed ledger entry
	//	date, amount, description
	//	note, that both dates and amounts have their own formatting
	//	which may include padding to a fixed field width
	private static final String LEDGER_FORMAT = "%s %s      %s";
	
	public int amount;			// amount of debit or credit
	public SimpleDate date;		// date on which it occurred
	public String description;	// description
		
	/**
	 * create a new ledger entry
	 * 
	 * @param cents	amount (in cents)
	 * @param when	SimpleDate
	 * @param what	String (description)
	 */
	public Ledger( int cents, SimpleDate when, String what ) {
		amount = cents;
		date = when;
		description = what;
	}
	
	/**
	 * convert a ledger entry into a text line
	 */
	public String toString() {
		
		return(String.format(LEDGER_FORMAT, date, Dollars.toString(amount), description ));
	}
}
