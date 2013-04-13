package simulation;

/**
 * flat growth rate
 * 
 * @author markk
 */
public class SingleRate extends Rate {

	private double myRate;
	
	/**
	 * create a Rate function with the specified flat rate
	 * 
	 * @param rate	flat growth rate for this function
	 */
	SingleRate( double rate ) {
		myRate = rate;
	}
	
	public double rateForYear(int year) {
		return myRate;
	}

}
