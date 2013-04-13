package simulation;

/**
 * a shaping function to be applied to rates or amounts
 * <P>
 * Envisioned uses include:
 * <UL>
 * 		<LI> costs that are proportional to some external
 *  		 factor (like groceries)
 *  	<LI> income that only exists for certain years
 *  		 (like social security)
 * </UL>
 * <P>
 * Note: in the absence of a shaping function (null) a
 *       scaling factor of 1.0 should be assumed for every 
 *       year.
 * 
 * @author markk
 */
public interface Envelope {
	
	/**
	 * Return the scaling factor for a specified year
	 * 
	 * @param year	year for which a value is required
	 * 
	 * @return		scaling factor for that year
	 * 				(typically, but not necessarily 0-1)
	 */
	double scaleForYear( int year );
}
