package simulation;

/**
 * a bracket in a graduated tax table
 * 
 * @author Mark
 */
public class Bracket {
	public static final int UNLIMITED = -1;	// final bracket
	
	public int income;
	public double rate;
	
	/**
	 * define a tax bracket
	 * 
	 * @param topIncome		max income to which this bracket applies
	 * @param marginalRate	marginal rate for income in this bracket
	 */
	public Bracket( int topIncome, double marginalRate ) {
		income = topIncome;
		rate = marginalRate;
	}
}
