package FinSimGui;
import java.awt.*;
import java.awt.event.*;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.text.ParseException;
import javax.swing.*;

/**
 * This class deals with the main-screen widgets and kicks
 * off various operations (and other windows) in response to
 * actions on those widgets.
 */
public class MainScreen extends JFrame 
						implements	ActionListener, 
									WindowListener {
	
	private static final long serialVersionUID = 0xdeadbeef;	// this is stupid
	
	// font for rendering columnar numbers (less arbitrary than you might think)
	// private final static String DISPLAY_FONT = "Lucida Sans Typewriter Regular";
	// private final static int DISPLAY_SIZE = 12;
	
	// desired window sizes
	private static final int WIDTH = 700;
	private static final int HEIGHT = 500;
	
	// icon for this application
	private static final String ICON_IMAGE = "images/accounting-icon-32.png";
	
	// General state
	private static String chosenFile;
	private ScenarioFile file;
	private boolean dirty;
	
	// GUI widgets
	private Container mainPane;
	
	// menu items
	private JMenuItem fileOpen;
	private JMenuItem fileSave;
	private JMenuItem fileSaveAs;
	private JMenuItem fileClose;
	private JMenuItem fileExit;
	private JMenuItem viewRefresh;
	
	Options opts;		// run time options

	/**
	 * create all the main-screen widgetry
	 * 
	 * @param file to process
	 */
	public MainScreen( String filename )  {

		// run time options
		opts = Options.getInstance();
		
		// get our window icon
		Image myIcon = getToolkit().getImage(getClass().getResource(ICON_IMAGE));
		setIconImage(myIcon);
		
		// get a handle on our primary window
		mainPane = getContentPane();
		addWindowListener( this );
		setDefaultCloseOperation(WindowConstants.DO_NOTHING_ON_CLOSE);
		
		// create our menu hierarchy
		createMenus();
		
		// lay it out, set the size, and make it visible
		setSize(WIDTH, HEIGHT);
		mainPane.validate();
		setVisible( true );	
		
		// if an input file was specified, process it
		if (filename != null && !filename.isEmpty())
			newFile( filename );
	}

	/**
	 * open and process a specified input file
	 */
	private void newFile( String filename ) {
		
		// see if we can open our input ledger
		try {	
			file = new ScenarioFile( filename );
			file.read();
			chosenFile = filename;
		} catch (FileNotFoundException e ) {	
			JOptionPane.showMessageDialog( mainPane, "File: " + filename, 
					"UNABLE TO OPEN INPUT FILE", JOptionPane.ERROR_MESSAGE );
			chosenFile = "NONE";
			file = null;
			return;
		} catch (ParseException e ) {
			JOptionPane.showMessageDialog( mainPane, 
					e.getMessage() 
					+ "\nFile: " + filename
					+ "\nLine: " + e.getErrorOffset(),
					"ERROR PROCESSING INPUT FILE", JOptionPane.ERROR_MESSAGE );
			file = null;
			return;
		} catch (IOException e ) {
			JOptionPane.showMessageDialog( mainPane, 
					e.getMessage() 
					+ "\nFile: " + filename,
					"ERROR READING INPUT FILE", JOptionPane.ERROR_MESSAGE );
			file = null;
			return;
		}
	
		// we've made no changes
		dirty = false;
		
		// set our screen title
		setTitle( chosenFile );

		// enable the open file functions
		fileSave.setEnabled(!opts.readOnly);
		fileSaveAs.setEnabled(!opts.readOnly);
		fileClose.setEnabled(true);
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
		
		if (file != null && !opts.readOnly && dirty){
			int choice = JOptionPane.showConfirmDialog(mainPane,
				"Save changes to " + chosenFile );
		
			if (choice == JOptionPane.CANCEL_OPTION) {
				return false;		// no harm done
			}
			
			if (choice == JOptionPane.YES_OPTION) {
				try {
					file.save();
				} catch (IOException e) {
					JOptionPane.showMessageDialog( mainPane, 
							e.getMessage() 
							+ "\nFile: " + chosenFile,
							"ERROR UPDATING FILE", JOptionPane.ERROR_MESSAGE );
				}
			}
		}
	
		// if we had a file open, it isn't open any more
		if (file != null) {
			chosenFile = "NONE";
			file.close();
			file = null;
		}
		
		// disable the open file functions
		fileSave.setEnabled(false);
		fileSaveAs.setEnabled(false);
		fileClose.setEnabled(false);
		
		// and there is nothing to save
		dirty = false;

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
		JMenu editMenu = new JMenu("Edit");
		
		// create our view menu
		viewRefresh = new JMenuItem("Refresh");
		viewRefresh.addActionListener(this);
		JMenu viewMenu = new JMenu("View");
		viewMenu.add(viewRefresh);
		
		// assemble the menu bar
		JMenuBar menuBar = new JMenuBar();
		menuBar.add(fileMenu);
		menuBar.add( editMenu );
		menuBar.add( viewMenu );
		setJMenuBar( menuBar );	
		
		// file save functions don't work until we have a file
		fileSave.setEnabled(false);
		fileSaveAs.setEnabled(false);
		fileClose.setEnabled(false);
	}
	
	/**
	 * The action handler from hell ... it gets everything
	 */
	public void actionPerformed( ActionEvent e ) {
		Object o = e.getSource();
	
		if (o == fileOpen) {
			// close the existing file
			if (!closeFile())
				return;
			
			// get a new file name
			JFileChooser fc = new JFileChooser();
			if (fc.showOpenDialog(null) == JFileChooser.APPROVE_OPTION) {
				newFile( fc.getSelectedFile().getAbsolutePath() );
			}
			return;
		}
		
		if (o == fileSave && !opts.readOnly) {
			try {
				file.save();
			} catch (IOException err ) {
				JOptionPane.showMessageDialog( mainPane, 
						err.getMessage() 
						+ "\nFile: " + chosenFile,
						"ERROR UPDATING FILE", JOptionPane.ERROR_MESSAGE );
			}
			
			return;
		}
		
		if (o == fileSaveAs && !opts.readOnly) {
			JFileChooser fc = new JFileChooser(chosenFile);
			if (fc.showSaveDialog(null) == JFileChooser.APPROVE_OPTION) {
				String chosen = "";
				try {
					chosen = fc.getSelectedFile().getAbsolutePath();
					file.saveAs(chosen);
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
		
		if (o == viewRefresh) {
			// SOMEDAY what does view:refresh mean
			return;
		}	
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
