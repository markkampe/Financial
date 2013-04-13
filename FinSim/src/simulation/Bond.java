package simulation;

/**
 * a bond is an asset that makes (annual) interest payments and
 * then repays its principal value after a fixed period.
 * 
 * @author Mark
 */
public class Bond extends Asset {

	/**
	 * 
	 * 
	 * @param assetName	name of bond
	 * @param value		face value (final payment)
	 * @param intFunct	annual interest rate
	 * 					(null for a zero)
	 * @param purchYear	year of acquisition
	 * @param dueYear	year of repayment
	 */
	public Bond(String assetName, int value, int basis,
			Rate intFunct, int purchYear, int dueYear, Simulation sim) {
		super(assetName, null, intFunct, null, null, false, sim);
		
		// note the eventual repayment
		sell(dueYear, value, basis);
		
		// fill in the returns for the life of the bond
		for( int y = purchYear; y <= sim.lastYear; y++ ) {
			if (y <= dueYear) {
				double interest = (intFunct == null) ? 0 :
								value * intFunct.rateForYear(y);
				setValue(y, value, basis );	// FIX compute discounted value
				setReturns( y, (int) interest, 0, 0, 0);
			}
		}
	}
}
