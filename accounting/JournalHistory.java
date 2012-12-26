package accounting;

/**
 * this class keeps a stack of journal records performed in one session
 * (to be used for LIFO undo)
 * 
 * @author markk
 */
public class JournalHistory {
	

		
	public int accountNum;		// number of account
	public String accountName;	// name of account
	public Ledger entry;		// ledger entry for this transaction
	private JournalHistory next;// next pointer
		
	private static JournalHistory firstRecord;	// top of our history stack
		
	/**
	 * create a new history entry 
	 * 
	 * @param acctNum	(int) number associated with this transaction
	 * @param acctName	(String) name of account
	 * @param entry		Ledger entry associated with this transaction
	 */
	private JournalHistory( int acctNum, String acctName, Ledger ent ) {
		accountNum = acctNum;
		accountName = acctName;
		entry = ent;
		next = null;
	}
		
	/**
	 * push a new history entry onto the stack
	 * 
	 * @param acctNum	(int) number associated with this transaction
	 * @param acctName	(String) name of account
	 * @param entry		Ledger entry associated with this transaction
	 */
	static public void push( int acctNum, String acctName, Ledger ent ) {
		JournalHistory newEntry = new JournalHistory(acctNum, acctName, ent );
		
		newEntry.next = firstRecord;
		firstRecord = newEntry;
	}
	
	/**
	 * pop the top item off of the history stack
	 * 
	 * @return	JournalHistory	first element on the stack
	 */
	static public JournalHistory pop() {
		JournalHistory top = firstRecord;
		if (top != null) {
			firstRecord = top.next;
			top.next = null;
		}
		return top;	
	}
	
	/**
	 * dump out the history stack in chronological order
	 * 
	 * @return	String containing the accumulated history
	 */
	static public String dump() {
		String result = "";
		String NAME_FORMAT = "%-" + Account.NAME_WIDTH + "s";
		
		for (	JournalHistory element = firstRecord;
				element != null;
				element = element.next ) {
			result = String.format(NAME_FORMAT, element.accountName) + "  " 
					+ element.entry.toString() + "\n" 
					+ result;
		}
		
		return result;
	}
}

