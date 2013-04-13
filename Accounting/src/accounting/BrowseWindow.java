package accounting;
import java.awt.*;
import java.awt.event.*;
import javax.swing.*;
import java.awt.font.*;
import java.awt.geom.*;


public class BrowseWindow implements WindowListener {
	// private static final long serialVersionUID = 0xdeadbeef;
	
	private static final int X_OFFSET = 100;	// x position relative to parent
	private static final int Y_OFFSET = 100;	// y position relative to parent
	
	private static final int WIDTH  = 1000;		// maximum window width)
	private static final int HEIGHT = 400;		// maximum window height
	private static final double WIDTH_FUDGE = 1.1;	// I hate this, but lineMetrics lies
	private static final double HEIGHT_FUDGE = 1.3; // I hate this, but lineMetrics lies
	
	// font for rendering columnar numbers (less arbitrary than you might think)
	private final static String DISPLAY_FONT = "Monospaced";
	private final static int DISPLAY_SIZE = 12;
	
	// icon for financial detail windows
	private static final String ICON_IMAGE = "images/accounting-icon-16.png";
	
	// the window in which we are running
	private Frame thisWindow;
	
	/**
	 * create a window for viewing a ledger
	 * 
	 * @param String[] ... the text content of the ledger
	 */
	public BrowseWindow( String title, String text[] ) {
		thisWindow = new Frame( title );
		thisWindow.setLocation(X_OFFSET,Y_OFFSET);
		thisWindow.addWindowListener(this);
		
		// figure out our desired width and height
		int numRows = text.length;
		int numCols = 0;
		int maxRow = 0;
		for (int i = 0; i < numRows; i++ ) {
			if (text[i].length() > numCols) {
				maxRow = i;
				numCols = text[i].length();
			}
		}
		
		// get our window icon
		Image myIcon = thisWindow.getToolkit().getImage(getClass().getResource(ICON_IMAGE));
		thisWindow.setIconImage(myIcon);
		
		// populate this window with a scrollable frame of the dump
		JTextArea area = new JTextArea( numRows, numCols );
		for (int i = 0; i < numRows; i++ ) {
			area.append( text[i] + "\n" );
		}
		
		// set the font and make it scroll
		Font ourFont = new Font( DISPLAY_FONT, Font.PLAIN, DISPLAY_SIZE );
		area.setFont( ourFont );
		JScrollPane scroller = new JScrollPane( area );
	
		thisWindow.add( scroller, BorderLayout.CENTER );
		thisWindow.validate();
		
		// IRKSOME getStringBounds is underestimating required size
		// turn those into pixels
		Rectangle2D bounds = ourFont.getStringBounds(text[maxRow], new FontRenderContext(null, false, false ));
		double h = bounds.getHeight() * numRows * HEIGHT_FUDGE;
		int height = (int) h;
		if (height > HEIGHT)
			height = HEIGHT;
		double w = bounds.getWidth() * WIDTH_FUDGE;
		int width = (int) w;
		if (width > WIDTH)
			width = WIDTH;
		
		thisWindow.setSize(width, height );
		thisWindow.setVisible(true);
	}
	
	/**
	 * Window closing event handler ... shut down the window
	 */
	public void windowClosing(WindowEvent e) {
		thisWindow.setVisible( false );
		thisWindow.dispose();
	}
	
	// unloved window event handles
	public void windowActivated(WindowEvent arg0) {	}
	public void windowClosed(WindowEvent arg0) {	}
	public void windowDeactivated(WindowEvent arg0) {}
	public void windowDeiconified(WindowEvent arg0) {}
	public void windowIconified(WindowEvent arg0) {}
	public void windowOpened(WindowEvent arg0) {}
}
