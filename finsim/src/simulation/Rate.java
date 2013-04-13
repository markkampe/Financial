package simulation;

/**
 * a growth rate
 * <P>
 * Envisioned uses include income, expenses, and portfolio growth.
 * <P>
 * The rate function might be constant, shaped, or some interesting
 * randomized distribution.  That is all hidden under the covers.
 * All the client sees is a growth/shrinkage rate for a specified
 * year.
 * 
 * @author markk
 */
public class Rate {
	
	/**
	 * Return the growth rate for a specified year
	 * <P>
	 * NOTE: if the rate is the result of a simulated distribution
	 *       and it is called multiple times for the same year, it 
	 *       should always return the same value for the same year.
	 * <P>
	 * NOTE: if no rate function is provided (null) zero growth
	 * 	     should be assumed.
	 * 
	 * @param year	year for which a value is required
	 * 
	 * @return		growth rate for that year
	 * 				(typically a number between -0.20 and + 0.20)
	 */
	public double rateForYear( int year ) {
		return 0;
	}
	
	public double compounded( int startYear, int endYear ) {
		double factor = 1.0;
		
		for( int y = startYear; y <= endYear; y++ ) {
			factor *= 1 + rateForYear( y );
		}
		return factor;
	}
}
