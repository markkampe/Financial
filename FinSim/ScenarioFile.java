package FinSim;
import java.io.*;
import java.text.ParseException;

/**
 * This class translates between the in-memory (books)
 * representation and the on-disk (accounts file)
 * representation of a complete ledger of accounts.
 * 
 * @author mkampe
 */
public class ScenarioFile {
	
	private static final String BACK_SUFFIX = ".bak";
	
	private String fileName;	// name of chosen input file
	private boolean fileOpen;	// do we have something to process
	
	private Options opts;		// run time options

	/**
	 * open the file and see if we can read it
	 * 
	 * @param filename name of ledger file to process
	 */
	public ScenarioFile( String filename ) throws FileNotFoundException {
		
		if (opts == null)
			opts = Options.getInstance();
		
		if (filename == null || filename.isEmpty() || filename == "NONE") {
			fileOpen = false;
			throw new FileNotFoundException("no input file specified");
		}
				
		if (!(new File(filename)).exists()) {
			fileOpen = false;
			throw new FileNotFoundException("file does not exist");
		}
		
		// SOMEDAY figure out what else opening a new file means
		
		fileName = filename;
		if (opts.debugFile)
			System.out.println("Open Input file " + fileName + " ... OK" );
		fileOpen = true;
	}
	
	/**
	 * SOMEDAY figure out what reading an input file means
	 * 
	 * @throws	IOException	file read errors
	 * @throws	ParseException input format errors
	 */
	public void read( ) throws ParseException, IOException {
		if (!fileOpen)
			throw new IOException("No input file");;
		
		BufferedReader reader = new BufferedReader( new FileReader( fileName ));
		
		int lineNum = 0;
		for(String line = reader.readLine(); line != null; line = reader.readLine()) {
			lineNum++;
			// SOMEDAY figure out what we are reading
		}
		if (opts.debugFile)
			System.out.println("Read Input file " + 
					fileName + ", " + lineNum + " lines ... OK");
		
		// we're done with the open stream 
		reader.close();
	}

	/**
	 */
	private void write( String filename ) throws IOException {
		
		if (!fileOpen)
			throw new IOException("No file to write out");
		
		FileWriter output = new FileWriter( filename );
		
		// SOMEDAY figure out what it means to write out a file
		
		if (opts.debugFile)
			System.out.println("Write output file " + filename + " ... OK");
		
		output.close();
	}
	
	/**
	 * reset all the state associated with the current file
	 */
	public void close() {
	
		// SOMEDAY what else is involved in having no input file
		
		if (opts.debugFile)
			System.out.println("Close file " + fileName + " ... OK");
		
		fileName = "NONE";
		fileOpen = false;
	}
	
	/**
	 * if the specified file already exists, move it to a backup name
	 */
	private void backup(String name) {
		// if there is no such file, there is nothing to do
		File chosen = new File( name );
		if (!chosen.exists())
			return;
			
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
		
		if (opts.debugFile)
			System.out.println("Rename old file " + 
					currentName + " to " + backupName + " ... OK");
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
		
		if (fileOpen) {
			backup( name );		// backup the file
			write( name );		// write out the books
		}
	}
}