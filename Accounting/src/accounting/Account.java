package accounting;

/**
 * A named account with a budget and a set of ledger entries
 * 
 * Note:
 * 		I know that I will surely go to hell for creating classes
 * 		with public fields rather than accessor methods.  All of
 * 		these classes are package-private, and I am not worried 
 * 		about my ability to change any of these types in the future.
 * 
 * @author markk
 */
public class Account {
	// these (and Dollars.width) control the output format
	private static final String	COL_SEP = "   ";	// distance between columns
	public static final int NAME_WIDTH = 16;		// width of a name
	private static final int PCTG_WIDTH = 6;		// width of a performance percentage
	
	private static final String BUDGET_DESCRIPTION = "budget";
	
	public String name;			// name of this account
	public int budget;			// monthly budget

	// these are expensive to compute, so we save them
	public int initBal;		// balance at start of asOf
	public int totCredits;	// credits since asOf
	public int totBudget;	// portion of totCredits from budget
	public int totDebits;	// debits since asOf
	public int finalBal;	// final balance
	public boolean ignored;	// is this just a place holder
	
	private boolean upToDate;	// is the summary up to date
	
	private LedgerL firstElement;
	
	/**
	 * a LedgerL is a Ledger entry, extended for putting in a list
	 */
	private class LedgerL {
		Ledger	entry;			// the actual ledger entry
		LedgerL	nextElement;	// next entry in the list
		boolean ignore;			// ignore this entry
		// OPTIMIZE: eliminate ignore and actually remove the LedgerL
		
		LedgerL( Ledger l ) {
			entry = l;
			nextElement = null;
			ignore = false;
		}
	}
	
	/**
	 * constructor for a normal account
	 * @param accountName
	 * @param monthlyBudget
	 */
	public Account( String accountName, int monthlyBudget ) {
		name = accountName;
		budget = monthlyBudget;
		
		initBal = 0;
		totBudget = 0;
		totCredits = 0;
		totDebits = 0;
		finalBal = 0;
		
		firstElement = null;
		upToDate = false;
		ignored = false;
	}
	
	/**
	 * constructor for a place-holder account
	 * 
	 * @param accountName
	 */
	public Account( String accountName ) {
		name = accountName;
		
		budget = 0;
		initBal = 0;
		totBudget = 0;
		totCredits = 0;
		totDebits = 0;
		finalBal = 0;
		
		firstElement = null;
		upToDate = false;
		ignored = true;
	}
	
	/**
	 * recompute the basic reporting balances
	 * 	done by re-walking the ledger list
	 * 
	 * @param	Date	date dividing prev bal from credits/debits
	 * @param	boolean	should we force a recomputation
	 */
	public void getBalances( SimpleDate asOfWhen, boolean force ) {
		// if we're up to date, there is nothing to do
		if (upToDate && !force)
			return;
		
		// reset all summary amounts to zero
		initBal = 0;
		totCredits = 0;
		totBudget = 0;
		totDebits = 0;
		finalBal = 0;
		
		// if we have no ledger entries, nothing to do
		if (firstElement == null)
			return;
		
		// if no date has been specified, use 1/1 
		if (asOfWhen == null) {
			asOfWhen = new SimpleDate( firstElement.entry.date.year, 1, 1 );
		}
		
		// walk the entire ledger
		//		accumulating each amount against proper balance
		for ( LedgerL thisElement = firstElement; thisElement != null; thisElement=thisElement.nextElement ) {
			if (thisElement.ignore)
				continue;
			if ( thisElement.entry.date.before(asOfWhen) ) {
				initBal += thisElement.entry.amount;
			} else if (thisElement.entry.amount < 0) {
				totDebits += thisElement.entry.amount;
			} else {
				if (thisElement.entry.description.equals( BUDGET_DESCRIPTION ))
					totBudget += thisElement.entry.amount;
				else
					totCredits += thisElement.entry.amount;
			}
			finalBal += thisElement.entry.amount;
		}
		
		upToDate = true;
	}
	
	/**
	 * add one month's budget to this account
	 * 
	 * @param when	month for which we are adding
	 * @return		did we add anything
	 */
	public Boolean addBudget(SimpleDate when) {
		if (budget == 0)
			return false;
		
		record( new Ledger(budget, when, BUDGET_DESCRIPTION));
		return true;
	}
	
	/**
	 * add a new ledger entry to an account
	 * (sorted by date, and then by insertion order)
	 * 
	 * @param entry	Ledger entry to be inserted
	 */
	public boolean record( Ledger entry ) {
		LedgerL element = new LedgerL(entry);
		LedgerL prev = null;
		LedgerL next = firstElement;
		
		// find the element we go in front of
		while( next != null && entry.date.after(next.entry.date) ) {
			prev = next;
			next = next.nextElement;	
		}
		
		// insert myself into the list
		element.nextElement = next;
		if (prev == null)
			firstElement = element;
		else
			prev.nextElement = element;
		
		upToDate = false;	// this invalidates our balance summary
		return true;
	}
	
	/**
	 * invalidate a ledger entry
	 * 
	 * @param which	Ledger entry to be invalidated
	 * 
	 * Note: 
	 * 	for now I am just flagging the bad entry, but later I will
	 *	actually remove it from the list ... which only this class
	 *	knows about.
	 */
	void undo( Ledger which ) {
		for( LedgerL element = firstElement; element != null; element = element.nextElement ) {
			if (element.entry == which) {
				element.ignore = true;
				upToDate = false;
				return;
			}
		}
	}
	
	/**
	 * return a summary string for an account
	 * @return	String summary line (as of default reporting date)
	 */
	public String toString() {
		return summaryLine( name, initBal, totBudget, totCredits, totDebits, finalBal, false );
	}
	
	/**
	 * return a summary line for this account
	 * 
	 * @param perfVsBudget	boolean (do we want performance vs budget)
	 * 
	 * @return	String
	 */
	public String summaryLine( Boolean perfVsBudget ) {
		return summaryLine( name, initBal, totBudget, totCredits, totDebits, finalBal, perfVsBudget );
	}
	
	/**
	 * this is the only routine that knows how to format a summary line
	 * 	it also, therefore, knows how to produce lines of subtotal dashes
	 * 	it has been made static so it can also be used to generate 
	 * 	grand total summaries with the same spacing
	 * 
	 * @param	accountName ("-" means sub-totals, '*' means headings
	 * @param	initBal	first dollar amount to print
	 * @param	budget	second dollar amount to print
	 * @param	totCredits	third dollar amount to print
	 * @param	totDebits	fourth dollar amount to print
	 * @param	finalBal	fifth dollar amount to print
	 * @param	perfVsBudge	include performance vs budget
	 * 
	 * @return	String for account summary line
	 */
	public static String summaryLine(String accountName,
									int init, int budget, int credits, int debits, int ending,
									Boolean perfVsBudget ) {
		String result = "";
		
		if (accountName == "-") {
			// dashes for the name
			for( int i = 0; i < NAME_WIDTH; i++ )
				result += '_';
			
			// four columns of number dashes
			for( int i = 0; i < 5; i++ ) {
				result += COL_SEP;
				for( int j = 0; j < Dollars.width; j++ ) {
					result += '_';
				}
			}
			
			if (perfVsBudget) {
				for( int i = 0; i < 3; i++ ) {
					result += COL_SEP;
					for( int j = 0; j < PCTG_WIDTH; j++ ) {
						result += '_';
					}
				}
			}
		} else if (accountName == "*") {
			for( int i = 0; i < NAME_WIDTH; i++ )
				result += ' ';
			
			final String COLUMN_FORMAT = "%"+Dollars.width+"s";
			final String PCTG_FORMAT = "%" + PCTG_WIDTH + "s";
			result += COL_SEP;
			result += String.format(COLUMN_FORMAT, "bal fwd ");
			result += COL_SEP;
			result += String.format(COLUMN_FORMAT, "budget  ");
			result += COL_SEP;
			result += String.format(COLUMN_FORMAT, "credits ");
			result += COL_SEP;
			result += String.format(COLUMN_FORMAT, " debits ");
			result += COL_SEP;
			result += String.format(COLUMN_FORMAT, "balance ");
			if (perfVsBudget) {
				result += COL_SEP;
				result += String.format(PCTG_FORMAT, "   net" );
				result += COL_SEP;
				result += String.format(PCTG_FORMAT, "budget" );
				result += COL_SEP;
				result += String.format(PCTG_FORMAT, "credit" );
			}
		} else {
			// figure out what the name output format should be
			final String NAME_FORMAT = "%-"+NAME_WIDTH+"s";
			final String PCTG_FORMAT = "%+" + (PCTG_WIDTH-1) + "d%%";

			result = String.format(NAME_FORMAT, accountName);
			result += COL_SEP;
			result += Dollars.toString(init);
			result += COL_SEP;
			result += Dollars.toString(budget);
			result += COL_SEP;
			result += Dollars.toString(credits);
			result += COL_SEP;
			result += Dollars.toString(debits);
			result += COL_SEP;
			result += Dollars.toString(ending);
			if (perfVsBudget) {
				// net expenses as a function of all credits
				int vsCredits = percentage(budget + credits + debits, budget + credits);
				
				//	for accounts that don't have a budget, use the credits
				if (budget <= 1200)
						budget = (credits <= 0) ? 100 : credits;
				// net balance for year as a fraction of the annual budget
				int net = percentage( ending, budget );
				// net expenses for year as a fraction of the annual budget
				int vsBudget = percentage(budget + debits, budget);
					
				result += COL_SEP + String.format(PCTG_FORMAT, net);
				result += COL_SEP + String.format(PCTG_FORMAT, vsBudget);
				result += COL_SEP + String.format(PCTG_FORMAT, vsCredits);
			}
		}
		
		return result;
	}
	
	/**
	 * turn a numerator and denominator into a rounded-up fraction
	 * 
	 * @param numerator
	 * @param denominator
	 * 
	 * @return (int) the fraction expressed as a percentage
	 */
	private static int percentage( int numerator, int denominator ) {
		if (denominator == 0)	// watch out for zero divide
			return( -1 );
		
		// rounding (up in magnitude)
		if (numerator > 0)
			numerator += denominator/200;
		else
			numerator -= denominator/200;
		
		return ((numerator*100)/denominator);
	}
	
	/**
	 * generate a textural copy of our ledger
	 * 
	 * @return	String[]	array of ledger entries
	 */
	public String[] ledgerDump() {
		
		if (firstElement == null)
			return null;
		
		// count the number of valid entries
		int numEntry = 0;
		for( LedgerL element = firstElement; element != null; element = element.nextElement) {
			if (!element.ignore)
				numEntry++;
		}
		
		// create a dump array for this chain of ledger entries
		String[] result = new String[numEntry];
		int i = 0;
		for( LedgerL element = firstElement; element != null; element = element.nextElement) {
			if (!element.ignore)
				result[i++] = element.entry.toString();
		}
		return result;
	}
}
