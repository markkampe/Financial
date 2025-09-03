package accounting;
import java.awt.*;
import java.awt.event.*;
import java.io.*;
import java.text.*;

import javax.swing.*;
import javax.swing.event.*;
import javax.swing.filechooser.FileNameExtensionFilter;

/**
 * This class deals with the main-screen widgets and kicks
 * off various operations (and other windows) in response to
 * actions on those widgets.
 */
public class MainScreen extends JFrame 
						implements	AccountChangeListener,
									ActionListener, 
									ListSelectionListener,
									WindowListener {
	
	private static final long serialVersionUID = 0xdeadbeef;	// this is stupid
	
	// font for rendering columnar numbers (less arbitrary than you might think)
	private final static String DISPLAY_FONT = "Monospaced";
	private final static int DISPLAY_SIZE = 12;
	
	// desired window sizes (calling pack renders these obsolete)
	// private static final int WIDTH = 700;
	// private static final int HEIGHT = 500;
	
	// icon for this application
	private static final String ICON_IMAGE = "images/accounting-icon-32.png";
	
	// used for date selector combo-boxes
	private static final String months[] = {
		"Jan", "Feb", "Mar", "Apr", "May", "Jun",
		"Jul", "Aug", "Sep", "Oct", "Nov", "Dec" };
	private static final String days[] = {  
		"1",  "2",  "3",  "4",  "5",  "6",  "7",  "8", "9", "10",
		"11", "12", "13", "14", "15", "16", "17", "18", "19","20",
		"21", "22", "23", "24", "25", "26", "27", "28", "29","30",
		"31" };

	private static final String Null = null;
	
	// internal state on which we operate
	private String fileName;		// name of the file we are processing
	private AccountsFile file;		// file manipulation object
	private Books books;			// the set of books on which we operate
	private SimpleDate refDate;		// reference date for balances

	// GUI widgets
	private Container mainPane;
	private JComboBox<String> monthSelector;
	private JComboBox<String> daySelector;
	private JTextField yearField;
	private JList<String> summaryList;
	private DefaultListModel<String> summaryModel;
	
	// menu items
	private JMenuItem fileOpen;
	private JMenuItem fileSave;
	private JMenuItem fileSaveAs;
	private JMenuItem fileClose;
	private JMenuItem fileExit;
	private JMenuItem editBudget;
	private JMenuItem editJournal;
	private JMenuItem editTransact;
	private JMenuItem editSoil;	// for testing
	private JMenuItem viewRefresh;
	private JMenuItem viewAnalysis;
	
	Options opts;		// run time options

	/**
	 * create all the main-screen widgetry
	 * 
	 * @param booksFileName String
	 * 
	 * NOTE:
	 * 	startup for this instance seems to be very expensive.
	 * 	I speculate this is because it creates a window.
	 */
	public MainScreen( String booksFileName, SimpleDate when )  {
		
		TimeStamp.logEvent("start MainScreen");
		
		// run time options
		opts = Options.getInstance();
		
		// we start out with nothing
		file = null;
		books = null;
		refDate = when;
		
		// get our window icon ... no longer works!!!
		//		getResource is returning the expected URL
		//		getImage is not reporting failure
		//		setIconImage is not reporting failure
		//		but the window icons are not changing!!!
		Image myIcon = getToolkit().getImage(getClass().getResource(ICON_IMAGE));
		setIconImage(myIcon);
		
		// get a handle on our primary window
		mainPane = getContentPane();
		addWindowListener( this );
		setDefaultCloseOperation(WindowConstants.DO_NOTHING_ON_CLOSE);
		
		// create our menu hierarchy
		createMenus();
		
		// create the (initally blank) summary screen
		createSummaryScreen();
		
		// create the date selector
		createDateSelector();
		
		// open the input file (and populate the display)
		TimeStamp.logEvent("open logfile");
		if (booksFileName != null && booksFileName != "")
			newFile( booksFileName );
		
		// if we don't have an open file, set everything to closed
		if (books == null)
			closeFile();
		
		// This too seems to be a very expensive operation
		//	probably because it is creating all the pixels
		TimeStamp.logEvent("expose");
		setVisible( true );	
		
		// validate widgets and auto-compute display size
		pack();
		
		TimeStamp.logEvent("done");
	}
	
	
	/**
	 * update the displayed summary
	 * 
	 * @param	boolean	should we force balance recomputation
	 */
	private void update( boolean force ) {
		// discard everything currently being displayed
		summaryModel.removeAllElements();
		
		// if there are no open books, there is no display to update
		if (books == null)
			return;
		
		// update the balances if necessary
		books.getBalances(refDate, force);
		
		// update the on-screen summary
		String[] summary = books.summary(false);
		for( int i = 0; i < summary.length; i++ ) {
			summaryModel.add(i, summary[i]);
		}
	}
	
	/**
	 * this method is invoked whenever a JournalWindow
	 * updates some account.
	 */
	public void AccountChanged( int acctNum ) {
		update( false );
	}
	
	/**
	 * put up a budget confirmation dialog,
	 * if confirmed, it will come back with a selected month
	 * add budget, for that month, to each account
	 */
	private boolean addBudget() {

		// put up a confirmation dialog
		Object chosen = JOptionPane.showInputDialog(mainPane, "Choose Month", "ADD MONTHLY BUDGET",
				JOptionPane.INFORMATION_MESSAGE, null, months, months[refDate.month - 1]);
		
		// if nothing was chosen, forget it
		if (chosen == null)
			return false;
			
		// see which month was chosen
		for( int i = 0; i < months.length; i++ ) {
			if (chosen == months[i]) {
				int month = i+1;
				int year = refDate.year;
				return books.addBudget( new SimpleDate(year, month, 1));
			}
		}
		
		return false;	// no month matched?
	}
	
	/**
	 * load a previously prepared transaction journal
	 */
	private boolean loadTransactions() {
		// get a transaction file
		JFileChooser fc = new JFileChooser();
		if (fc.showOpenDialog(null) != JFileChooser.APPROVE_OPTION) 
			return false;
		String chosen = "";
		BufferedReader reader = null;
		try {
			chosen = fc.getSelectedFile().getAbsolutePath();
			File file = new File(chosen);
			if (!file.exists())
				throw new FileNotFoundException("file does not exist");
			reader = new BufferedReader( new FileReader( chosen ));
		} catch (FileNotFoundException err) {
			JOptionPane.showMessageDialog( mainPane, 
					err.getMessage() 
					+ "\nFile: " + chosen,
					"UNABLE TO OPEN TRANSACTION FILE", JOptionPane.ERROR_MESSAGE );
			return false;
		} 
		
		// Process every line in that file
		int lines = 0;		
		try {
			int entries = 0;
			int ignored = 0;
			int warns = 0;
			int noAcct = 0;
			for(String line = reader.readLine(); line != null; line = reader.readLine()) {
				lines++;
				// ignore empty lines
				line = line.trim();
				if (line.length() == 0)
					continue;
				
				// try a simple comma-split (and pray that it works)
				String[] fields = line.split(",");
				if (fields.length < 4) {
					reader.close();
					throw new ParseException("TOO FEW FIELDS", lines);
				} else if (fields.length > 4) {
					reader.close();
					throw new ParseException("TOO MANY FIELDS", lines);
				} else if (lines == 1 && ("Date".equals(fields[0]) || "date".equals(fields[0])))
					continue;
				
				// see if we recognize the account name
				String acctName = fields[2].trim();
				if (acctName == Null || acctName.equals("")) {
					noAcct++;
					continue;
				}
				int account = books.accountNumber(acctName);
				if (account < 0) {
					JOptionPane.showMessageDialog(mainPane,
							"File: " + chosen + ". line " + lines +
							"\nUNRECOGNIZED ACCOUNT: " + acctName);
					continue;
				}
				
				if (books.isWarned(account)) {
					warns++;
					System.err.println("WARNING: transaction against ignored account " + acctName);
				}
				
				if (books.isIgnored(account)) {
					ignored++;
					continue;
				}
		
				// parse the date, amount, and description
				SimpleDate date = new SimpleDate(fields[0], refDate.year);
				int amount = Dollars.Parse(fields[1]);
				String descr = "";
				if (fields.length == 4) {
					descr = fields[3].trim();
					if ((descr.startsWith("\"") && descr.endsWith("\"")) ||
						(descr.startsWith("'") && descr.endsWith("'")))
							descr = descr.substring(1, descr.length() - 1);
				}
				
				// and add it to our books
				Ledger entry = new Ledger(amount, date, descr);	
				if (books.post(account, entry)) {
					entries++;
					continue;
				} else {
					reader.close();
					throw new ParseException("UNABLE TO POST", lines);
				}	
			} 
			reader.close();
			
			// display a processing confirmation dialog
			String message = "File: " + chosen + 
					"\nLines: " + lines +
					"\nProcessed: " + entries;
			if (ignored > 0) {
				message = message + "\nIgnored: " + ignored;
				if (warns > 0)
					message = message + " (" + warns + " warnings)";
			}
			if (noAcct > 0)
				message += "\nNo Account: " + noAcct;
			JOptionPane.showMessageDialog(mainPane, message);
			return true;
		} catch (ParseException err) {
			JOptionPane.showMessageDialog( mainPane,
						err.getMessage()
						+ "\nFile: " + chosen + ", line: " + err.getErrorOffset(),
						"ERROR PROCESSING TRANSACTION FILE", JOptionPane.ERROR_MESSAGE );
		} catch (NumberFormatException err) {
			JOptionPane.showMessageDialog( mainPane,
						err.getMessage()
						+ "\nFile: " + chosen + ", line: " + lines,
						"ERROR PROCESSING TRANSACTION FILE", JOptionPane.ERROR_MESSAGE );
		} catch (IOException err ) {
			JOptionPane.showMessageDialog( mainPane, 
					err.getMessage() 
					+ "\nFile: " + chosen,
					"ERROR LOADING TRANSACTION FILE", JOptionPane.ERROR_MESSAGE );
		}
		return false;
	}
	
	/**
	 * open a specified file as our set of books
	 */
	private void newFile( String filename ) {
		// allocate a new set of books
		books = new Books();
		
		// see if we can open our input ledger
		try {	
			file = new AccountsFile( filename, books );
			file.read(refDate.year);
			fileName = filename;
		} catch (FileNotFoundException e ) {	
			JOptionPane.showMessageDialog( mainPane, "File: " + filename, 
					"UNABLE TO OPEN INPUT FILE", JOptionPane.ERROR_MESSAGE );
			file = null;
			fileName = "NONE";
		} catch (ParseException e ) {
			JOptionPane.showMessageDialog( mainPane, 
					e.getMessage() 
					+ "\nFile: " + filename
					+ "\nLine: " + e.getErrorOffset(),
					"ERROR PROCESSING INPUT FILE", JOptionPane.ERROR_MESSAGE );
		} catch (IOException e ) {
			JOptionPane.showMessageDialog( mainPane, 
					e.getMessage() 
					+ "\nFile: " + filename,
					"ERROR READING INPUT FILE", JOptionPane.ERROR_MESSAGE );
		}
	
		if (file != null) {
			// set our screen title
			setTitle( fileName );
			
			// enable the open file functions
			fileSave.setEnabled(opts.writeable);
			fileSaveAs.setEnabled(opts.writeable);
			fileClose.setEnabled(true);
			editBudget.setEnabled(opts.writeable);
			editJournal.setEnabled(opts.writeable);
			editSoil.setEnabled(opts.writeable);
			viewAnalysis.setEnabled(true);
		
			// and update the display
			update( true );
		}
	}
	
	/**
	 * process a shut-down command or window-close event
	 * 	see if we need to save, do a save dialog, save
	 */
	private void shutdown() {
		if (closeFile())
			System.exit(0);
	}
	
	/**
	 * process a close file request
	 * 	see if we have any changes to save, and if
	 * 	so put up a save dialog, and do the save
	 * 
	 * @return	is everything now OK?
	 */
	private boolean closeFile() {
		if (books != null && opts.writeable && !books.clean()){
			int choice = JOptionPane.showConfirmDialog(mainPane,
				"Save changes to " + fileName);
		
			if (choice == JOptionPane.CANCEL_OPTION) {
				return false;		// no harm done
			}
			
			if (choice == JOptionPane.YES_OPTION) {
				try {
					file.save();
				} catch (IOException e) {
					JOptionPane.showMessageDialog( mainPane, 
							e.getMessage() 
							+ "\nFile: " + fileName,
							"ERROR UPDATING FILE", JOptionPane.ERROR_MESSAGE );
				}
			}
		}
		
		// this file is old news, so clear it out
		if (file != null) {
			file.close();
			file = null;
		}
		books = null;
		fileName = "NONE";
		
		// disable the open file functions
		fileSave.setEnabled(false);
		fileSaveAs.setEnabled(false);
		fileClose.setEnabled(false);
		editBudget.setEnabled(false);
		editJournal.setEnabled(false);
		editTransact.setEnabled(false);
		editSoil.setEnabled(false);
		viewAnalysis.setEnabled(false);
		
		update(false);
		return true;
	}
		
	
	/**
	 * create the hierarchy of menus that will drive most 
	 * of our actions
	 */
	private void createMenus() {
		
		// create File menu
		fileOpen = new JMenuItem("Open");
		fileOpen.addActionListener(this);
		fileSave = new JMenuItem("Save");
		fileSave.addActionListener(this);
		fileSaveAs = new JMenuItem("Save as");
		fileSaveAs.addActionListener(this);
		fileClose = new JMenuItem("Close file");
		fileClose.addActionListener(this);
		fileExit = new JMenuItem("Exit");
		fileExit.addActionListener(this);
		JMenu fileMenu = new JMenu("File");
		fileMenu.add(fileOpen);
		fileMenu.add(fileSave);
		fileMenu.add(fileSaveAs);
		fileMenu.add(fileClose);
		fileMenu.add( new JSeparator() );
		fileMenu.add(fileExit);
		
		// create our edit menu
		editBudget = new JMenuItem("add budget");
		editBudget.addActionListener(this);
		editJournal = new JMenuItem("Journal");
		editJournal.addActionListener(this);
		editTransact = new JMenuItem("load transactions");
		editTransact.addActionListener(this);
		editSoil = new JMenuItem("null change");
		editSoil.addActionListener(this);
		JMenu editMenu = new JMenu("Edit");
		editMenu.add(editBudget);
		editMenu.add(editJournal);
		editMenu.add(editTransact);
		editMenu.add( new JSeparator() );
		editMenu.add(editSoil);
		
		// create our view menu
		viewRefresh = new JMenuItem("Refresh");
		viewRefresh.addActionListener(this);
		viewAnalysis = new JMenuItem("Analysis");
		viewAnalysis.addActionListener(this);
		JMenu viewMenu = new JMenu("View");
		viewMenu.add(viewRefresh);
		viewMenu.add(viewAnalysis);
		
		// assemble the menu bar
		JMenuBar menuBar = new JMenuBar();
		menuBar.add(fileMenu);
		menuBar.add( editMenu );
		menuBar.add( viewMenu );
		setJMenuBar( menuBar );	
	}
	
	
	/**
	 * The action handler from hell ... it gets everything
	 */
	public void actionPerformed( ActionEvent e ) {
		Object o = e.getSource();
		
		// change of the as-of date
		if (o == monthSelector || o == daySelector || o == yearField) {
			changeRefDate();
		} 
		
		if (o == fileOpen) {
			// close the existing file
			if (!closeFile())
				return;
			
			// get a new file name
			JFileChooser fc = new JFileChooser();
			fc.setFileFilter( new FileNameExtensionFilter("Ledgers/Backups (.act/.bak)", "act", "bak" ));
			if (fc.showOpenDialog(null) == JFileChooser.APPROVE_OPTION) {
				newFile( fc.getSelectedFile().getAbsolutePath() );
			}
			return;
		}
		
		if (o == fileSave && opts.writeable && books != null) {
			try {
				file.save();
			} catch (IOException err ) {
				JOptionPane.showMessageDialog( mainPane, 
						err.getMessage() 
						+ "\nFile: " + fileName,
						"ERROR UPDATING FILE", JOptionPane.ERROR_MESSAGE );
			}
			return;
		}
		
		if (o == fileSaveAs && opts.writeable && books != null) {
			JFileChooser fc = new JFileChooser(fileName);
			if (fc.showSaveDialog(null) == JFileChooser.APPROVE_OPTION) {
				String chosen = "";
				try {
					chosen = fc.getSelectedFile().getAbsolutePath();
					file.saveAs( chosen );
				} catch (IOException err ) {
					JOptionPane.showMessageDialog( mainPane, 
							err.getMessage() 
							+ "\nFile: " + chosen,
							"ERROR UPDATING FILE", JOptionPane.ERROR_MESSAGE );
				}
			}
			return;
		}
		
		if (o == fileClose) {
			if (closeFile()) {
				setTitle("NONE");
			}
			return;
		}
		
		if (o == fileExit) {
			shutdown();
			return;
		}
		
		if (o == editBudget && opts.writeable && books != null) {
			if (addBudget()) {
				update( false );
			}
			return;
		}
		
		if (o == editJournal && opts.writeable && books != null) {
			JournalWindow j = new JournalWindow(books, refDate );
			j.addAccountChangeListener( this );
			return;
		}
		
		if (o == editTransact && opts.writeable && books != null) {
			if (loadTransactions()) {
				update( false );
			}
			return;
		}
		
		if (o == editSoil && opts.writeable && books != null) {
			books.clean(false);
			return;
		}
		
		if (o == viewRefresh) {
			update(true);
			return;
		}
		
		if (o == viewAnalysis && books != null) {
			String[] dump = books.analysis();
			String title = "Budget vs Expenses Analysis (since " + refDate.toString() + ")";
			new BrowseWindow( title, dump );
			
			// and then re-recompute the balances relative to refDate
			books.getBalances(refDate, true);
			return;
		}
	}
	
	
	/**
	 * create a scrollable/selectable list in which we will display the
	 * basic account balance information.
	 */
	private void createSummaryScreen() {
		summaryModel = new DefaultListModel<String>();
		
		summaryList = new JList<String>( summaryModel );
		summaryList.setFont( new Font( DISPLAY_FONT, Font.PLAIN, DISPLAY_SIZE ));
		summaryList.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);
		
		ListSelectionModel lsm = summaryList.getSelectionModel();
		lsm.addListSelectionListener(this);
		
		mainPane.add(summaryList, BorderLayout.CENTER);
	}
	
	/**
	 * list selection even handler for account summary screen
	 */
	public void valueChanged( ListSelectionEvent e ) {
		// if the button is still down, ignore it
		if (e.getValueIsAdjusting())
			return;
		
		// if nothing is selected, ignore it
		ListSelectionModel lsm = (ListSelectionModel) e.getSource();
		if (lsm.isSelectionEmpty())
			return;
		
		// if a valid account has been selected, generate a detailed ledger
		int acct = lsm.getMinSelectionIndex() - 1;
		
		// if there is nothing in that account, ignore it
		String dump[] = books.ledgerDump(acct);
		if (dump == null)
			return;
		
		// kick off a new sub-window for the dump
		String title = "Ledger for account: " + books.accountName(acct);
		new BrowseWindow( title, dump );
	}
	
	/**
	 * create the combo-boxes and input fields for date selection
	 * and put them in the bottom of our window
	 */
	private void createDateSelector() {
		// create the combobox
		monthSelector = new JComboBox<String>( months );
		monthSelector.setSelectedIndex(refDate.month-1);
		monthSelector.addActionListener(this);
		daySelector = new JComboBox<String>( days );
		daySelector.setSelectedIndex(refDate.day-1);
		daySelector.addActionListener(this);
		yearField = new JTextField( "" + refDate.year );
		yearField.addActionListener(this);
		
		// add these to a Jpanel for date selection
		JPanel dateSelector = new JPanel(new FlowLayout(FlowLayout.LEADING));
		dateSelector.add(new JLabel( "balances relative to" ));
		dateSelector.add( monthSelector );
		dateSelector.add( daySelector );
		dateSelector.add( yearField );
		
		mainPane.add( dateSelector, BorderLayout.SOUTH );
	}
	
	/**
	 * the reference date selector has changed
	 * 	figure out what the new reference date is
	 * 	and then update the display accordingly
	 */
	private void changeRefDate() {
		int month = monthSelector.getSelectedIndex() + 1;
		int day   = daySelector.getSelectedIndex() + 1;
		int year  = Integer.parseInt(yearField.getText());
		refDate = new SimpleDate(year, month, day);
		
		update( true );
	}
	
	/**
	 * window close event handler
	 * 	this is the only one I really wanted to catch,
	 * 	so I can force a save dialog
	 */
	public void windowClosing(WindowEvent e) {
			shutdown();
	}
	
	public void windowActivated(WindowEvent arg0) {	}
	public void windowClosed(WindowEvent arg0) {}
	public void windowDeactivated(WindowEvent arg0) {}
	public void windowDeiconified(WindowEvent arg0) {}
	public void windowIconified(WindowEvent arg0) {}
	public void windowOpened(WindowEvent arg0) {}
}
