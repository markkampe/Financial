package accounting;

/**
 * a collection of accounts
 * 
 * @author markk
 */
public class Books {
	// empty refs are so cheap it isn't worth making dynamic
	private static final int MAX_ACCOUNTS = 99;
	
	private int		num_accounts;
	private Account	accounts[];
	private String	summaries[];
	private boolean dirty;		// has this account been updated
	
	// these are values rather than functions because they
	// are expensive to accumulate, so I update them very
	// deliberately
	public int monBudget;	// monthly budget
	public int initBal;		// balance at start of asOf
	public int totCredits;	// credits since asOf
	public int totBudget;	// budget credits since asOf
	public int totDebits;	// debits since asOf
	public int finalBal;	// final balance
	
	public Books( ) {
		// create an empty accounts array
		accounts = new Account[MAX_ACCOUNTS];
		num_accounts = 0;
		summaries = null;
		
		// initialize the total summary
		monBudget = 0;
		initBal = 0;
		totCredits = 0;
		totDebits = 0;
		finalBal = 0;
		
		dirty = false;
	}
	
	/**
	 * return the name of the n'th account
	 * 
	 * @param acctNumber	selection index of desired account
	 * 
	 * @return	String		name of selected account
	 */
	public String accountName( int acctNumber ) {
		if (acctNumber >= 0 && acctNumber < num_accounts) {
			return accounts[acctNumber].name;
		} else
			return null;
	}
	
	/**
	 * return an array of account names (e.g. for combox)
	 * 
	 * @return 	String[]
	 */
	public String[] accountNames() {
		String[] names = new String[num_accounts];
		for( int i = 0; i < num_accounts; i++ ) {
			names[i] = accounts[i].name;
		}
		return names;
	}
	
	/**
	 * return the monthly budget for an account
	 * 
	 * @param	acctNumber	selection index of desired account
	 * 
	 * @return	Dollars		monthly budget
	 */
	public int accountBudget( int acctNumber ) {
		if (acctNumber >= 0 && acctNumber < num_accounts)
			return( accounts[acctNumber].budget );
		else
			return 0;
	}
	
	/**
	 * return the final balance for an account
	 * 
	 * @param	acctNumber	selection index of desired account
	 * 
	 * @return	Dollars		final balance
	 */
	public int finalBalance( int acctNumber ) {
		if (acctNumber >= 0 && acctNumber < num_accounts)
			return( accounts[acctNumber].finalBal );
		else
			return 0;
	}
	
	
	/**
	 * return number of initialized accounts
	 * @return	int	number of initialized accounts
	 */
	int numAccounts() {
		return num_accounts;
	}
	
	/**
	 * add a new account to the current set of books
	 * 
	 * @param name		name of new account
	 * @param monthly	monthly budget
	 * @return			account index number
	 */
	public int addAccount( String name, int monthly ) {
		accounts[num_accounts] = new Account( name, monthly );
		return( num_accounts++ );
	}
	
	/**
	 * post a ledger entry to an account
	 * 
	 * @param account	index of account to which it should be posted
	 * @param entry		ledger entry to be posted
	 */
	public boolean post( int account, Ledger entry ) {
		if (account < num_accounts) {
			dirty = true;
			return accounts[account].record(entry);
		} else
			return false;
	}
	
	/**
	 * undo a ledger entry in an account
	 * 
	 * @param account	(int) account in which entry was made
	 * @param entry		(Ledger) entry to be invalidated
	 */
	public void undo(int account, Ledger entry) {
		if (account < num_accounts) {
			accounts[account].undo(entry);
		}
	}
	
	/**
	 * add the monthly budget for each account
	 * 
	 * @param	SimpleDate	effective date of addition
	 * 
	 * @return	Boolean	were any changes made
	 */
	public boolean addBudget( SimpleDate when ) {
		int changes = 0;
		for( int i = 0; i < num_accounts; i++ ) {
			if (accounts[i].addBudget( when ))
				changes++;
		}
		
		if (changes > 0) {
			dirty = true;
		    return true;
		} else
			return false;
	}
	
	/**
	 * get the balances for all accounts, and then come up with grand totals
	 * 
	 * @param	boolean	should we force a recomputation for all accounts
	 */
	public void getBalances( SimpleDate when, boolean force ) {
		// zero my totals
		initBal = 0;
		totCredits = 0;
		totBudget = 0;
		totDebits = 0;
		finalBal = 0;
		monBudget = 0;
		
		// then recompute balances for each account
		for( int i = 0; i < num_accounts; i++ ) {
			accounts[i].getBalances(when, force);
			
			// accumulate the balances from this account
			monBudget += accounts[i].budget;
			initBal += accounts[i].initBal;
			totBudget += accounts[i].totBudget;
			totCredits += accounts[i].totCredits;
			totDebits += accounts[i].totDebits;
			finalBal += accounts[i].finalBal;
		}
	}

	public String[] analysis() {
		getBalances(null, true);
		return summary(true);
	}
	
	/**
	 * print out a summary of each account followed by a grand total
	 * 
	 * @param	perfVsBudget	include vs budget percentages
	 * 
	 * @return	String[]		array of lines of summary
	 */
	public String[] summary( Boolean perfVsBudget ) {
		
		// if we don't already have a summary array, allocate one
		if (summaries == null)
			summaries = new String[num_accounts+3];
		
		// start with a heading line
		summaries[0] = Account.summaryLine("*", 0, 0, 0, 0, 0, perfVsBudget );
		
		// generate the summary for each account
		for( int i = 0; i < num_accounts; i++ ) {
			summaries[i+1] = accounts[i].summaryLine( perfVsBudget );
		}
		
		//	summaries[num_accounts] is left blank
		summaries[num_accounts+1] = Account.summaryLine("-", 0, 0, 0, 0, 0, perfVsBudget );
		
		// grand total summary
		summaries[num_accounts+2] = Account.summaryLine("Total", initBal, totBudget, totCredits, totDebits, finalBal, perfVsBudget );
		
		return( summaries );
	}
	
	/**
	 * have there been changes made to these books
	 * 
	 * @return	boolean
	 */
	public boolean clean() {
		
		return !dirty;
	}
	
	/**
	 * mark an account as clean (in sync w/on-disk file)
	 * 
	 * @param isclean
	 */
	public void clean(Boolean isclean) {
		dirty = !isclean;
	}

	/**
	 * detailed ledger listing of a specified account
	 * 
	 * @param index
	 */
	public String[] ledgerDump( int index ) {
		if (index < 0 || index >= num_accounts)
			return null;
		return accounts[index].ledgerDump();
	}
}