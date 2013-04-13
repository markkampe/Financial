package accounting;
import java.awt.*;
import java.awt.event.*;
import javax.swing.*;

/**
 * this class implements the journalling window in which new 
 * deposits and expenses are entered
 * 
 * @author mkampe
 */
public class JournalWindow implements WindowListener, ActionListener {
	// private static final long serialVersionUID = 0xdeadbeef;
	
	private static final String TITLE = "New Ledger Entry";
	
	private static final int X_OFFSET = 100;	// x position relative to parent
	private static final int Y_OFFSET = 100;	// y position relative to parent
	
	// icon for this application
	private static final String ICON_IMAGE = "images/accounting-icon-32.png";
	
	private static final int WIDTH  = 500;		// maximum window width
	private static final int HEIGHT = 300;		// maximum window height
	
	private static final int ROWS = 8;			// default rows in transaction record
	private static final int COLS = 40;			// default columns in transaction record
	
	// context for this set of transactions
	private Books books;
	private SimpleDate when;
	
	// GUI widgetry
	private Frame thisWindow;
	
	private JTextField date;		// date of this transaction
	private JComboBox<String> account;		// account for this transaction
	private JTextField amount;		// amount of this transaction
	private JTextField description;	// description of this transaction
	
	private JTextArea lastOps;		// recently completed transaction
	
	private JButton credit;			// CREDIT button
	private JButton debit;			// DEBIT button
	private JButton done;			// DONE button
	private JButton undo;			// UNDO button
	
	// who should we tell when a transaction gets added
	private AccountChangeListener changeListener = null;
	
	/**
	 * create a window journaling window
	 * 
	 * @param String[] ... the text content of the ledger
	 */
	public JournalWindow( Books ourBooks, SimpleDate startingDate ) {
		when = startingDate;
		books = ourBooks;
		
		thisWindow = new Frame( TITLE );
		thisWindow.setLocation(X_OFFSET,Y_OFFSET);
		thisWindow.addWindowListener(this);
		
		// get our window icon
		Image myIcon = thisWindow.getToolkit().getImage(getClass().getResource(ICON_IMAGE));
		thisWindow.setIconImage(myIcon);
		
		// add the account selector and transaction fill-ins
		addTransactionPanel();
		date.setText(startingDate.toString());
		
		// create the transaction echo window
		lastOps = new JTextArea(ROWS, COLS);
		JScrollPane pane = new JScrollPane( lastOps );
		thisWindow.add(pane, BorderLayout.CENTER);
		
		// arrange to keep the focus out of the journal
		pane.setFocusable(false);
		lastOps.setFocusable(false);
		
		// add the action buttons to the bottom of the window
		addButtons();
		
		// put up the window
		thisWindow.setSize(WIDTH, HEIGHT);
		thisWindow.validate();
		thisWindow.setVisible(true);
		
		// prepare for input
		cleanup();
	}
	
	/**
	 * input verifier for date fields
	 *	run it through the date parser, catching/handling any exceptions
	 *	if it is good, rewrite it in canonical format
	 */
	class DateVerifier extends InputVerifier {
		public boolean verify( JComponent input ) {
			JTextField f = (JTextField) input;
			String infield = f.getText();
			
			// blank isn't valid, but neither is it broken
			if (infield.length() == 0)
				return true;
			
			try {
				SimpleDate result = new SimpleDate( infield, when.year );
				f.setText( result.toString() );
				return true;
			} catch (NumberFormatException e) {
				JOptionPane.showMessageDialog( thisWindow, 
						e.getMessage(), "INVALID DATE", JOptionPane.ERROR_MESSAGE );
				return false;
			}
		}
		
		public boolean shouldYieldFocus( JComponent input ) {
			return( verify( input ) );
		}
	}
	
	/**
	 * dollar amount verifier
	 * run it through the dollar parser, catching/handling any exceptions
	 * if it works, rewrite it in canonical form
	 */
	class DollarVerifier extends InputVerifier {
		public boolean verify( JComponent input ) {
			JTextField f = (JTextField) input;
			String infield = f.getText();
			
			// blank isn't valid, but neither is it broken
			if (infield.length() == 0)
				return true;
			
			try {
				int value = Dollars.Parse(infield);
				String canon = Dollars.toString(value);
				f.setText(canon.trim());
				return true;
			} catch (NumberFormatException e ) {
				JOptionPane.showMessageDialog( thisWindow, 
						e.getMessage(), "INVALID AMOUNT", JOptionPane.ERROR_MESSAGE );
				return false;
			}
		}
		
		/**
		 * if a field is broken, we should not yield focus
		 */
		public boolean shouldYieldFocus( JComponent input ) {
			return( verify( input ) );
		}
	
	}
	/**
	 * validate the input and create a ledger transaction
	 * for it.
	 * 
	 * @param	credit	(boolean) is this a credit?
	 * 
	 * @return	Ledger	pointer to new Ledger entry (or null)
	 */
	private Ledger getLedgerEntry(Boolean credit) {
		// see if the date and amount are legal
		try {
			when = new SimpleDate( date.getText(), when.year );
			date.setText( when.toString() );
		} catch (NumberFormatException e) {
			JOptionPane.showMessageDialog( thisWindow, 
					e.getMessage(), "INVALID DATE", JOptionPane.ERROR_MESSAGE );
			return null;
		}
		
		// see if the amount is legal
		int amt;
		try {
			amt = Dollars.Parse(amount.getText());
			if (!credit && amt > 0) // double negative probably a mistake
				amt *= -1;
			amount.setText( Dollars.toString(amt) );
		} catch (NumberFormatException e ) {
			JOptionPane.showMessageDialog( thisWindow, 
					e.getMessage(), "INVALID AMOUNT", JOptionPane.ERROR_MESSAGE );
			return null;
		}
		
		return new Ledger( amt, when, description.getText());
	}
	
	/**
	 * reset the fields that should not be preserved after a successful transaction
	 */
	private void cleanup() {
		description.setText("");
		amount.setText("");
		amount.requestFocusInWindow();
	}
	
	
	/**
	 * add the transaction we just processed to a scrollable
	 * window as a confirmation of success
	 * 
	 * @param accountName
	 * @param entry
	 */
	private void log( int accountNum, String accountName, Ledger entry ) {
		
		// add this transaction to the stack
		JournalHistory.push( accountNum, accountName, entry );
		
		// add it to the history display
		lastOps.setText(JournalHistory.dump());
	}
	
	/**
	 * undo the last operation on our stack
	 * 
	 */
	private void undo() {
		
		JournalHistory last = JournalHistory.pop();	// get the last operation off the stack
		if (last != null) {
			books.undo(last.accountNum, last.entry );
			lastOps.setText(JournalHistory.dump());
			if (changeListener != null)
				changeListener.AccountChanged( last.accountNum );
		}
	}
	
	/**
	 * note the object I am to notify whenever I add a
	 * new transaction to some account
	 * 
	 * @param obj
	 */
	public void addAccountChangeListener( AccountChangeListener obj ) {
		changeListener = obj;
	}
	
	private void addTransactionPanel() {
		// create the transaction fill-in panel
		JPanel fillIns = new JPanel(new GridLayout(3,4));
		account = new JComboBox<String>( books.accountNames() );
		account.setSelectedIndex(0);
		date = new JTextField();
		amount = new JTextField();
		amount.addActionListener( this );
		description = new JTextField();
		description.addActionListener( this );
		
		fillIns.add(new JLabel("   Account  "));
		fillIns.add(new JLabel("    Date    "));
		fillIns.add(new JLabel("   Amount   "));
		fillIns.add(new JLabel(" Description"));
		fillIns.add(account);
		fillIns.add(date);
		fillIns.add(amount);
		fillIns.add(description);
		fillIns.add(new JLabel(" "));
		fillIns.add(new JLabel(" "));
		fillIns.add(new JLabel(" "));
		fillIns.add(new JLabel(" "));
		thisWindow.add(fillIns, BorderLayout.NORTH);
		
		// create the input field verifiers
		DateVerifier dateVerifier = new DateVerifier();
		DollarVerifier dollarVerifier = new DollarVerifier();
		date.setInputVerifier(dateVerifier);
		amount.setInputVerifier(dollarVerifier);
	}
	
	private void addButtons() {
		// create the buttons panel
		JPanel buttons = new JPanel();
		debit = new JButton("DEBIT");
		debit.addActionListener(this);
		credit = new JButton("CREDIT");
		credit.addActionListener(this);
		done = new JButton("DONE");
		done.addActionListener(this);
		undo = new JButton("UNDO");
		undo.addActionListener(this);
		buttons.add(debit);
		buttons.add(credit);
		buttons.add(undo);
		buttons.add(done);
		thisWindow.add(buttons, BorderLayout.SOUTH);
	}
	
	
	/**
	 * Widget action listener
	 * 	CREDIT button ... validate input and update the ledger
	 *  DEBIT button ... validate input and update the ledger
	 *  UNDO button ... pop the last trasaction
	 *  DONE button ... shut down the journal window
	 *  amount or description field ... do a DEBIT
	 */
	public void actionPerformed(ActionEvent e) {
		if (e.getSource() == credit ) {
			Ledger c = getLedgerEntry(true);
			if (c != null) {
				books.post(account.getSelectedIndex(), c);
				log( account.getSelectedIndex(),(String) account.getSelectedItem(), c );
				if (changeListener != null)
					changeListener.AccountChanged( account.getSelectedIndex() );
				cleanup();
			}
		} else if (e.getSource() == debit||
				e.getSource() == amount ||
				e.getSource() == description ) {
			Ledger d = getLedgerEntry(false);
			if (d != null) {
				books.post(account.getSelectedIndex(), d);
				log( account.getSelectedIndex(),(String) account.getSelectedItem(), d );
				if (changeListener != null)
					changeListener.AccountChanged( account.getSelectedIndex() );
				cleanup();
			}
		} else if (e.getSource() == done ) {
			thisWindow.dispose();
		} else if (e.getSource() == undo ) {
			undo();
		}
	}
	
	/**
	 * The only window event I care about is shutdown, which
	 * we handle by promptly shutting down
	 */
	public void windowClosing(WindowEvent e) {
		thisWindow.setVisible( false );
		thisWindow.dispose();
	}
	
	public void windowActivated(WindowEvent arg0) {	}
	public void windowClosed(WindowEvent arg0) {	}
	public void windowDeactivated(WindowEvent arg0) {}
	public void windowDeiconified(WindowEvent arg0) {}
	public void windowIconified(WindowEvent arg0) {}
	public void windowOpened(WindowEvent arg0) {}
}
