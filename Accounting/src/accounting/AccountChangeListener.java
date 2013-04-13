package accounting;

/**
 * Account updates can be made from other than the MainScreen.
 * This interface allows the MainScreen to register to be notified
 * when somebody else records a new transaction.
 * 
 * @author markk
 */
public interface AccountChangeListener {
	
	/**
	 * call-back when an account is updated
	 * 
	 * @param accountNumber
	 */
	public void AccountChanged( int accountNumber );
}
