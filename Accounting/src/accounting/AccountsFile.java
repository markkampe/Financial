package accounting;
import java.io.*;
import java.text.ParseException;

/**
 * This class translates between the in-memory (books)
 * representation and the on-disk (accounts file)
 * representation of a complete ledger of accounts.
 * 
 * @author mkampe
 */
public class AccountsFile {
	private static final Boolean WRITE_ANALYSIS = true;
	
	// strings we write into the books (and expect to read back)
	private static final String ACCT_TAG = "ACCOUNT: ";
	private static final String BUDGET_TAG = "Budget: ";
	private static final String BALANCE_TAG = "Balance: ";
	private static final String END_TAG = "END";
	private static final String IGNORE_TAG = "IGNORE: ";
	private static final String IGNORE_WARN_TAG = "IGNORE! ";
	private static final String ANALYSIS_HEADER = "Performance vs Budget for entire year";
	
	// characters that introduce a comment line
	private static final String COMMENT_CHARS = "#/*";
	
	private static final String BACK_SUFFIX = ".bak";

	private String fileName;	// file being processed
	private Books books;		// books being processed
	
	/**
	 * open the file and see if we can read it
	 * 
	 * @param filename name of ledger file to process
	 */
	public AccountsFile( String filename, Books theseBooks ) throws FileNotFoundException {
		
		books = null;		// we aren't enabled until we find the file
		
		if (filename == "NONE")
			return;
			
		if (!(new File(filename)).exists())
			throw new FileNotFoundException("file does not exist");
			
		fileName = filename;
		books = theseBooks;
	}
	
	/**
	 * read the currently open accounts file,
	 * creating the described, books, accounts, and ledger entries
	 * 
	 * @param	dfltYear	default year to use (for entries that lack them)
	 * 						This may seem bogus, but old files had no years
	 * 						in them, so I may need outside (e.g. human) input
	 * 						to figure out what year we are talking about.
	 * 
	 * @param	Books object (containing accounts, containing ledger entries)
	 * 
	 * @throws	IOException	file read errors
	 * @throws	ParseException input format errors
	 */
	public void read( int dfltYear ) throws ParseException, IOException {
		if (fileName == "NONE")
			throw new IOException("No such file");;
		
		BufferedReader reader = new BufferedReader( new FileReader( fileName ));
		
		int acct = -1;	// account we are processing
		int lineNum = 0;
		for(String line = reader.readLine(); line != null; line = reader.readLine()) {
			lineNum++;
			
			// ignore empty lines
			line = line.trim();
			if (line.length() == 0)
				continue;
			
			// ignore comment lines
			char c = line.charAt(0);
			if (COMMENT_CHARS.indexOf(c) >= 0)
				continue;
		
			// is this a "stop reading" indicator
			if (line.startsWith(END_TAG))
				break;
			
			if (line.startsWith(IGNORE_TAG)) {	// is this an account to be ignored
				// lex off the account name
				int nameStart = IGNORE_TAG.length();
				String name = line.substring(nameStart);
				books.addIgnored(name, false);
			} else if (line.startsWith(IGNORE_WARN_TAG)) {	// ignore and warn
				// lex off the account name
				int nameStart = IGNORE_TAG.length();
				String name = line.substring(nameStart);
				books.addIgnored(name, true);
			} else if (line.startsWith(ACCT_TAG)) {	// is this a new account
				// lex off the account name
				int nameStart = ACCT_TAG.length();
				int nameEnd = line.indexOf(' ', nameStart );
				String name = line.substring(nameStart, nameEnd);
				
				// lex off the budget
				int budget = 0;
				int bgtStart = line.indexOf(BUDGET_TAG, nameEnd);
				if (bgtStart > nameEnd) {
					line = line.substring( bgtStart + BUDGET_TAG.length() );
					line = line.trim();
					int bgtEnd = line.indexOf(' ');
					if (bgtEnd < 2) {
						reader.close();
						throw new ParseException("missing budget", lineNum );
					}
					try {
						budget = Dollars.Parse( line.substring(0,bgtEnd) );
					} catch ( NumberFormatException e ) {
						reader.close();
						throw new ParseException( e.getMessage() + " in budget", lineNum );
					}
				}
				
				// create the new account
				acct = books.addAccount(name, budget);
			} else { // this is a journal entry within an account
				// it should start with a date
				int dateStart = 0;
				int dateEnd = nextWhiteSpace( line, dateStart );
				if (dateEnd < dateStart+2) {
					reader.close();
					throw new ParseException("missing transaction date", lineNum );
				}
				SimpleDate when = null;
				try {
					when = new SimpleDate(line.substring(dateStart, dateEnd), dfltYear);
				} catch (NumberFormatException e) {
					reader.close();
					throw new ParseException(e.getMessage() + " in transaction date", lineNum );
				}
				
				// next field should be the amount
				int amount = 0;
				line = line.substring(dateEnd);
				line = line.trim();
				if (line.length() < 2) {
					reader.close();
					throw new ParseException("missing transaction amount", lineNum);
				}
				int amountEnd = nextWhiteSpace( line, 0 );
				if (amountEnd < 0)
					amountEnd = line.length();
				try {
					amount = Dollars.Parse( line.substring(0,amountEnd));
				} catch (NumberFormatException e) {
					reader.close();
					throw new ParseException(e.getMessage() + " in transaction amount", lineNum);
				}
				
				// parse off the comments (if any)
				line = line.substring(amountEnd);
				String comment = line.trim();
				
				// create the new ledger entry
				Ledger entry = new Ledger( amount, when, comment );
				books.post(acct, entry);
			}	
		}
		
		// we're done with the open stream 
		reader.close();
		
		// all of these transactions are already in the ledger
		books.clean(true);
	}

	/**
	 * write out the current set of books
	 * 	for each account
	 * 		write out an account line
	 * 		for each ledger entry
	 * 			dump it out
	 */
	private void write( String filename ) throws IOException {
		FileWriter output = new FileWriter( filename );
		
		// for each account
		for( int i = 0; i < books.numAccounts(); i++ ) {
			if (books.isIgnored(i))
				continue;
			
			output.write( ACCT_TAG + books.accountName(i) + "    "
					+ BUDGET_TAG + Dollars.toString(books.accountBudget(i)) + "/mo     " 
					+ BALANCE_TAG + Dollars.toString(books.finalBalance(i)) + "\n" );
			
			// for each ledger entry
			String dump[] = books.ledgerDump(i);
			for( int j = 0; j < dump.length; j++ ) {
				output.write( "        " + dump[j] + "\n" );
			}
			
			output.write("\n");
		}
		
		// for each ignored account
		for( int i = 0; i < books.numAccounts(); i++ ) {
			if (books.isIgnored(i)) {
				output.write(books.isWarned(i) ? IGNORE_WARN_TAG : IGNORE_TAG);
				output.write( books.accountName(i) + "\n");
			}
		}
		
		// see if we should also output an analysis
		if (WRITE_ANALYSIS) {	
			output.write("\n" + END_TAG + "\n");
			
			String comment = COMMENT_CHARS.substring(0,1);
			output.write(comment + "\n");
			output.write(comment + " " + ANALYSIS_HEADER + "\n");
			output.write(comment + "\n");
			output.write(comment + " " + "NOTES:" + "\n");
			output.write(comment + "    " + "bgt-deb: budget - debits" + "\n");
			output.write(comment + "    " + "bal/bgt: % balance vs budget" + "\n");
			output.write(comment + "    " + "exp/bgt: % expenses vs budget" + "\n");
			output.write(comment + "    " + "exp/tot: % expenses vs budget+credits" + "\n");
			output.write(comment + "\n");
			
			String dump[] = books.analysis();
			for( int i = 0; i < dump.length; i++ ) {
				if (dump[i] != null)
					output.write( dump[i] + "\n" );
			}

			// explanatory notes
		}
		output.close();
	}
	
	public void close() {
		books = null;
		fileName = "NONE";
	}
	
	/**
	 * find the next white-space character in a string
	 * 
	 * @param	string to be searched
	 * @param	starting index for search
	 * 
	 * @return	index of the first whitespace character
	 */
	private int nextWhiteSpace( String string, int startingAt ) {
		int nextSpace = string.indexOf( ' ', startingAt );
		int nextTab = string.indexOf( '\t', startingAt );
		
		if (nextSpace == -1)
			return nextTab;
		if (nextTab == -1)
			return nextSpace;
		if (nextTab < nextSpace)
			return nextTab;
		return nextSpace;
	}
	
	/**
	 * if the specified file already exists, move it to a backup name
	 */
	private void backup(String name) {
		// if there is no such file, there is nothing to do
		File chosen = new File( name );
		if (!chosen.exists())
			return;
			
		// FIXME - does not always create .bak
		//	I was editing rem12.act and the write blew up in a zero-divide
		//	and no .bak was created
		
		// figure out what to call the backup;
		String currentName = chosen.getName();
		String backupName;
		int dot = currentName.indexOf('.');
		if (dot < 0) {
			backupName = chosen.getParent() + "/" + currentName + BACK_SUFFIX;
		} else {
			backupName = chosen.getParent() + "/" + currentName.substring(0,dot) + BACK_SUFFIX;
		}
		
		// if the backup file already exists, delete it
		File save = new File( backupName );
		if (save.exists()) {
			save.delete();
		}
		
		// rename the current file to the backup name
		chosen.renameTo(save);
	}
	
	/**
	 * save the current file
	 */
	public void save( ) throws IOException {
		saveAs( fileName );
	}
	
	/**
	 * save the current file to a specified name
	 * 
	 * @param name
	 */
	public void saveAs( String name ) throws IOException {
		
		if (books != null) {
			backup( name );		// backup the file
			write( name );		// write out the books
			books.clean(true);		// in-memory == persistent
		}
	}
}

